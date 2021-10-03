# Local Imports
from CrawlerInstance.classModels.IndexModel import IndexModel
from CrawlerInstance.iCrawlController.HtmlParser import HtmlParser
from CrawlerInstance.iCrawlController.StaticParser import StaticParser


# Parsing Manager - It parses a given url and generate and opject of parsed url model or indexmodel.py

class Parser:
    def __init__(self):
        self.m_static_parser = StaticParser()
        pass

    def parseHtml(self, p_html, p_base_url_model, p_response):

        m_index_model = IndexModel()
        m_index_model.setBaseURL(p_base_url_model)

        if p_response is True:
            m_index_model = self.htmlParserInvoke(m_index_model, p_base_url_model, p_html)
            m_index_model = self.staticParserInvoke(m_index_model)
        else:
            m_index_model.setResponse(False)

        return m_index_model

    def staticParserInvoke(self, p_index_model):
        return self.m_static_parser.invokeParsing(p_index_model)

    def htmlParserInvoke(self, p_index_model, p_base_url_model, p_html):
        m_html_parser = HtmlParser(p_base_url_model.getRedirectedURL(), p_html)
        m_html_parser.feed(p_html)
        correct_word, incorrect_word = m_html_parser.getKeyword()

        p_index_model.setTitle(m_html_parser.getTitle()[0:500])
        p_index_model.setDescription(m_html_parser.getDescription())
        p_index_model.setResponse(True)
        p_index_model.setTfIdfModel(m_html_parser.getTFScore(correct_word, incorrect_word))
        p_index_model.setTfIdfBinaryModel(m_html_parser.getTFBinaryScore(correct_word, incorrect_word))
        p_index_model.setImageURL(m_html_parser.image_URL)
        p_index_model.setDocURL(m_html_parser.doc_URL)
        p_index_model.setVidURL(m_html_parser.vid_URL)
        p_index_model.setContentType(m_html_parser.getContentType())
        p_index_model.setKeyword(correct_word, incorrect_word)
        p_index_model.setSubURL(m_html_parser.getSubURL(p_html))
        p_index_model.setSubURL(m_html_parser.getSubURL(p_html))
        p_index_model.setValidityScore(m_html_parser.getValidityScore(correct_word))
        return p_index_model
