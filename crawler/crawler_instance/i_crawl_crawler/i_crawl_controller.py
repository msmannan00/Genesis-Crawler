# Local Imports
import time

from thefuzz import fuzz
from crawler.crawler_instance.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.crawler_instance.constants.strings import MANAGE_CRAWLER_MESSAGES
from crawler.crawler_instance.crawl_controller.crawl_enums import CRAWLER_STATUS
from crawler.crawler_instance.i_crawl_crawler.i_crawl_enums import ICRAWL_CONTROLLER_COMMANDS, CRAWL_STATUS_TYPE
from crawler.crawler_services.crawler_services.elastic_manager.elastic_controller import elastic_controller
from crawler.crawler_services.crawler_services.elastic_manager.elastic_enums import ELASTIC_CRUD_COMMANDS, ELASTIC_REQUEST_COMMANDS
from crawler.crawler_services.crawler_services.url_duplication_manager.url_duplication_controller import \
    url_duplication_controller
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler
from crawler.crawler_services.helper_services.duplication_handler import duplication_handler
from crawler.crawler_services.helper_services.helper_method import helper_method
from crawler.crawler_instance.i_crawl_crawler.parse_controller import parse_controller
from crawler.crawler_instance.i_crawl_crawler.web_request_handler import webRequestManager


class i_crawl_controller(request_handler):

    def __init__(self):
        self.__m_duplication_handler = duplication_handler()
        self.__m_web_request_handler = webRequestManager()
        self.__m_content_duplication_handler = []
        self.__m_request_model = None

        self.__m_parsed_model = None
        self.__m_thread_status = CRAWLER_STATUS.S_RUNNING
        self.__m_save_to_mongodb = False
        self.__m_url_status = CRAWL_STATUS_TYPE.S_NONE

    def __clean_sub_url(self, p_parsed_model):
        m_sub_url_filtered = []
        for m_sub_url in  p_parsed_model.m_sub_url:
            if self.__m_duplication_handler.validate_duplicate(m_sub_url) is False:
                self.__m_duplication_handler.insert(m_sub_url)
                m_sub_url_filtered.append(m_sub_url)
        p_parsed_model.m_sub_url = m_sub_url_filtered


        return p_parsed_model

    def __validate_duplicate_content(self, p_content):
        for m_document in self.__m_content_duplication_handler:
            if fuzz.ratio(m_document,p_content)>CRAWL_SETTINGS_CONSTANTS.S_SUB_HOST_DATA_FUZZY_SCORE:
                return True

        return False

    def __validate_recrawl(self, p_index_model):
        return True

    # Web Request To Get Physical URL HTML
    def __trigger_url_request(self, p_request_model):
        __m_save_to_mongodb = False
        m_html_parser = parse_controller()

        m_redirected_url, m_response, m_html = self.__m_web_request_handler.load_url(p_request_model.m_url)
        if m_response is True:
            m_status, m_parsed_model = m_html_parser.on_parse_html(m_html, p_request_model)
            if m_status is False:
                return None

            m_redirected_url = helper_method.normalize_slashes(m_redirected_url)
            m_redirected_requested_url = helper_method.normalize_slashes(p_request_model.m_url)
            if m_redirected_url == m_redirected_requested_url or m_redirected_url != m_redirected_requested_url and self.__m_duplication_handler.validate_duplicate(m_redirected_url) is False:
                self.__m_duplication_handler.insert(m_redirected_url)

                m_status = self.__validate_duplicate_content(m_parsed_model.m_content)
                if m_status is True:
                    self.__m_save_to_mongodb = False
                    log.g().w(MANAGE_CRAWLER_MESSAGES.S_LOCAL_DUPLICATE_URL + " : " + p_request_model.m_url)
                elif m_status is False and m_parsed_model.m_validity_score >= 15 and (len(m_parsed_model.m_content) > 0) and m_response:
                    m_status = self.__validate_recrawl(m_parsed_model)
                    if m_status is None:
                        self.__m_save_to_mongodb = False
                        m_parsed_model.m_sub_url = []
                        return None

                    if m_status is True:
                        m_parsed_model = m_html_parser.on_parse_files(m_parsed_model)
                        self.__m_duplication_handler.insert(m_parsed_model.m_base_url_model.m_redirected_host)
                        self.__m_save_to_mongodb = True
                        self.__m_content_duplication_handler.append(m_parsed_model.m_content)
                        m_parsed_model.m_sub_url = []
                    else:
                        self.__m_save_to_mongodb = False
                        log.g().w(MANAGE_CRAWLER_MESSAGES.S_ALREADY_CRAWL_URL + " : " + p_request_model.m_url)
                else:
                    self.__m_save_to_mongodb = False
                    log.g().w(MANAGE_CRAWLER_MESSAGES.S_LOW_YIELD_URL + " : " + p_request_model.m_url)
                    self.__m_url_status = CRAWL_STATUS_TYPE.S_LOW_YIELD

            m_parsed_model = self.__clean_sub_url(m_parsed_model)

            return m_parsed_model

        self.__m_url_status = CRAWL_STATUS_TYPE.S_FETCH_ERROR
        return None

    # Wait For Crawl Manager To Provide URL From Queue
    def __start_crawler_instance(self, p_request_model):
        self.__invoke_thread(True, p_request_model)
        self.__m_content_duplication_handler.clear()
        while self.__m_thread_status in [CRAWLER_STATUS.S_RUNNING, CRAWLER_STATUS.S_PAUSE]:
            time.sleep(CRAWL_SETTINGS_CONSTANTS.S_ICRAWL_INVOKE_DELAY)
            #try:
            if self.__m_thread_status == CRAWLER_STATUS.S_RUNNING:
                    self.__m_parsed_model = self.__trigger_url_request(self.__m_request_model)
                    self.__m_thread_status = CRAWLER_STATUS.S_PAUSE
            #except Exception as ex:
            #    self.__m_thread_status = CRAWLER_STATUS.S_PAUSE
            #    print(ex.__traceback__)

    # Crawl Manager Makes Request To Get Crawl duplicationHandlerService
    def __get_crawled_data(self):
        return self.__m_parsed_model, self.__m_thread_status, self.__m_save_to_mongodb, self.__m_url_status, self.__m_request_model

    # Crawl Manager Awakes Crawler Instance From Sleep
    def __invoke_thread(self, p_status, p_request_model):
        if p_status is True:
            self.__m_request_model = p_request_model
            self.__m_thread_status = CRAWLER_STATUS.S_RUNNING
        else:
            self.__m_thread_status = CRAWLER_STATUS.S_STOP

    def invoke_trigger(self, p_command, p_data=None):
        if p_command == ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE:
            self.__start_crawler_instance(p_data[0])
        if p_command == ICRAWL_CONTROLLER_COMMANDS.S_GET_CRAWLED_DATA:
            return self.__get_crawled_data()
        if p_command == ICRAWL_CONTROLLER_COMMANDS.S_INVOKE_THREAD:
            return self.__invoke_thread(p_data[0], p_data[1])
