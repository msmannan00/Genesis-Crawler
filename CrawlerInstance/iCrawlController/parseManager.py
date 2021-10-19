# Local Imports
from CrawlerInstance.classModels.indexModel import indexModel
from CrawlerInstance.iCrawlController.htmlParser import htmlParser
from CrawlerInstance.iCrawlController.staticParseManager import staticParseManager


class parseManager:
    def __init__(self):

        self.m_static_parser = staticParseManager()
        pass

    def on_parse_html(self, p_html, p_base_url_model, p_response):

        m_index_model = indexModel()
        m_index_model.setBaseURL(p_base_url_model)

        if p_response is True:
            m_index_model = self.__on_html_parser_invoke(m_index_model, p_base_url_model, p_html)
            # m_index_model = self.__on_file_parser_invoke(m_index_model)
        else:
            m_index_model.setResponse(False)

        return m_index_model

    def __on_file_parser_invoke(self, p_index_model):
        return self.m_static_parser.invoke_parsing(p_index_model)

    def __on_html_parser_invoke(self, p_index_model, p_base_url_model, p_html):

        m_html_parser = htmlParser(p_base_url_model.getRedirectedURL(), p_html)
        m_html_parser.feed(p_html)

        p_index_model.setTitle(m_html_parser.get_title())
        p_index_model.setDescription(m_html_parser.get_description())

        correct_word, incorrect_word = m_html_parser.get_keyword()
        # p_index_model.setTfIdfModel(m_html_parser.getTFScore(correct_word, incorrect_word))
        # p_index_model.setTfIdfBinaryModel(m_html_parser.getTFBinaryScore(correct_word, incorrect_word))
        p_index_model.setKeyword(correct_word, incorrect_word)
        p_index_model.setSubURL(m_html_parser.get_sub_url())

        p_index_model.setResponse(True)
        # p_index_model.setImageURL(m_html_parser.m_image_url)
        # p_index_model.setDocURL(m_html_parser.m_doc_url)
        # p_index_model.setVidURL(m_html_parser.m_video_url)
        # p_index_model.setContentType(m_html_parser.getContentType())
        # p_index_model.setKeyword(correct_word, incorrect_word)
        # p_index_model.setValidityScore(m_html_parser.getValidityScore(correct_word))
        return p_index_model
