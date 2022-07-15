# Local Imports
import json

from crawler.celery_manager import celery_genbot
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.constants.strings import MANAGE_CRAWLER_MESSAGES
from crawler.crawler_instance.genbot_service.genbot_enums import ICRAWL_CONTROLLER_COMMANDS
from crawler.crawler_instance.local_shared_model.url_model import url_model, url_model_init
from crawler.crawler_services.crawler_services.elastic_manager.elastic_controller import elastic_controller
from crawler.crawler_services.crawler_services.elastic_manager.elastic_enums import ELASTIC_CRUD_COMMANDS, ELASTIC_REQUEST_COMMANDS
from crawler.crawler_services.crawler_services.mongo_manager.mongo_controller import mongo_controller
from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGO_CRUD, MONGODB_COMMANDS
from crawler.crawler_services.helper_services.duplication_handler import duplication_handler
from crawler.crawler_services.helper_services.helper_method import helper_method
from crawler.crawler_instance.genbot_service.parse_controller import parse_controller
from crawler.crawler_instance.genbot_service.web_request_handler import webRequestManager
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler
from gevent import sleep
from crawler.shared_data import celery_shared_data
from crawler.crawler_instance.local_shared_model.unique_file_model import unique_file_model


class genbot_controller(request_handler):

    def __init__(self):
        self.__m_url_duplication_handler = duplication_handler()
        self.__m_web_request_handler = webRequestManager()
        self.__depth = 0
        self.__m_unparsed_url = []
        self.__m_parsed_url = []

        self.__m_html_parser = parse_controller()

    def init(self, p_url):
        m_requested_url = helper_method.on_clean_url(p_url)
        m_mongo_response = mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_READ, [MONGODB_COMMANDS.S_GET_INDEX, [m_requested_url], [None]])
        m_unparsed_url = []

        for m_data in m_mongo_response:
            self.__m_parsed_url = m_data["sub_url_parsed"]
            m_unparsed_url = m_data["sub_url_pending"]
            self.__m_html_parser.on_static_parser_init(m_data["document_url_parsed"], m_data["image_url_parsed"], m_data["video_url_parsed"])
            break

        for m_parsed_url in self.__m_parsed_url:
            self.__m_url_duplication_handler.insert(m_parsed_url)

        for m_url in m_unparsed_url:
            self.__m_unparsed_url.append(url_model(**m_url))
        pass

    def __clean_sub_url(self, p_parsed_model):
        m_sub_url_filtered = []
        for m_sub_url in p_parsed_model.m_sub_url:
            if self.__m_url_duplication_handler.validate_duplicate(m_sub_url) is False:
                self.__m_url_duplication_handler.insert(m_sub_url)
                m_sub_url_filtered.append(helper_method.on_clean_url(m_sub_url))
        p_parsed_model.m_sub_url = m_sub_url_filtered

        return p_parsed_model

    # Web Request To Get Physical URL HTML
    def __trigger_url_request(self, p_request_model: url_model):
        log.g().i(MANAGE_CRAWLER_MESSAGES.S_PARSING_STARTING + " : " + p_request_model.m_url)
        m_redirected_url, m_response, m_content = self.__m_web_request_handler.load_url(p_request_model.m_url)
        m_unique_file_model = unique_file_model([], [], [])

        if m_response is True:

            m_parsed_model, m_images = self.__m_html_parser.on_parse_html(m_content, p_request_model)
            m_redirected_url = helper_method.on_clean_url(m_redirected_url)
            m_redirected_requested_url = helper_method.on_clean_url(p_request_model.m_url)

            if m_redirected_url == m_redirected_requested_url or m_redirected_url != m_redirected_requested_url and self.__m_url_duplication_handler.validate_duplicate(m_redirected_url) is False:
                self.__m_url_duplication_handler.insert(m_redirected_requested_url)

                if m_parsed_model.m_validity_score >= 15 and (len(m_parsed_model.m_content) > 0) and m_response:
                    log.g().s(MANAGE_CRAWLER_MESSAGES.S_LOCAL_URL_PARSED + " : " + m_redirected_requested_url)
                    m_parsed_model, m_unique_file_model = self.__m_html_parser.on_parse_files(m_parsed_model, m_images)
                    elastic_controller.get_instance().invoke_trigger(ELASTIC_CRUD_COMMANDS.S_INDEX, [ELASTIC_REQUEST_COMMANDS.S_INDEX, [json.dumps(m_parsed_model.dict())], [True]])
                else:
                    log.g().w(MANAGE_CRAWLER_MESSAGES.S_LOW_YIELD_URL + " : " + m_redirected_requested_url)

            m_parsed_model = self.__clean_sub_url(m_parsed_model)
            self.__m_parsed_url.append(m_redirected_requested_url)


            return m_parsed_model, m_unique_file_model
        else:
            log.g().w(MANAGE_CRAWLER_MESSAGES.S_LOCAL_URL_PARSED_FAILED + " : " + p_request_model.m_url + " : " + str(m_content))
            return None, None

    # Wait For Crawl Manager To Provide URL From Queue
    def start_crawler_instance(self, p_request_url):
        self.init(p_request_url)

        self.__m_unparsed_url.append(url_model_init(p_request_url, CRAWL_SETTINGS_CONSTANTS.S_DEFAULT_DEPTH))
        while len(self.__m_unparsed_url) > 0:
            if celery_shared_data.get_instance().get_network_status():
                item = self.__m_unparsed_url.pop(0)
                m_parsed_model, m_unique_file_model = self.__trigger_url_request(item)
                if m_parsed_model is None and not celery_shared_data.get_instance().get_network_status():
                    sleep(30)
                    continue

                if m_parsed_model:
                    if item.m_depth < CRAWL_SETTINGS_CONSTANTS.S_MAX_ALLOWED_DEPTH and len(self.__m_unparsed_url) < CRAWL_SETTINGS_CONSTANTS.S_MAX_HOST_QUEUE_SIZE:
                        for sub_url in m_parsed_model.m_sub_url[0:int(CRAWL_SETTINGS_CONSTANTS.S_MAX_SUBHOST_QUEUE_SIZE / (item.m_depth + 1))]:
                            self.__m_unparsed_url.append(url_model_init(sub_url, item.m_depth + 1))

                    mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_UPDATE, [MONGODB_COMMANDS.S_UPDATE_INDEX, [helper_method.on_clean_url(helper_method.get_host_url(item.m_url)), self.__m_parsed_url, self.__m_unparsed_url, m_unique_file_model], [True]])
            else:
                sleep(30)

        p_request_url = helper_method.on_clean_url(p_request_url)
        mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_UPDATE, [MONGODB_COMMANDS.S_CLOSE_INDEX_ON_COMPLETE, [p_request_url], [True]])

    def invoke_trigger(self, p_command, p_data=None):
        if p_command == ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE:
            self.start_crawler_instance(p_data[0])


@celery_genbot.task(name='celery_genbot_instance.task', bind=False, queue='genbot_queue')
def celery_genbot_instance(p_url):
    m_crawler = genbot_controller()
    m_crawler.invoke_trigger(ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE, [p_url])
