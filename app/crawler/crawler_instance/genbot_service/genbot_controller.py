# Local Imports
import asyncio
import copy
import threading
from time import sleep

from crawler.crawler_instance.genbot_service.parse_controller import parse_controller
from crawler.crawler_instance.local_shared_model.index_model import index_model
from crawler.crawler_instance.local_shared_model.url_model import url_model, url_model_init
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler
lock = threading.Lock()

class genbot_controller(request_handler):
    import os
    import sys

    hashseed = os.getenv('PYTHONHASHSEED')
    if not hashseed:
        os.environ['PYTHONHASHSEED'] = '0'
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def __init__(self):
        from crawler.crawler_instance.genbot_service.web_request_handler import webRequestManager
        from crawler.crawler_services.crawler_services.url_duplication_manager.html_duplication_controller import html_duplication_controller
        from crawler.crawler_services.helper_services.duplication_handler import duplication_handler

        self.__task_id = None
        self.__m_url_duplication_handler = duplication_handler()
        self.__m_web_request_handler = webRequestManager()
        self.__html_duplication_handler = html_duplication_controller()
        self.__m_html_parser = parse_controller()

        self.__m_tor_id = - 1
        self.__m_depth = 0
        self.__m_unparsed_url = []
        self.__m_parsed_url = []
        self.__m_proxy = {}

    def flush(self):
        self.__task_id = None
        self.__m_url_duplication_handler = None
        self.__m_web_request_handler = None
        self.__html_duplication_handler = None
        self.__m_html_parser = None

        del self.__task_id
        del self.__m_url_duplication_handler
        del self.__m_web_request_handler
        del self.__html_duplication_handler
        del self.__m_html_parser

        self.__m_tor_id = - 1
        self.__m_depth = 0
        self.__m_unparsed_url = []
        self.__m_parsed_url = []
        self.__m_proxy = {}

    def init(self, p_url):
        from crawler.crawler_instance.helper_services.helper_method import helper_method
        from crawler.crawler_services.crawler_services.mongo_manager.mongo_controller import mongo_controller
        from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGO_CRUD
        from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGODB_COMMANDS
        from crawler.crawler_services.crawler_services.url_duplication_manager.html_duplication_controller import html_duplication_controller
        from crawler.crawler_instance.tor_controller.tor_controller import tor_controller
        from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS

        self.__m_proxy, self.__m_tor_id = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_PROXY, [])

        m_requested_url = helper_method.on_clean_url(p_url)
        m_mongo_response = mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_READ, [MONGODB_COMMANDS.S_GET_INDEX, [m_requested_url], [None]])
        m_content_list = []

        self.__html_duplication_handler = None
        self.__html_duplication_handler = html_duplication_controller()

        for m_data in m_mongo_response:
            self.__m_parsed_url = m_data["sub_url_parsed"]
            m_content_list = m_data["content"]
            self.__m_html_parser.on_static_parser_init(m_data["document_url_parsed"], m_data["image_url_parsed"], m_data["video_url_parsed"])
            break

        for m_html in m_content_list:
            self.__html_duplication_handler.on_insert_content(m_html)

    def __check_content_duplication(self, p_parsed_model):
        from crawler.crawler_shared_directory.log_manager.log_controller import log
        from crawler.constants.strings import MANAGE_CRAWLER_MESSAGES
        m_score = self.__html_duplication_handler.verify_content_duplication(p_parsed_model.m_important_content_hidden)

        if m_score <= 0.80:
            self.__html_duplication_handler.on_insert_content(p_parsed_model.m_important_content_hidden)
            return False
        else:
            log.g().w(str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " + MANAGE_CRAWLER_MESSAGES.S_DUPLICATE_CONTENT + " : " + str(m_score))
            return True

    def __clean_sub_url(self, p_parsed_model:index_model):
        from crawler.crawler_instance.helper_services.helper_method import helper_method

        m_sub_url_filtered = []
        for m_sub_url in p_parsed_model.m_sub_url:
            if self.__m_url_duplication_handler.validate_duplicate(m_sub_url) is False:
                self.__m_url_duplication_handler.insert(m_sub_url)
                m_sub_url_filtered.append(helper_method.on_clean_url(m_sub_url))

        p_parsed_model.m_sub_url = m_sub_url_filtered[0:int(50/(1+(p_parsed_model.m_base_model.m_depth*4)))]

        return p_parsed_model

    # Web Request To Get Physical URL HTML
    def __trigger_url_request(self, p_request_model: url_model):
        try:
            from crawler.constants.strings import MANAGE_CRAWLER_MESSAGES
            from crawler.crawler_shared_directory.log_manager.log_controller import log
            from crawler.crawler_instance.helper_services.helper_method import helper_method
            #from crawler.crawler_services.crawler_services.elastic_manager.elastic_controller import elastic_controller
            #from crawler.crawler_services.crawler_services.elastic_manager.elastic_enums import ELASTIC_CRUD_COMMANDS, ELASTIC_REQUEST_COMMANDS
            import json

            # log.g().i(str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " + MANAGE_CRAWLER_MESSAGES.S_PARSING_STARTING + " : " + p_request_model.m_url)
            m_redirected_url, m_response, m_raw_html = asyncio.run(self.__m_web_request_handler.load_url(p_request_model.m_url, self.__m_proxy))

            if m_response is True:

                m_parsed_model, m_images = self.__m_html_parser.on_parse_html(m_raw_html, p_request_model)
                m_redirected_url = helper_method.on_clean_url(m_redirected_url)
                m_redirected_requested_url = helper_method.on_clean_url(p_request_model.m_url)

                m_parsed_model = self.__clean_sub_url(m_parsed_model)
                m_status = self.__check_content_duplication(m_parsed_model)
                if m_status:
                    return None, None, None

                if (m_redirected_url.replace("https", "http")) == m_redirected_requested_url.replace("https","http") or (m_redirected_url.replace("https", "http")) != m_redirected_requested_url.replace("https", "http") and self.__m_url_duplication_handler.validate_duplicate(m_redirected_url) is False:
                    self.__m_url_duplication_handler.insert(m_redirected_requested_url)


                    if m_parsed_model.m_validity_score >= 0 and (len(m_parsed_model.m_content) > 0) and m_response:

                        m_parsed_model, m_unique_file_model = self.__m_html_parser.on_parse_files(m_parsed_model, m_images)
                        m_final_doc = copy.deepcopy(m_parsed_model)
                        m_final_doc.m_sub_url = []
                        self.thread_safe_append(m_redirected_url)
                        # elastic_controller.get_instance().invoke_trigger(ELASTIC_CRUD_COMMANDS.S_INDEX, [ELASTIC_REQUEST_COMMANDS.S_INDEX, [json.dumps(m_final_doc.dict())], [True]])
                        log.g().s(str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " + MANAGE_CRAWLER_MESSAGES.S_LOCAL_URL_PARSED + " : " + m_redirected_requested_url)
                    else:
                        log.g().w(str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " + MANAGE_CRAWLER_MESSAGES.S_LOW_YIELD_URL + " : " + m_redirected_requested_url + " : " + str(m_parsed_model.m_validity_score))
                        return None, None, None

                    self.__m_parsed_url.append(m_redirected_requested_url)

                    return m_parsed_model, m_unique_file_model, m_raw_html
                else:
                    return None, None, None
            else:
                log.g().e(str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " + MANAGE_CRAWLER_MESSAGES.S_LOCAL_URL_PARSED_FAILED + " : " + p_request_model.m_url + " : " + str(m_raw_html))
                return None, None, None
        except Exception as ex:
            print(ex, flush=True)
            return None, None, None

    def thread_safe_append(self, p_url):
        file_path = './filtered_url.txt'
        with lock:
            with open(file_path, 'a') as file:
                file.write(p_url + '\n')

    # Wait For Crawl Manager To Provide URL From Queue
    def start_crawler_instance(self, p_request_url, p_task_id):
        from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
        from crawler.crawler_instance.helper_services.helper_method import helper_method
        from crawler.crawler_services.crawler_services.mongo_manager.mongo_controller import mongo_controller
        from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGO_CRUD, MONGODB_COMMANDS

        self.__task_id = "dirlink_" + str(p_task_id)
        self.init(p_request_url)
        m_host_crawled = False
        m_failure_count = 0

        self.__m_unparsed_url.append(url_model_init(p_request_url, CRAWL_SETTINGS_CONSTANTS.S_DEFAULT_DEPTH))
        while len(self.__m_unparsed_url) > 0:
            item = self.__m_unparsed_url.__getitem__(0)
            m_parsed_model, m_unique_file_model, m_raw_html = self.__trigger_url_request(item)

            if m_parsed_model is None:
                if not m_host_crawled:
                    if m_failure_count>3:
                        return
                    else:
                        m_failure_count += 1
                        sleep(5)
                        continue

            if m_parsed_model is not None and item.m_depth < CRAWL_SETTINGS_CONSTANTS.S_MAX_ALLOWED_DEPTH and len(self.__m_unparsed_url) < CRAWL_SETTINGS_CONSTANTS.S_MAX_HOST_QUEUE_SIZE:
                for sub_url in m_parsed_model.m_sub_url[0:int(CRAWL_SETTINGS_CONSTANTS.S_MAX_SUBHOST_QUEUE_SIZE / (item.m_depth + 1))]:
                    self.__m_unparsed_url.append(url_model_init(sub_url, item.m_depth + 1))

                m_unique_file_model.m_content.append(m_parsed_model.m_important_content_hidden)
                mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_UPDATE, [MONGODB_COMMANDS.S_UPDATE_INDEX, [helper_method.on_clean_url(helper_method.get_host_url(item.m_url)), self.__m_parsed_url, self.__m_unparsed_url, m_unique_file_model], [True]])
            m_host_crawled = True
            self.__m_unparsed_url.pop(0)

    def invoke_trigger(self, p_command, p_data=None):
        from crawler.crawler_instance.genbot_service.genbot_enums import ICRAWL_CONTROLLER_COMMANDS

        if p_command == ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE:
            self.start_crawler_instance(p_data[0], p_data[1])

def genbot_instance(p_url, p_vid):
    from crawler.crawler_instance.genbot_service.genbot_enums import ICRAWL_CONTROLLER_COMMANDS
    from crawler.crawler_instance.helper_services.helper_method import helper_method
    from crawler.crawler_services.crawler_services.mongo_manager.mongo_controller import mongo_controller
    from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGO_CRUD
    from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGODB_COMMANDS
    from crawler.constants import status
    import gc

    m_crawler = genbot_controller()
    try:
        m_crawler.invoke_trigger(ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE, [p_url, p_vid])
        m_crawler.flush()
        gc.collect()
        p_request_url = helper_method.on_clean_url(p_url)
        mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_UPDATE,[MONGODB_COMMANDS.S_CLOSE_INDEX_ON_COMPLETE, [p_request_url], [True]])
    except Exception as ex:
        print("Genbot Controller Error : " + str(p_url) + " : " + str(ex), flush=True)
        m_crawler.flush()
        gc.collect()
    finally:
        status.S_THREAD_COUNT -= 1
        m_crawler.flush()
        del m_crawler
        gc.enable()
        gc.unfreeze()
        gc.collect()
