# Local Imports
import copy
import json
import os
import random
import string
import time

from PIL import Image
from gevent import sleep
from crawler.constants.app_status import APP_STATUS
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS, RAW_PATH_CONSTANTS
from crawler.constants.strings import PARSE_STRINGS, MANAGE_CRAWLER_MESSAGES
from crawler.crawler_instance.helper_services.helper_method import helper_method
from crawler.crawler_instance.local_shared_model.image_model import image_model_init, image_model_list, image_model
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

        m_list_temp = copy.copy(p_list)
        while len(m_list_temp) > 0:
            if celery_shared_data.get_instance().get_network_status():
                try:
                    m_url = m_list_temp.__getitem__(0)
                    if self.__m_duplication_url_handler.validate_duplicate(m_url) is False:
                        self.__m_duplication_url_handler.insert(m_url)

                        m_response, m_header = self.m_web_request_hander.load_header(m_url, p_proxy_queue)
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

    def __is_image_favourable(self, p_list, p_proxy_queue):
        m_filtered_list = []
        m_filtered_list_unique = []
        m_porn_image_count = 0
        m_list_temp = copy.copy(p_list[0:10])

        while len(m_list_temp) > 0 and APP_STATUS.DOCKERIZED_RUN and len(m_filtered_list_unique)<2:
            try:
                if celery_shared_data.get_instance().get_network_status():
                    m_url = m_list_temp.__getitem__(0)

                    if self.__m_duplication_url_handler.validate_duplicate(m_url) is False:

                        time.sleep(CRAWL_SETTINGS_CONSTANTS.S_ICRAWL_IMAGE_INVOKE_DELAY)
                        if m_url.startswith("data") or m_url.endswith("gif"):
                            m_list_temp.pop(0)
                            continue

                        m_status, m_response = self.m_web_request_hander.download_image(m_url, p_proxy_queue)
                        if not m_status:
                            if celery_shared_data.get_instance().get_network_status():
                                m_list_temp.pop(0)
                            continue

                        self.__m_images[m_url] = 0

                        if m_status:
                            key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

                            m_content_type = m_response.headers['Content-Type'].split('/')[0]
                            m_file_type = m_response.headers['Content-Type'].split('/')[1]
                            m_url_path = key + "." + m_response.headers['Content-Type'].split('/')[1]

                            if len(m_file_type) > 4 or m_file_type == "gif" or m_content_type != "image" or len(
                                    m_response.content) < 15000 or " html" in str(m_response.content):
                                m_list_temp.pop(0)
                                continue

                            m_url_path = RAW_PATH_CONSTANTS.S_CRAWLER_IMAGE_CACHE_PATH + m_url_path
                            helper_method.write_content_to_path(m_url_path, m_response.content)
                            m_classifier_response = m_classifier.classify(m_url_path)

                            width, height = Image.open(m_url_path).size
                            if width < 250 and height < 250:
                                os.remove(m_url_path)
                                m_list_temp.pop(0)
                                continue

                            log.g().s(MANAGE_CRAWLER_MESSAGES.S_FILE_PARSED + " : " + m_url)
                            if m_classifier_response[m_url_path]['unsafe'] > 0.5:
                                m_porn_image_count += 1
                                self.__m_images[m_url] = 'a'
                                m_filtered_list.append(image_model_init(m_url, 'a'))
                                m_filtered_list_unique.append(json.loads(json.dumps(image_model_init(m_url, 'a').dict())))

                            else:
                                self.__m_images[m_url] = 'g'
                                m_filtered_list.append(image_model_init(m_url, 'g'))
                                m_filtered_list_unique.append(json.loads(json.dumps(image_model_init(m_url, 'g').dict())))

                            os.remove(m_url_path)
                            self.__m_duplication_url_handler.insert(m_url)

                    elif m_url in self.__m_images:
                        m_filtered_list.append(image_model_init(m_url, self.__m_images[m_url]))
                else:
                    sleep(30)
                    continue
                m_list_temp.pop(0)
            except Exception as ex:
                log.g().e(str(ex))
                m_list_temp.pop(0)

        return image_model_list(m_images=m_filtered_list), m_porn_image_count, m_filtered_list_unique


    def parse_static_files(self, p_images, p_documents, p_videos, p_content_type, p_proxy_queue):
        m_documents, m_documents_unique = self.__is_static_url_valid(p_documents, p_proxy_queue)
        m_videos, m_videos_unique = self.__is_static_url_valid(p_videos, p_proxy_queue)
        m_images, m_porn_image_count, m_image_unique = self.__is_image_favourable(p_images, p_proxy_queue)

        m_unique_file_model = unique_file_model(m_documents_unique, m_videos_unique, m_image_unique)

        if m_porn_image_count > 0:
            m_content_type = 'adult'
        else:
            m_content_type = p_content_type

        return m_images, m_documents, m_videos, m_content_type, m_unique_file_model
