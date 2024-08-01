# Local Imports
from copy import copy

from crawler.crawler_instance.genbot_service.html_parse_manager import html_parse_manager
from crawler.crawler_instance.genbot_service.file_parse_manager import file_parse_manager
from crawler.crawler_instance.local_shared_model.index_model import index_model, index_model_init, index_image_model_init
from crawler.crawler_instance.local_shared_model.url_model import url_model


class parse_controller:

    m_static_parser = None

    def __init__(self):
        self.m_static_parser = file_parse_manager()

    def on_parse_html(self, p_html, p_request_model: url_model):
        m_title, m_meta_description, m_title_hidden, m_important_content, m_important_content_hidden, m_meta_keywords, m_content, m_content_type, m_sub_url, m_images, m_document, m_video, m_validity_score, m_extended_content = self.__on_html_parser_invoke(copy(p_request_model.m_url), p_html)
        return index_model_init(p_request_model, m_title, m_meta_description, m_title_hidden, m_important_content, m_important_content_hidden, m_meta_keywords, m_content, m_content_type, m_sub_url, m_document, m_video, m_validity_score, m_extended_content), m_images

    def on_parse_files(self, p_parsed_model: index_model, p_images, p_proxy_queue):
        m_images, m_documents, m_videos, m_content_type, m_unique_file_model = self.__on_static_parser_invoke(p_images, p_parsed_model. m_document, p_parsed_model. m_video, p_parsed_model.m_content_type[0], p_proxy_queue)
        return index_image_model_init(p_parsed_model.m_base_model, p_parsed_model.m_title, p_parsed_model.m_meta_description, p_parsed_model.m_title_hidden, p_parsed_model.m_important_content, p_parsed_model.m_important_content_hidden, p_parsed_model.m_meta_keywords, p_parsed_model.m_content, m_content_type, p_parsed_model.m_sub_url, m_images, m_documents, m_videos, p_parsed_model.m_validity_score, p_parsed_model.m_extended_content), m_unique_file_model

    def __on_html_parser_invoke(self, p_base_url, p_html):

        m_html_parser = html_parse_manager(p_base_url, p_html)
        m_html_parser.feed(p_html)
        return m_html_parser.parse_html_files()

    def __on_static_parser_invoke(self, p_images, p_documents, p_videos, p_content_type, p_proxy_queue):
        return self.m_static_parser.parse_static_files(p_images, p_documents, p_videos, p_content_type, p_proxy_queue)

    def on_static_parser_init(self, p_documents, p_images, p_videos):
        return self.m_static_parser.init(p_documents, p_images, p_videos)
