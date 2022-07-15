# Local Imports
import os

from crawler.constants.app_status import APP_STATUS
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS, RAW_PATH_CONSTANTS
from crawler.constants.strings import MANAGE_CRAWLER_MESSAGES
from crawler.crawler_instance.crawl_controller.crawl_enums import CRAWL_MODEL_COMMANDS
from crawler.crawler_instance.genbot_service import genbot_controller
from crawler.crawler_instance.helper_services.helper_method import helper_method
from crawler.crawler_instance.tor_controller.tor_controller import tor_controller
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS
from crawler.crawler_services.crawler_services.mongo_manager.mongo_controller import mongo_controller
from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGODB_COMMANDS, MONGO_CRUD
from crawler.crawler_services.helper_services.scheduler import RepeatedTimer
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler


class crawl_model(request_handler):

    def __init__(self):
        self.__init_image_cache()

    # Insert To Database - Insert URL to database after parsing them
    def __init_image_cache(self):
        if not os.path.isdir(RAW_PATH_CONSTANTS.S_CRAWLER_IMAGE_CACHE_PATH):
            os.makedirs(RAW_PATH_CONSTANTS.S_CRAWLER_IMAGE_CACHE_PATH)
        else:
            helper_method.clear_folder(RAW_PATH_CONSTANTS.S_CRAWLER_IMAGE_CACHE_PATH)

    # Start Crawler Manager
    def __install_live_url(self):
        mongo_response = mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_READ, [MONGODB_COMMANDS.S_GET_CRAWLABLE_URL_DATA, [None], [None]])
        m_live_url_list = set().union([x['m_url'] for x in mongo_response])

        m_request_handler, proxies, headers = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_CREATE_SESSION, [True])
        m_response = m_request_handler.get(CRAWL_SETTINGS_CONSTANTS.S_START_URL, headers=headers, timeout=CRAWL_SETTINGS_CONSTANTS.S_URL_TIMEOUT, proxies=proxies, allow_redirects=True)

        m_updated_url_list = []
        for m_server_url in m_response.text.splitlines():
            m_url = helper_method.on_clean_url(m_server_url)
            if helper_method.is_uri_validator(m_server_url) and m_url not in m_live_url_list:
                log.g().s(MANAGE_CRAWLER_MESSAGES.S_INSTALLED_URL + " : " + m_url)
                mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_UPDATE, [MONGODB_COMMANDS.S_INSTALL_CRAWLABLE_URL, [m_url], [True]])
                m_updated_url_list.append(m_url)

        mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_DELETE, [MONGODB_COMMANDS.S_REMOVE_DEAD_CRAWLABLE_URL, [list(m_live_url_list)], [None]])
        return m_live_url_list, m_updated_url_list

    def __init_docker_request(self):
        m_live_url_list, m_updated_url_list = self.__install_live_url()
        self.__start_docker_request(list(m_live_url_list) + m_updated_url_list)

    def __reinit_docker_request(self):
        m_live_url_list, m_updated_url_list = self.__install_live_url()
        self.__start_docker_request(m_updated_url_list)

    def __start_docker_request(self, p_fetched_url_list):
        log.g().i(MANAGE_CRAWLER_MESSAGES.S_REINITIALIZING_CRAWLABLE_URL)

        for m_url_node in p_fetched_url_list:
            if APP_STATUS.DOCKERIZED_RUN:
                genbot_controller.celery_genbot_instance.apply_async(
                    args=[m_url_node],
                    kwargs={},
                    queue='genbot_queue', retry=False)

    def __start_direct_request(self):
        log.g().i(MANAGE_CRAWLER_MESSAGES.S_REINITIALIZING_CRAWLABLE_URL)

        while True:
            m_live_url_list, p_fetched_url_list = self.__install_live_url()
            m_request_list = list(m_live_url_list) + p_fetched_url_list
            for m_url_node in m_request_list:
                genbot_controller.celery_genbot_instance(m_url_node)

    def __init_crawler(self):
        if APP_STATUS.DOCKERIZED_RUN:
            self.__init_docker_request()
            RepeatedTimer(CRAWL_SETTINGS_CONSTANTS.S_CELERY_RESTART_DELAY, self.__reinit_docker_request, trigger_on_start=False)
        else:
            self.__start_direct_request()

    def invoke_trigger(self, p_command, p_data=None):
        if p_command == CRAWL_MODEL_COMMANDS.S_INIT:
            self.__init_crawler()
