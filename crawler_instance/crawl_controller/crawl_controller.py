# Local Imports
import threading
from time import sleep

from raven.transport import requests
from crawler_instance.constants import app_status
from crawler_instance.constants.constant import CRAWL_SETTINGS_CONSTANTS, RAW_PATH_CONSTANTS
from crawler_instance.constants.strings import MESSAGE_STRINGS
from crawler_instance.crawl_controller.crawl_enums import CRAWLER_STATUS, CRAWL_MODEL_COMMANDS, CRAWL_CONTROLLER_COMMANDS, NETWORK_STATUS
from crawler_instance.helper_services.helper_method import helper_method
from crawler_instance.i_crawl_crawler.i_crawl_enums import ICRAWL_CONTROLLER_COMMANDS
from crawler_instance.local_shared_model.url_model import url_model
from crawler_services.helper_services.internet_monitor import network_monitor
from crawler_shared_directory.log_manager.log_controller import log
from crawler_shared_directory.request_manager.request_handler import request_handler
from crawler_instance.crawl_controller.crawl_model import crawl_model
from crawler_instance.i_crawl_crawler.i_crawl_controller import i_crawl_controller
from crawler_instance.tor_controller import tor_enums
from crawler_services.crawler_services.mongo_manager.mongo_controller import mongo_controller
from crawler_services.crawler_services.mongo_manager.mongo_enums import MONGODB_COMMANDS, MONGO_CRUD


