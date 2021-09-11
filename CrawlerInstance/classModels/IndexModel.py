# Local Imports
import copy
import re

from json import JSONEncoder

from CrawlerInstance.classModels.TFIDFModel import TFIDFModel
from CrawlerInstance.classModels.UrlModel import UrlModel


# model representing information of any particular url
class IndexModel:
    # Local Variables
    m_title = ""
    m_description = ""
    m_base_url_model = UrlModel(None, None)
    m_url = ""
    m_response = False
    m_innode_count = 0
    m_sub_url = []
    m_image_url = []
    m_doc_url = []
    m_vid_url = []
    m_validity_score = 0
    m_content_type = "General"
    m_thread_id = ""
    m_tfidf_model = None

    # Initializations
    def __init__(self):
        pass

    # Getter Setters
    def setTitle(self, p_title):
        self.m_title = p_title

    def setDescription(self, p_description):
        self.m_description = re.sub(' +', ' ', p_description)

    def setBaseURL(self, p_base_url_model):
        self.m_base_url_model = p_base_url_model
        self.setURL(p_base_url_model.m_redirected_host + p_base_url_model.m_redirected_subhost)

    def setURL(self, p_url):
        self.m_url = p_url

    def setSubURL(self, p_sub_url):
        self.m_sub_url = p_sub_url

    def setImageURL(self, p_image_url):
        self.m_image_url = p_image_url

    def setDocURL(self, p_doc_url):
        self.m_doc_url = p_doc_url

    def setVidURL(self, p_vid_url):
        self.m_vid_url = p_vid_url

    def setTfIdfModel(self, p_tfidf_model):
        self.m_tfidf_model = p_tfidf_model

    def getTfIdfModel(self):
        return self.m_tfidf_model

    def setContentType(self, p_content_type):
        self.m_content_type = p_content_type

    def setKeyword(self, m_correct_keyword, p_incorrect_keyword):
        self.m_correct_keyword = m_correct_keyword
        self.m_incorrect_keyword = p_incorrect_keyword

    def setResponse(self, p_response):
        self.m_response = p_response

    def setValidityScore(self, p_validity_score):
        self.m_validity_score = p_validity_score

    def setInnodeCount(self, p_innode_count):
        self.m_innode_count = p_innode_count

    def setThreadID(self, p_thread_id):
        self.m_thread_id = p_thread_id

    def getTFIDFModel(self):
        return self.m_tfidf_model

# subclass JSONEncoder
class UrlObjectEncoder(JSONEncoder):
    def default(self, o):
        m_dict = copy.deepcopy(o.__dict__)

        # skip objects for server processing to reduce request load
        if 'm_sub_url' in m_dict:
            del m_dict['m_sub_url']
            del m_dict['m_response']
            del m_dict['m_thread_id']
            del m_dict['m_validity_score']
            del m_dict['m_base_url_model']

        return m_dict
