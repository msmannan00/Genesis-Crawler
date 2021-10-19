# Local Imports
import os
import random
import string

from nudenet.classifier import Classifier
from CrawlerInstance.classModels.imagemodel import imageModel
from CrawlerInstance.constants import constants
from CrawlerInstance.logManager.logManager import log
from GenesisCrawlerServices.constants import strings
from CrawlerInstance.iCrawlController.webRequestManager import webRequestManager
from GenesisCrawlerServices.helperServices.duplicationHandler import DuplicationHandler


class staticParseManager:
    def __init__(self):
        self.m_web_request_hander = webRequestManager()
        self.m_duplication_handler = DuplicationHandler()
        pass

    def __is_static_url_valid(self, p_list):

        m_filtered_list = []

        for m_url in p_list:
            if self.m_duplication_handler.validate_duplicate_url(m_url) is False:
                self.m_duplication_handler.insert_url(m_url)

                m_response, m_header = self.m_web_request_hander.load_header(m_url)
                if m_response is True and ('content-length' not in m_header or int(m_header['content-length']) >= constants.S_MIN_CONTENT_LENGTH):
                   m_filtered_list.insert(0, m_url)
                   log.g().i(strings.S_FIILE_PARSED + " : " + m_url)
            if len(m_filtered_list)>5:
                break

        return m_filtered_list

    def __is_image_favourable(self, p_list):

        m_filtered_list = []

        for m_url in p_list:

            try:
                m_status, m_response = self.m_web_request_hander.download_image(m_url)

                if m_status:
                    key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

                    m_url_path = key + "." + m_response.headers['Content-Type'].split('/')[1]
                    m_url_type = key + "." + m_response.headers['Content-Type'].split('/')[0]
                    if m_url_type != "image":
                        return

                    file = open(m_url_path, "wb")
                    file.write(m_response.content)
                    file.close()

                    m_classifier = Classifier()
                    m_classifier_response = m_classifier.classify(m_url_path)
                    print(m_classifier_response[m_url_path]['unsafe'])

                    if m_classifier_response[m_url_path]['unsafe'] > 0.5:
                        print("Given Image At : " + m_url + " : Is Porn")
                        m_doc_collection = imageModel(m_url, 0)
                        m_filtered_list.append(m_doc_collection)
                    else:
                        print("Given Image At : " + m_url + " : Is Not Porn")
                        m_doc_collection = imageModel(m_url, 1)
                        m_filtered_list.append(m_doc_collection)
                    os.remove(m_url_path)
            except Exception as e:
                log.g().e(str(e))

        return m_filtered_list

    def invoke_parsing(self, p_index_model):
        p_index_model.m_image_url = self.__is_static_url_valid(p_index_model.m_image_url)
        p_index_model.m_image_url = self.__is_image_favourable(p_index_model.m_image_url)
        p_index_model.m_doc_url = self.__is_static_url_valid(p_index_model.m_doc_url)
        p_index_model.m_vid_url = self.__is_static_url_valid(p_index_model.m_vid_url)

        return p_index_model
