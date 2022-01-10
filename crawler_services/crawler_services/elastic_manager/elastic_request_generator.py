# Local Imports
import base64
import json

from crawler_instance.helper_services.helper_method import helper_method
from crawler_instance.local_shared_model.index_model import UrlObjectEncoder
from crawler_shared_directory.request_manager.request_handler import request_handler
from crawler_services.crawler_services.elastic_manager.elastic_enums import ELASTIC_KEYS, ELASTIC_INDEX, ELASTIC_REQUEST_COMMANDS


class elastic_request_generator(request_handler):

    def __on_index(self, p_data):
        m_host, m_sub_host = helper_method.split_host_url(p_data.m_base_url_model.m_url)
        m_data = {
            "m_doc_size": len(p_data.m_document),
            "m_img_size": len(p_data.m_images),
            "m_host": m_host,
            "m_sub_host": m_sub_host,
            "m_title": p_data.m_title,
            "m_meta_description": p_data.m_meta_description,
            "m_title_hidden": p_data.m_title_hidden,
            "m_important_content": p_data.m_important_content,
            "m_important_content_hidden": p_data.m_important_content_hidden,
            "m_total_hits": 0,
            "m_half_month_hits": 0,
            "m_monthly_hits": 0,
            "m_user_generated": p_data.m_user_crawled,
            "m_date": helper_method.get_time(),
            "m_meta_keywords": p_data.m_meta_keywords,
            "m_content": p_data.m_content,
            "m_content_type": p_data.m_content_type,
            "m_doc_url": p_data.m_document,
            "m_video": p_data.m_video,
            "m_images": json.loads(UrlObjectEncoder().encode(p_data.m_images)),
            "m_crawled_doc_url": [],
            "m_crawled_video": [],
            "m_crawled_user_images": []
        }


        return {ELASTIC_KEYS.S_DOCUMENT: ELASTIC_INDEX.S_WEB_INDEX, ELASTIC_KEYS.S_ID : base64.b64encode((m_host+m_sub_host).encode('ascii')), ELASTIC_KEYS.S_VALUE:m_data, ELASTIC_KEYS.S_FILTER:(m_host + m_sub_host)}

    def __on_index_user_query(self, p_data):
        m_host, m_sub_host = helper_method.split_host_url(p_data.m_base_url_model.m_url)
        m_data = {

            "script": {
                "source": "ctx._source.m_doc_size = params.m_doc_size;"
                          "ctx._source.m_img_size = params.m_img_size;"
                          "ctx._source.m_host = params.m_host;"
                          "ctx._source.m_sub_host = params.m_sub_host;"
                          "ctx._source.m_title = params.m_title;"
                          "ctx._source.m_meta_description = params.m_meta_description;"
                          "ctx._source.m_title_hidden = params.m_title_hidden;"
                          "ctx._source.m_important_content = params.m_important_content;"
                          "ctx._source.m_important_content_hidden = params.m_important_content_hidden;"
                          "ctx._source.m_total_hits  += params.m_total_hits;"
                          "ctx._source.m_half_month_hits  += params.m_half_month_hits;"
                          "ctx._source.m_monthly_hits  += params.m_monthly_hits;"
                          "ctx._source.m_user_generated  = params.m_user_generated;"
                          "ctx._source.m_date  = params.m_date;"
                          "ctx._source.m_meta_keywords  = params.m_meta_keywords;"
                          "ctx._source.m_content  = params.m_content;"
                          "ctx._source.m_content_type  = params.m_content_type;"
                          "ctx._source.m_crawled_doc_url  = params.m_crawled_doc_url;"
                          "ctx._source.m_crawled_video  = params.m_crawled_video;"
                          "ctx._source.m_crawled_user_images  = params.m_crawled_user_images;"
                ,"lang": "painless",
                "params": {
                    "m_doc_size": len(p_data.m_document),
                    "m_img_size": len(p_data.m_images),
                    "m_host": m_host,
                    "m_sub_host": m_sub_host,
                    "m_title": p_data.m_title,
                    "m_meta_description": p_data.m_meta_description,
                    "m_title_hidden": p_data.m_title_hidden,
                    "m_important_content": p_data.m_important_content,
                    "m_important_content_hidden": p_data.m_important_content_hidden,
                    "m_total_hits": 1,
                    "m_half_month_hits": 1,
                    "m_monthly_hits": 1,
                    "m_user_generated": True,
                    "m_date": helper_method.get_time(),
                    "m_meta_keywords": p_data.m_meta_keywords,
                    "m_content": p_data.m_content,
                    "m_content_type": p_data.m_content_type,
                    "m_crawled_doc_url": p_data.m_document,
                    "m_crawled_video": p_data.m_video,
                    "m_crawled_user_images": json.loads(UrlObjectEncoder().encode(p_data.m_images))
                }
            },
            "upsert": {
                "m_doc_size": len(p_data.m_document),
                "m_img_size": len(p_data.m_images),
                "m_host": m_host,
                "m_sub_host": m_sub_host,
                "m_title": p_data.m_title,
                "m_meta_description": p_data.m_meta_description,
                "m_title_hidden": p_data.m_title_hidden,
                "m_important_content": p_data.m_important_content,
                "m_important_content_hidden": p_data.m_important_content_hidden,
                "m_total_hits": 0,
                "m_half_month_hits": 0,
                "m_monthly_hits": 0,
                "m_user_generated": p_data.m_user_crawled,
                "m_date": helper_method.get_time(),
                "m_meta_keywords": p_data.m_meta_keywords,
                "m_content": p_data.m_content,
                "m_content_type": p_data.m_content_type,
                "m_crawled_doc_url": p_data.m_document,
                "m_crawled_video": p_data.m_video,
                "m_crawled_user_images": json.loads(UrlObjectEncoder().encode(p_data.m_images)),
                "m_doc_url": [],
                "m_video": [],
                "m_images": []
            }
        }

        return {ELASTIC_KEYS.S_DOCUMENT: ELASTIC_INDEX.S_WEB_INDEX, ELASTIC_KEYS.S_ID : base64.b64encode((m_host+m_sub_host).encode('ascii')), ELASTIC_KEYS.S_VALUE:m_data, ELASTIC_KEYS.S_FILTER:(m_host + m_sub_host)}

    def __on_unique_host(self):

        m_query = {
            "query": {
                "match": {
                    "m_sub_host": 'na'
                }
            },"_source": ["script.m_host"]
        }

        return {ELASTIC_KEYS.S_DOCUMENT: ELASTIC_INDEX.S_WEB_INDEX, ELASTIC_KEYS.S_FILTER:m_query}

    def __is_service_duplicate(self, p_content):

        m_query = {
            "query": {
                "match_phrase": {
                    "m_content": p_content
                }
            }
        }

        return {ELASTIC_KEYS.S_DOCUMENT: ELASTIC_INDEX.S_WEB_INDEX, ELASTIC_KEYS.S_FILTER:m_query}

    def invoke_trigger(self, p_commands, p_data=None):
        if p_commands == ELASTIC_REQUEST_COMMANDS.S_INDEX:
            return self.__on_index(p_data[0])
        if p_commands == ELASTIC_REQUEST_COMMANDS.S_INDEX_USER_QUERY:
            return self.__on_index_user_query(p_data[0])
        if p_commands == ELASTIC_REQUEST_COMMANDS.S_UNIQUE_HOST:
            return self.__on_unique_host()
        if p_commands == ELASTIC_REQUEST_COMMANDS.S_DUPLICATE:
            return self.__is_service_duplicate(p_data[0])
