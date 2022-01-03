# Local Imports
import json

from crawler_instance.helper_services.helper_method import helper_method
from crawler_instance.local_shared_model.index_model import UrlObjectEncoder
from crawler_shared_directory.request_manager.request_handler import request_handler
from crawler_services.crawler_services.elastic_manager.elastic_enums import ELASTIC_KEYS, ELASTIC_INDEX, ELASTIC_REQUEST_COMMANDS


class elastic_request_generator(request_handler):

    def __on_index(self, p_data):
        m_host, m_sub_host = helper_method.split_host_url(p_data.m_base_url_model.m_url)
        m_query = {
            "query":
                { "bool":
                      { "must":
                         [ { "term": { "m_host": m_host } },
                           { "term": { "m_sub_host": m_sub_host } }
                         ]
                      }
                 }
            }

        m_data = { "script": {'m_doc_size': len(p_data.m_document),'m_img_size': len(p_data.m_images), 'm_host':m_host, "m_sub_host":m_sub_host,'m_title':p_data.m_title,'m_meta_description': p_data.m_meta_description,'m_title_hidden':p_data.m_title_hidden,'m_important_content': p_data.m_important_content,'m_important_content_hidden': p_data.m_important_content_hidden, 'm_meta_keywords': p_data.m_meta_keywords, 'm_content': p_data.m_content, 'm_content_type': p_data.m_content_type, 'm_sub_url': p_data.m_sub_url, 'm_images': json.loads(UrlObjectEncoder().encode(p_data.m_images)), 'm_doc_url': p_data.m_document, 'm_vid': p_data.m_video}, "query": m_query}
        return {ELASTIC_KEYS.S_DOCUMENT: ELASTIC_INDEX.S_WEB_INDEX, ELASTIC_KEYS.S_VALUE:m_data, ELASTIC_KEYS.S_FILTER:(m_host + m_sub_host)}

    def __on_unique_host(self):

        m_query = {
            "query": {
                "match": {
                    "script.m_sub_host": 'na'
                }
            },"_source": ["script.m_host"]
        }

        return {ELASTIC_KEYS.S_DOCUMENT: ELASTIC_INDEX.S_WEB_INDEX, ELASTIC_KEYS.S_FILTER:m_query}

    def __is_service_duplicate(self, p_content):

        m_query = {
            "query": {
                "match_phrase": {
                    "script.m_content": p_content
                }
            }
        }

        return {ELASTIC_KEYS.S_DOCUMENT: ELASTIC_INDEX.S_WEB_INDEX, ELASTIC_KEYS.S_FILTER:m_query}

    def invoke_trigger(self, p_commands, p_data=None):
        if p_commands == ELASTIC_REQUEST_COMMANDS.S_INDEX:
            return self.__on_index(p_data[0])
        if p_commands == ELASTIC_REQUEST_COMMANDS.S_UNIQUE_HOST:
            return self.__on_unique_host()
        if p_commands == ELASTIC_REQUEST_COMMANDS.S_DUPLICATE:
            return self.__is_service_duplicate(p_data[0])
