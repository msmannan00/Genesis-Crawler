# Local Imports
import asyncio
import copy
from gevent import sleep
from crawler.constants.app_status import APP_STATUS
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.constants.strings import PARSE_STRINGS, MANAGE_CRAWLER_MESSAGES
from crawler.crawler_instance.local_shared_model.image_model import image_model
from crawler.crawler_instance.genbot_service.web_request_handler import webRequestManager
from crawler.crawler_instance.local_shared_model.unique_file_model import unique_file_model
from crawler.crawler_services.helper_services.duplication_handler import duplication_handler
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.shared_data import celery_shared_data

if APP_STATUS.DOCKERIZED_RUN:
    from libs.nudenet.lite_classifier import LiteClassifier
    m_classifier = LiteClassifier()

class file_parse_manager:
    __m_duplication_url_handler = None
    __m_images = None

    def __init__(self):
        self.m_web_request_hander = webRequestManager()
        self.__m_duplication_url_handler = duplication_handler()
        self.__m_images = {}

    def init(self, p_documents, p_images, p_videos):
        for m_url in p_documents:
            self.__m_duplication_url_handler.insert(m_url)
        for m_url in p_videos:
            self.__m_duplication_url_handler.insert(m_url)
        for m_url in p_images:
            m_image_model = image_model(**m_url)
            self.__m_duplication_url_handler.insert(m_image_model.m_url)
            self.__m_images[m_image_model.m_url] = m_image_model.m_type

    def __is_static_url_valid(self, p_list, p_proxy_queue):

        m_filtered_list = []
        m_filtered_list_unique = []

        m_list_temp = copy.deepcopy(p_list)
        while len(m_list_temp) > 0:
            if celery_shared_data.get_instance().get_network_status():
                try:
                    m_url = m_list_temp.__getitem__(0)
                    if self.__m_duplication_url_handler.validate_duplicate(m_url) is False:
                        self.__m_duplication_url_handler.insert(m_url)

                        m_response, m_header = asyncio.run(self.m_web_request_hander.load_header(m_url))
                        if not m_response and not celery_shared_data.get_instance().get_network_status():
                            continue

                        if m_response is False:
                            continue
                        if m_response is True and (PARSE_STRINGS.S_CONTENT_LENGTH_HEADER not in m_header or int( m_header[PARSE_STRINGS.S_CONTENT_LENGTH_HEADER]) >= CRAWL_SETTINGS_CONSTANTS.S_MIN_CONTENT_LENGTH):
                            m_filtered_list.insert(0, m_url)
                            m_filtered_list_unique.insert(0, m_url)
                            log.g().s(MANAGE_CRAWLER_MESSAGES.S_FILE_PARSED + " : " + m_url)
                    else:
                        m_filtered_list.insert(0, m_url)

                    if len(m_filtered_list) > CRAWL_SETTINGS_CONSTANTS.S_STATIC_PARSER_LIST_MAX_SIZE:
                        break
                except Exception:
                    pass
            else:
                sleep(30)
                continue
            m_list_temp.pop(0)

        return m_filtered_list, m_filtered_list_unique

    def parse_static_files(self, p_images, p_documents, p_videos, p_proxy_queue):
        m_documents, m_documents_unique = self.__is_static_url_valid(p_documents, p_proxy_queue)
        m_videos, m_videos_unique = self.__is_static_url_valid(p_videos, p_proxy_queue)

        m_unique_file_model = unique_file_model(m_documents_unique, m_videos_unique, p_images)

        return p_images, m_documents, m_videos, m_unique_file_model
