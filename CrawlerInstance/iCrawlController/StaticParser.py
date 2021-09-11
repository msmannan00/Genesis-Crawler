# Local Imports
from CrawlerInstance.constants import constants
from CrawlerInstance.logManager.LogManager import log
from GenesisCrawlerServices.constants import strings
from GenesisCrawlerServices.duplicationHandlerService.DuplicationHandlerLocal import DuplicationHandlerLocal
from CrawlerInstance.iCrawlController.WebRequestHandler import WebRequestHandler


# Image Parsing Manager - It parses a given url and generate and opject of parsed url model or indexmodel.py
class StaticParser:
    def __init__(self):
        # self.m_web_request_hander = WebRequestHandler()
        # self.m_valid_images = DuplicationHandlerLocal()
        # self.m_invalid_images = DuplicationHandlerLocal()
        pass

    def invokeParsing(self, p_index_model):
        # p_index_model.m_image_url = self.isStaticURLValid(p_index_model.m_image_url)
        # p_index_model.m_doc_url = self.isStaticURLValid(p_index_model.m_doc_url)
        # p_index_model.m_vid_url = self.isStaticURLValid(p_index_model.m_vid_url)
        return p_index_model

    def isStaticURLValid(self, p_list):
        if 1==1:
            return p_list

        m_is_element_parsed = {None}
        m_filtered_list = []
        for m_url in p_list:
            if m_url not in m_is_element_parsed:
                m_is_element_parsed.add(m_url)
                if self.m_valid_images.isURLDuplicate(m_url):
                    self.m_valid_images.insertURL(m_url)
                elif self.m_invalid_images.isURLDuplicate(m_url):
                    continue
                else:
                    m_filtered_list.insert(0, m_url)
                    self.m_valid_images.insertURL(m_url)
                    log.g().i(strings.image_parsed + " : " + m_url)

                    # m_response, m_header = self.m_web_request_hander.loadHeader(m_url)
                    # if m_response is True and ('content-length' not in m_header or int(m_header['content-length']) >= constants.m_min_content_length):
                    #     m_filtered_list.insert(0, m_url)
                    #     self.m_valid_images.insertURL(m_url)
                    #     log.g().i(strings.image_parsed + " : " + m_url)
                    # else:
                    #     self.m_invalid_images.insertURL(m_url)
        return m_filtered_list
