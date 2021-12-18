# Local Imports
import copy
from json import JSONEncoder


class index_model:

    def __init__(self, p_base_url_model, p_title = None, p_description = None , p_uniary_tfidf_score = None , p_binary_tfidf_score = None , p_validity_score = None ,p_content_type = None ,  p_sub_url = None , p_images = None , p_documents = None , p_videos = None ):
        self.m_base_url_model = p_base_url_model
        self.m_title = p_title
        self.m_description = p_description
        self.m_uniary_tfidf_score = p_uniary_tfidf_score
        self.m_binary_tfidf_score = p_binary_tfidf_score
        self.m_validity_score = p_validity_score
        self.m_content_type = p_content_type
        self.m_sub_url = p_sub_url
        self.m_images = p_images
        self.m_documents = p_documents
        self.m_videos = p_videos

class UrlObjectEncoder(JSONEncoder):
    def default(self, o):
        m_dict = copy.deepcopy(o.__dict__)

        # skip objects for server processing to reduce request load
        if 'm_sub_url' in m_dict:
            del m_dict['m_sub_url']

        return m_dict