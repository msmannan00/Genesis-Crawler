# Local Imports
import asyncio
import copy
import gc
import json

from crawler.constants import status
from crawler.crawler_instance.genbot_service.parse_controller import parse_controller
from crawler.crawler_instance.local_shared_model.url_model import url_model, url_model_init
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler
from crawler.crawler_instance.tor_controller.tor_controller import tor_controller
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS
from crawler.constants.strings import MANAGE_CRAWLER_MESSAGES
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_services.crawler_services.elastic_manager.elastic_controller import elastic_controller
from crawler.crawler_services.crawler_services.elastic_manager.elastic_enums import ELASTIC_CRUD_COMMANDS, ELASTIC_REQUEST_COMMANDS
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.crawler_instance.helper_services.helper_method import helper_method
from crawler.crawler_instance.genbot_service.web_request_handler import webRequestManager
from crawler.crawler_instance.genbot_service.genbot_enums import ICRAWL_CONTROLLER_COMMANDS


class genbot_hot_controller(request_handler):

    def __init__(self):

        self.__task_id = None
        self.__m_web_request_handler = webRequestManager()
        self.__m_html_parser = parse_controller()

        self.__m_tor_id = - 1
        self.__m_depth = 0
        self.__m_proxy = {}

    def init(self):
        self.__m_proxy, self.__m_tor_id = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_PROXY, [])

    def flush(self):
        self.__task_id = None
        self.__m_web_request_handler = None
        self.__m_html_parser = None

        del self.__task_id
        del self.__m_web_request_handler
        del self.__m_html_parser

        self.__m_tor_id = - 1
        self.__m_depth = 0
        self.__m_proxy = {}

    # Web Request To Get Physical URL HTML
    def __trigger_url_request(self, p_request_model: url_model):
        try:

            #log.g().i(str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " + MANAGE_CRAWLER_MESSAGES.S_PARSING_STARTING + " : " + p_request_model.m_url)
            m_redirected_url, m_response, m_raw_html = asyncio.run(self.__m_web_request_handler.load_url(p_request_model.m_url, self.__m_proxy))

            if m_response is True:
                m_parsed_model, m_images = self.__m_html_parser.on_parse_html(m_raw_html, p_request_model)
                m_redirected_url = helper_method.on_clean_url(m_redirected_url)
                m_redirected_requested_url = helper_method.on_clean_url(p_request_model.m_url)

                if (m_redirected_url.replace("https", "http")) == m_redirected_requested_url.replace("https","http") or (m_redirected_url.replace("https", "http")) != m_redirected_requested_url.replace("https", "http"):
                    m_final_doc = copy.deepcopy(m_parsed_model)
                    m_final_doc.m_sub_url = []
                    elastic_controller.get_instance().invoke_trigger(ELASTIC_CRUD_COMMANDS.S_INDEX, [ELASTIC_REQUEST_COMMANDS.S_INDEX, [json.dumps(m_final_doc.dict())], [True]])
                    log.g().s(str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " + MANAGE_CRAWLER_MESSAGES.S_LOCAL_URL_PARSED + " : " + m_redirected_requested_url)
                    return m_parsed_model
            else:
                log.g().e(str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " + MANAGE_CRAWLER_MESSAGES.S_LOCAL_URL_PARSED_FAILED + " : " + p_request_model.m_url + " : " + str(m_raw_html))

        except Exception as ex:
            print(ex, flush=True)

        return None

    # Wait For Crawl Manager To Provide URL From Queue
    def start_crawler_instance(self, p_request_url, p_task_id):

        self.__task_id = "hotlink_" + str(p_task_id)
        self.init()
        m_parsed_model = self.__trigger_url_request(url_model_init(p_request_url, CRAWL_SETTINGS_CONSTANTS.S_DEFAULT_DEPTH))

        if m_parsed_model is not None:
            m_parsed_model.m_sub_url = m_parsed_model.m_sub_url[0:50]
            for item in m_parsed_model.m_sub_url:
               m_parsed_model.m_sub_url.pop(0)
               self.__trigger_url_request(url_model_init(item, 1))

    def invoke_trigger(self, p_command, p_data=None):
        if p_command == ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE:
            self.start_crawler_instance(p_data[0], p_data[1])

def genbot_hot_instance(p_url, p_vid):
    m_crawler = genbot_hot_controller()
    try:
        m_crawler.invoke_trigger(ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE, [p_url, p_vid])
    except Exception as ex:
        log.g().e(ex)
    finally:
        status.S_HOTLINK_THREAD_COUNT -= 1
        m_crawler.flush()
        gc.enable()
        gc.unfreeze()
        gc.collect()
