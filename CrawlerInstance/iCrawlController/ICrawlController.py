# Local Imports
import time

from CrawlerInstance.constants import constants
from CrawlerInstance.constants.enums import ICRAWL_CONTROLLER_COMMANDS
from CrawlerInstance.sharedModel.requestHandler import requestHandler
from GenesisCrawlerServices.constants.enums import CRAWLER_STATUS, MONGODB_COMMANDS
from GenesisCrawlerServices.helperServices.duplicationHandler import DuplicationHandler
from GenesisCrawlerServices.helperServices.helperMethod import helper_method
from CrawlerInstance.iCrawlController.parseManager import parseManager
from CrawlerInstance.classModels.indexModel import indexModel
from CrawlerInstance.iCrawlController.webRequestManager import webRequestManager
from GenesisCrawlerServices.crawlerServices.mongoDB.mongoController import mongo_controller


class iCrawlController(requestHandler):

    __m_web_request_handler = None
    __m_duplication_handler = None
    __m_request_model = None

    __m_parsed_model = indexModel()
    __m_thread_status = CRAWLER_STATUS.S_RUNNING

    def __init__(self):
        self.__m_duplication_handler = DuplicationHandler()
        self.__m_web_request_handler = webRequestManager()

    # Set Thread Info Of Crawler
    def __filter_sub_url_size(self, p_parsed_model):
        m_subhost_filtered = []
        m_host = helper_method.get_host_url(p_parsed_model.m_base_url_model.m_redirected_host)
        m_filter_counter = 0

        for m_url in p_parsed_model.m_base_url_model.m_redirected_host:
            if m_host != helper_method.get_host_url(m_url):
                m_subhost_filtered.append(m_url)
            elif m_filter_counter < constants.S_MAX_SUBHOST_QUEUE_SIZE:
                m_subhost_filtered.append(m_url)
                m_filter_counter +=1

        p_parsed_model.m_base_url_model.m_redirected_host = m_subhost_filtered
        return p_parsed_model

    def __clean_sub_url(self, p_parsed_model):
        m_sub_url_filtered = []
        for m_sub_url in  p_parsed_model.m_sub_url:
            if self.__m_duplication_handler.validate_duplicate_url(m_sub_url) is False:
                self.__m_duplication_handler.insert_url(m_sub_url)
                m_sub_url_filtered.append(m_sub_url)
        p_parsed_model.m_sub_url = m_sub_url_filtered
        return p_parsed_model

    # Web Request To Get Physical URL HTML
    def __trigger_url_request(self, p_request_model):
        m_html_parser = parseManager()
        m_redirected_url, response, html = self.__m_web_request_handler.load_url(p_request_model.getURL())

        p_request_model.setRedirectedURL(m_redirected_url)
        m_parsed_model = m_html_parser.on_parse_html(html, p_request_model, response)
        m_parsed_model = self.__filter_sub_url_size(m_parsed_model)



        m_parsed_model.m_content_type = p_request_model.m_type



        p_request_model.setRedirectedURL(helper_method.on_clean_url(helper_method.normalize_slashes(m_redirected_url + "////")))

        if len(m_parsed_model.m_sub_url)>5 and response and self.__m_duplication_handler.validate_duplicate_url(m_parsed_model.m_base_url_model.m_redirected_host) is False:
            self.__m_duplication_handler.insert_url(m_parsed_model.m_base_url_model.m_redirected_host)
            mongo_controller.get_instance().invoke_trigger(MONGODB_COMMANDS.S_SAVE_PARSE_URL, m_parsed_model)

        m_parsed_model = self.__clean_sub_url(m_parsed_model)

        return m_parsed_model

    # Wait For Crawl Manager To Provide URL From Queue
    def __start_crawler_instance(self, p_request_model):
        self.__invoke_thread(True, p_request_model)
        self.__m_parsed_model.setBaseURL(self.__m_request_model)
        while self.__m_thread_status in [CRAWLER_STATUS.S_RUNNING, CRAWLER_STATUS.S_PAUSE]:
            if self.__m_thread_status == CRAWLER_STATUS.S_RUNNING:
                self.__m_parsed_model = self.__trigger_url_request(self.__m_request_model)
                self.__m_thread_status = CRAWLER_STATUS.S_PAUSE
            time.sleep(2)

    # Crawl Manager Makes Request To Get Crawl duplicationHandlerService
    def __get_crawled_data(self):
        return self.__m_parsed_model, self.__m_thread_status

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
