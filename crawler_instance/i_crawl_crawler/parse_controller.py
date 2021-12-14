# Local Imports
from crawler_instance.i_crawl_crawler.html_parse_manager import html_parse_manager
from crawler_instance.i_crawl_crawler.i_crawl_enums import CRAWL_STATUS_TYPE
from crawler_instance.i_crawl_crawler.static_parse_manager import file_parse_manager
from crawler_instance.i_crawl_crawler.static_parse_manager.file_parse_manager import file_parse_manager
from crawler_instance.shared_class_model.index_model import index_model
from genesis_crawler_services.crawler_services.content_duplication_manager.content_duplication_controller import \
    content_duplication_controller
from genesis_crawler_services.crawler_services.content_duplication_manager.content_duplication_enums import \
    CONTENT_DUPLICATION_MANAGER


class parse_controller:

    m_static_parser = None
    m_html_parser = None

    def __init__(self):
        self.m_static_parser = file_parse_manager()

    def on_parse_html(self, p_html, p_base_url_model):
        m_title, m_description, m_correct_keyword, m_incorrect_keyword, m_uniary_tfidf_score, m_binary_tfidf_score, m_validity_score,m_content_type,  m_sub_url, m_images, m_doc, m_vid = self.__on_html_parser_invoke(p_base_url_model, p_html)
        m_duplication_status, m_url_status = self.__verify_content_duplication(m_title, m_description, m_content_type, p_base_url_model.m_depth)

        if m_duplication_status is False:
            m_images, m_documents, m_videos, m_content_type = self.__on_static_parser_invoke(m_images, m_doc, m_vid, m_content_type[0], p_base_url_model.m_url)

            try:
                return True, index_model(p_base_url_model = p_base_url_model, p_title = m_title, p_description = m_description, p_correct_keyword = m_correct_keyword, p_incorrect_keyword = m_incorrect_keyword, p_uniary_tfidf_score = m_uniary_tfidf_score, p_binary_tfidf_score = m_binary_tfidf_score, p_validity_score = m_validity_score,p_content_type = m_content_type,  p_sub_url = m_sub_url, p_images = m_images, p_documents = m_documents, p_videos = m_videos), m_url_status
            except Exception as ex:
                pass
        return False, None, m_url_status


    def __verify_content_duplication(self, p_title, p_description, p_content_type, p_depth):
        m_status = content_duplication_controller.get_instance().invoke_trigger(CONTENT_DUPLICATION_MANAGER.S_VALIDATE,[p_title, p_description, p_content_type])
        if p_depth != 1 or m_status is False:
            content_duplication_controller.get_instance().invoke_trigger(CONTENT_DUPLICATION_MANAGER.S_INSERT, [p_title, p_description, p_content_type])
            return False, CRAWL_STATUS_TYPE.S_NONE
        else:
            return True, CRAWL_STATUS_TYPE.S_DUPLICATE

    def __on_html_parser_invoke(self, p_base_url, p_html):

        self.m_html_parser = html_parse_manager(p_base_url, p_html)
        self.m_html_parser.feed(p_html)
        return self.m_html_parser.parse_html_files()

    def __on_static_parser_invoke(self, p_images, p_documents, p_videos, p_content_type, p_url):
        return self.m_static_parser.parse_static_files(p_images, p_documents, p_videos, p_content_type, p_url)
