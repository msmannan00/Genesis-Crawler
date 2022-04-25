# Local Imports
import os
import random
import string
import time

from PIL import Image
from nudenet import NudeClassifierLite
from crawler.crawler_instance.helper_services.helper_method import helper_method
from crawler.crawler_instance.i_crawl_crawler.static_parse_manager.image_model import image_model
from crawler.crawler_instance.constants.constant import CRAWL_SETTINGS_CONSTANTS, RAW_PATH_CONSTANTS
from crawler.crawler_instance.constants.strings import PARSE_STRINGS, MANAGE_CRAWLER_MESSAGES, STRINGS
from crawler.crawler_instance.i_crawl_crawler.web_request_handler import webRequestManager
from crawler.crawler_services.helper_services.duplication_handler import duplication_handler
from crawler.crawler_shared_directory.log_manager.log_controller import log


class file_parse_manager:
    __m_duplication_url_handler = None
    __m_images = None

    def __init__(self):
        self.m_web_request_hander = webRequestManager()
        self.__m_duplication_url_handler = duplication_handler()
        self.__m_images = {}

    def __is_static_url_valid(self, p_list):

        m_filtered_list = []

        for m_url in p_list:
            if self.__m_duplication_url_handler.validate_duplicate(m_url) is False:
                self.__m_duplication_url_handler.insert(m_url)

                m_response, m_header = self.m_web_request_hander.load_header(m_url)
                if m_response is False:
                    continue
                if m_response is True and (PARSE_STRINGS.S_CONTENT_LENGTH_HEADER not in m_header or int(m_header[PARSE_STRINGS.S_CONTENT_LENGTH_HEADER]) >= CRAWL_SETTINGS_CONSTANTS.S_MIN_CONTENT_LENGTH):
                   m_filtered_list.insert(0, m_url)
                   log.g().s(MANAGE_CRAWLER_MESSAGES.S_FILE_PARSED + " : " + m_url)
            if len(m_filtered_list)>CRAWL_SETTINGS_CONSTANTS.S_STATIC_PARSER_LIST_MAX_SIZE:
                break

        return m_filtered_list

    def __is_image_favourable(self, p_list, p_url):

        m_filtered_list = []
        m_porn_image_count = 0
        for m_url in p_list:
            try:
                if len(m_filtered_list) > 5 or m_porn_image_count > 5:
                    break

                if self.__m_duplication_url_handler.validate_duplicate(m_url) is False:

                    time.sleep(CRAWL_SETTINGS_CONSTANTS.S_ICRAWL_IMAGE_INVOKE_DELAY)
                    if m_url.startswith("data") or m_url.endswith("gif"):
                        continue
                    m_status, m_response = self.m_web_request_hander.download_image(m_url)
                    self.__m_images[m_url] = 0

                    if m_status:
                        key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

                        m_content_type = m_response.headers['Content-Type'].split('/')[0]
                        m_file_type = m_response.headers['Content-Type'].split('/')[1]
                        m_url_path = key + "." + m_response.headers['Content-Type'].split('/')[1]

                        if len(m_file_type) >3 or m_file_type=="gif" or m_content_type != "image" or len(m_response.content) < 15000 or " html" in str(m_response.content):
                            continue

                        helper_method.write_content_to_path(RAW_PATH_CONSTANTS.S_CRAWLER_IMAGE_CACHE_PATH + m_url_path, m_response.content)
                        m_classifier = NudeClassifierLite()
                        m_classifier_response = m_classifier.classify(m_url_path)

                        width, height = Image.open(m_url_path).size
                        if width < 250 and height < 250:
                            os.remove(m_url_path)
                            continue

                        log.g().s(MANAGE_CRAWLER_MESSAGES.S_FILE_PARSED + " : " + m_url)
                        if m_classifier_response[m_url_path]['unsafe'] > 0.5:
                            m_porn_image_count += 1
                            self.__m_images[m_url] = 'a'
                            m_filtered_list.append(image_model(m_url, 'a'))

                        else:
                            self.__m_images[m_url] = 'g'
                            m_filtered_list.append(image_model(m_url, 'g'))
                        os.remove(m_url_path)

                        self.__m_duplication_url_handler.insert(m_url)

                elif m_url in self.__m_images:
                    m_filtered_list.append(image_model(m_url, self.__m_images[m_url]))

            except Exception as ex:
                 pass

        return m_filtered_list, m_porn_image_count

    def parse_static_files(self, p_images, p_documents, p_videos, p_content_type, p_url, p_local_parser):
        if p_local_parser is True:
            m_images = p_images
            m_porn_image_count = 0
        else:
            m_images, m_porn_image_count= self.__is_image_favourable(p_images, p_url)
        m_documents = self.__is_static_url_valid(p_documents)
        m_videos = self.__is_static_url_valid(p_videos)

        if m_porn_image_count>0:
            m_content_type = 'adult'
        else:
            m_content_type = p_content_type

        return m_images, m_documents, m_videos, m_content_type