class crawl_controller(request_handler):

    # Local Variables
    __m_crawl_model = None

    # Crawler Instances & Threads
    __m_main_thread = None
    __m_crawler_instance_list = []

    # Initializations
    def __init__(self):
        self.__m_crawl_model = crawl_model()

    # Start Crawler Manager

    def __install_live_url(self):
        try:
            mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_UPDATE, [MONGODB_COMMANDS.S_RESET_CRAWLABLE_URL, [None], [None]])
            m_response = requests.get(CRAWL_SETTINGS_CONSTANTS.S_START_URL)

            for line in m_response.text.splitlines():
                log.g().s(MESSAGE_STRINGS.S_INSTALLED_URL + " : " + line)
                mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_UPDATE,[MONGODB_COMMANDS.S_INSTALL_CRAWLABLE_URL, [line], [None]])
        except Exception:
            pass

    def __init_live_url(self):
        log.g().i(MESSAGE_STRINGS.S_REINITIALIZING_CRAWLABLE_URL)

        m_url_list = []
        m_response = mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_READ,[MONGODB_COMMANDS.S_GET_CRAWLABLE_URL_DATA,[None], [None]])
        for m_document in m_response:
            m_url_list.append(m_document)

        for m_document in m_url_list:
            self.__m_crawl_model.invoke_trigger(CRAWL_MODEL_COMMANDS.S_INSERT_INIT, [m_document['m_url'], url_model(CRAWL_SETTINGS_CONSTANTS.S_START_URL, 0, CRAWL_SETTINGS_CONSTANTS.S_THREAD_CATEGORY_GENERAL)])

    def __on_run_general(self):
        # self.__install_live_url()
        # self.__init_live_url()

        helper_method.clear_folder(RAW_PATH_CONSTANTS.S_CRAWLER_IMAGE_CACHE_PATH)
        self.__m_main_thread = threading.Thread(target=self.__init_thread_manager)
        self.__m_main_thread.start()

    # ICrawler Manager
    def __init_thread_manager(self):
        while True:

            if network_monitor.get_instance().get_network_status() == NETWORK_STATUS.S_ONLINE:
                self.__crawler_instance_manager()
            else:
                log.g().e(MESSAGE_STRINGS.S_INTERNET_ERROR)
                sleep(5)
                continue

            if app_status.TOR_STATUS.S_TOR_STATUS != tor_enums.TOR_STATUS.S_RUNNING:
                threading.Event().wait(CRAWL_SETTINGS_CONSTANTS.S_CRAWLER_INVOKE_DELAY)
                continue

            while len(self.__m_crawler_instance_list) < CRAWL_SETTINGS_CONSTANTS.S_MAX_THREAD_COUNT_PER_INSTANCE:

                m_status, m_url_model = self.__m_crawl_model.invoke_trigger(CRAWL_MODEL_COMMANDS.S_GET_HOST_URL)
                if m_status is False:
                    break
                else:
                    m_icrawler_instance = i_crawl_controller()
                    self.__m_crawler_instance_list.insert(0, m_icrawler_instance)
                    thread_instance = threading.Thread(target=self.__create_crawler_instance, args=(m_url_model,m_icrawler_instance,))
                    thread_instance.start()

            threading.Event().wait(CRAWL_SETTINGS_CONSTANTS.S_CRAWLER_INVOKE_DELAY)
            if app_status.CRAWL_STATUS.S_QUEUE_BACKUP_STATUS is False and len(self.__m_crawler_instance_list)<=0:
                mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_DELETE, [MONGODB_COMMANDS.S_CLEAR_BACKUP, [None],[None]])
                mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_DELETE, [MONGODB_COMMANDS.S_CLEAR_UNIQUE_HOST, [None], [None]])
                app_status.CRAWL_STATUS.S_QUEUE_BACKUP_STATUS = True
                self.__m_crawl_model.invoke_trigger(CRAWL_MODEL_COMMANDS.S_CRAWL_FINISHED_STATUS)
                self.__m_crawl_model = crawl_model()
                self.__init_live_url()

    # Awake Crawler From Sleep
    def __crawler_instance_manager(self):
        for m_crawl_instance in self.__m_crawler_instance_list:
            m_index_model, m_thread_status, m_save_to_mongodb, m_url_status, m_request_model = m_crawl_instance.invoke_trigger(ICRAWL_CONTROLLER_COMMANDS.S_GET_CRAWLED_DATA)
            if m_thread_status == CRAWLER_STATUS.S_STOP:
                self.__m_crawler_instance_list.remove(m_crawl_instance)
            elif m_thread_status == CRAWLER_STATUS.S_PAUSE:
                m_status, m_url_model = self.__crawler_instance_job_fetcher(m_index_model, m_save_to_mongodb, m_request_model)
                mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_UPDATE, [MONGODB_COMMANDS.S_UPDATE_CRAWLABLE_URL_DATA, [m_request_model.m_url, m_url_status], [None]])
                m_crawl_instance.invoke_trigger(ICRAWL_CONTROLLER_COMMANDS.S_INVOKE_THREAD,[m_status, m_url_model])

    def __create_crawler_instance(self, p_url_model, p_crawler_instance):

        # Creating Thread Instace
        m_crawler_instance = p_crawler_instance

        # Saving Thread Instace
        log.g().i("THREAD CREATED : " + str(len(self.__m_crawler_instance_list)))

        # Start Thread Instace
        m_crawler_instance.invoke_trigger(ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE, [p_url_model])

    # Try To Get Job For Crawler Instance
    def __crawler_instance_job_fetcher(self, p_index_model, p_save_to_mongodb, p_request_model):
        if p_save_to_mongodb is True and p_index_model is not None:
            self.__m_crawl_model.invoke_trigger(CRAWL_MODEL_COMMANDS.S_INSERT_URL, [p_index_model, p_save_to_mongodb])

        m_status, m_url_model = self.__m_crawl_model.invoke_trigger(CRAWL_MODEL_COMMANDS.S_GET_SUB_URL, [p_request_model.m_url])
        if m_status:
            return m_status, m_url_model
        else:
            return False, None

    def invoke_trigger(self, p_command, p_data=None):
        if p_command == CRAWL_CONTROLLER_COMMANDS.S_RUN_GENERAL_CRAWLER:
            self.__on_run_general()
