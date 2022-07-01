# Local Imports
import os

from raven.transport import requests

from crawler.constants.app_status import APP_STATUS
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS, RAW_PATH_CONSTANTS
from crawler.constants.strings import MANAGE_CRAWLER_MESSAGES
from crawler.crawler_instance.crawl_controller.crawl_enums import CRAWL_MODEL_COMMANDS
from crawler.crawler_instance.genbot_service import genbot_controller
from crawler.crawler_instance.helper_services.helper_method import helper_method
from crawler.crawler_services.crawler_services.mongo_manager.mongo_controller import mongo_controller
from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGODB_COMMANDS, MONGO_CRUD
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler


class crawl_model(request_handler):

    # Insert To Database - Insert URL to database after parsing them
    def __init_image_cache(self):
        if not os.path.isdir(RAW_PATH_CONSTANTS.S_CRAWLER_IMAGE_CACHE_PATH):
            os.makedirs(RAW_PATH_CONSTANTS.S_CRAWLER_IMAGE_CACHE_PATH)
        else:
            helper_method.clear_folder(RAW_PATH_CONSTANTS.S_CRAWLER_IMAGE_CACHE_PATH)

    # Start Crawler Manager
    def __install_live_url(self):
        try:
            mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_UPDATE, [MONGODB_COMMANDS.S_RESET_CRAWLABLE_URL, [None], [False]])
            m_response = requests.get(CRAWL_SETTINGS_CONSTANTS.S_START_URL)
            m_server_url_list = []

            for m_server_url in m_response.text.splitlines():
                if helper_method.is_uri_validator(m_server_url):
                    log.g().s(MANAGE_CRAWLER_MESSAGES.S_INSTALLED_URL + " : " + m_server_url)
                    m_server_url = helper_method.on_clean_url(m_server_url)
                    mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_UPDATE, [MONGODB_COMMANDS.S_INSTALL_CRAWLABLE_URL, [helper_method.on_clean_url(m_server_url)], [True]])
                    m_server_url_list.append(m_server_url)
            mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_DELETE, [MONGODB_COMMANDS.S_REMOVE_DEAD_CRAWLABLE_URL, [], [None]])
            return m_server_url_list
        except Exception as ex:
            log.g().c(MANAGE_CRAWLER_MESSAGES.S_UNIQUE_URL_CACHE_LOAD_FAILURE + " : " + str(ex))
            exit(0)

    def __wait_tasks(self, m_job_list):
        for m_job in m_job_list:
            m_job.wait()

    def __start_crawler_services(self, p_fetched_url_list):
        log.g().i(MANAGE_CRAWLER_MESSAGES.S_REINITIALIZING_CRAWLABLE_URL)

        m_job_list = []
        for m_url_node in p_fetched_url_list:
            if APP_STATUS.DOCKERIZED_RUN:
                m_job_list.append(genbot_controller.celery_genbot_instance.apply_async(
                    args=[m_url_node],
                    kwargs={},
                    queue='genbot_queue'))
            else:
                genbot_controller.celery_genbot_instance(m_url_node)
        self.__wait_tasks(m_job_list)

    def __init_reset(self):
        self.__init_image_cache()
        return self.__install_live_url()


    def __init_crawler(self):
        mongo_response = mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_READ, [MONGODB_COMMANDS.S_GET_CRAWLABLE_URL_DATA, [None], [None]])
        mongo_response = list(mongo_response)
        p_fetched_url_list = []

        if len(mongo_response) == 0:
            p_fetched_url_list = self.__install_live_url()
        else:
            for item in mongo_response:
                p_fetched_url_list.append(item["m_url"])

        while True:
            self.__start_crawler_services(p_fetched_url_list)
            p_fetched_url_list = self.__init_reset()

    def invoke_trigger(self, p_command, p_data=None):
        if p_command == CRAWL_MODEL_COMMANDS.S_INIT:
            self.__init_crawler()
