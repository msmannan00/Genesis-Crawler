# Local Imports
import mimetypes
import pathlib
import re
import validators

from abc import ABC
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from raven.transport import requests
from crawler_instance.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler_instance.constants.strings import STRINGS
from crawler_instance.helper_services.helper_method import helper_method
from crawler_instance.i_crawl_crawler.i_crawl_enums import PARSE_TAGS
from crawler_services.crawler_services.topic_manager.topic_classifier_controller import topic_classifier_controller
from crawler_services.crawler_services.topic_manager.topic_classifier_enums import TOPIC_CLASSFIER_COMMANDS
from crawler_services.helper_services.spell_check_handler import spell_checker_handler

# class to parse html raw duplicationHandlerService

class html_parse_manager(HTMLParser, ABC):

    def __init__(self, m_base_url, m_html):
        super().__init__()
        self.m_html = m_html
        self.m_base_url = m_base_url

        self.m_title = STRINGS.S_EMPTY
        self.m_description = STRINGS.S_EMPTY
        self.m_content_type = CRAWL_SETTINGS_CONSTANTS.S_THREAD_CATEGORY_GENERAL
        self.m_sub_url = []
        self.m_image_url = []
        self.m_doc_url = []
        self.m_video_url = []
        self.m_unary_tf_words = {}
        self.m_binary_tf_words = {}

        self.m_meta_description = STRINGS.S_EMPTY
        self.m_meta_keyword = STRINGS.S_EMPTY

        self.m_query_url_count = 0
        self.m_paragraph_count = 0

        self.rec = PARSE_TAGS.S_NONE

    # find url type and populate the list respectively

    def __insert_external_url(self, p_url):
        if p_url is not None and not str(p_url).__contains__("#"):
            mime = mimetypes.MimeTypes().guess_type(p_url)[0]
            if len(p_url) <= CRAWL_SETTINGS_CONSTANTS.S_MAX_URL_SIZE:

                # Joining Relative URL
                if not p_url.startswith("https://") and not p_url.startswith("http://") and not p_url.startswith(
                        "ftp://"):
                    m_temp_base_url = self.m_base_url
                    if not m_temp_base_url.m_url.endswith("/"):
                        m_temp_base_url.m_url = m_temp_base_url.m_url + "/"
                    p_url = requests.compat.urljoin(m_temp_base_url.m_url, p_url)
                    p_url = p_url.replace(" ", "%20")
                    p_url = helper_method.on_clean_url(helper_method.normalize_slashes(p_url))

                if validators.url(p_url):
                    suffix = ''.join(pathlib.Path(p_url).suffixes)
                    m_host_url = helper_method.get_host_url(p_url)
                    if mime is None or mime != "text/html":
                        if suffix in CRAWL_SETTINGS_CONSTANTS.S_DOC_TYPES and len(self.m_doc_url) < 10:
                            self.m_doc_url.append(p_url)
                        elif str(mime).startswith("video") and len(self.m_video_url) < 10:
                            self.m_video_url.append(p_url)
                    elif m_host_url.__contains__(".onion"):
                        if m_host_url.__contains__("?"):
                            self.m_query_url_count+=1
                        if self.m_query_url_count < 5:
                            self.m_sub_url.append(p_url)


    def handle_starttag(self, p_tag, p_attrs):
        if p_tag == "a":
            for name, value in p_attrs:
                if name == "href":
                    self.__insert_external_url(value)

        if p_tag == 'img':
            for value in p_attrs:
                if value[0] == 'src' and not helper_method.is_url_base_64(value[1]) and len(self.m_image_url)<35:
                    # Joining Relative URL
                    m_temp_base_url = self.m_base_url
                    if not m_temp_base_url.m_url.endswith("/"):
                        m_temp_base_url.m_url = m_temp_base_url.m_url + "/"
                    m_url = requests.compat.urljoin(m_temp_base_url.m_url, value[1])
                    m_url = helper_method.on_clean_url(helper_method.normalize_slashes(m_url))
                    self.m_image_url.append(m_url)

        elif p_tag == 'title':
            self.rec = PARSE_TAGS.S_TITLE

        elif p_tag == 'h1' or p_tag == 'h2' or p_tag == 'h3' or p_tag == 'h4':
            self.rec = PARSE_TAGS.S_HEADER

        elif p_tag == 'span' and self.m_paragraph_count==0:
            self.rec = PARSE_TAGS.S_SPAN

        elif p_tag == 'li' or p_tag == 'br':
            self.rec = PARSE_TAGS.S_PARAGRAPH

        elif p_tag == 'p':
            self.rec = PARSE_TAGS.S_PARAGRAPH
            self.m_paragraph_count+=1

        elif p_tag == 'meta':
            try:
                if p_attrs[0][1] == 'description':
                    if len(p_attrs) > 1 and len(p_attrs[1]) > 0 and p_attrs[1][0] == 'content' and p_attrs[1][1] is not None:
                        self.__add_to_description(p_attrs[1][1])
                        self.m_meta_description = p_attrs[1][1]
                elif p_attrs[0][1] == 'keywords':
                    if len(p_attrs) > 1 and len(p_attrs[1]) > 0 and p_attrs[1][0] == 'content' and p_attrs[1][1] is not None:
                        self.m_meta_keyword = p_attrs[1][1].replace(",", " ")
            except Exception:
                pass
        else:
            self.rec = PARSE_TAGS.S_NONE

    def handle_endtag(self, p_tag):
        if p_tag == 'p':
            self.m_paragraph_count -= 1
        self.rec = PARSE_TAGS.S_NONE

    def handle_data(self, p_data):
        if self.rec == PARSE_TAGS.S_HEADER:
            self.__add_to_description(p_data)
        if self.rec == PARSE_TAGS.S_TITLE:
            self.m_title = p_data
        elif self.rec == PARSE_TAGS.S_META and len(self.m_title) > 0:
            self.m_title = p_data
        elif self.rec == PARSE_TAGS.S_PARAGRAPH:
            self.__add_to_description(p_data)
        elif self.rec == PARSE_TAGS.S_SPAN and p_data.count(' ')>5:
            self.__add_to_description(p_data)
        elif self.rec == PARSE_TAGS.S_NONE:
            if self.m_paragraph_count > 0:
                self.__add_to_description(p_data)

    # creating keyword shared_model for webpage representation

    def __add_to_description(self, p_data):
        if p_data.count(' ')>2 and p_data not in self.m_description:
            p_data = re.sub('[^A-Za-z0-9 ,;"\]\[/.+-;!\'@#$%^&*_+=]', '', p_data)
            p_data = re.sub(' +', ' ', p_data)
            p_data = re.sub(r'^\W*', '', p_data)

            if len(self.m_description)>2:
                self.m_description = self.m_description + spell_checker_handler.get_instance().validate_sentence(p_data.lower())
            else:
                self.m_description = self.m_description + spell_checker_handler.get_instance().validate_sentence(p_data.capitalize())

    def __get_html_text(self):
        m_soup = BeautifulSoup(self.m_html, "html.parser")
        m_text = m_soup.get_text(separator=u' ')

        m_text = m_text.replace('\n', ' ')
        m_text = m_text.replace('\t', ' ')
        m_text = m_text.replace('\r', ' ')
        m_text = re.sub(' +', ' ', m_text)
        return m_text

    # --------------- Text Preprocessing --------------- #

    def __update_unary_score(self, m_stemmed_word, p_length):
        if m_stemmed_word in self.m_unary_tf_words:
            m_tf_score = self.m_unary_tf_words[m_stemmed_word]
            m_tf_score = round(((m_tf_score * p_length) + 1) / p_length, 2)
            self.m_unary_tf_words[m_stemmed_word] = m_tf_score
        else:
            self.m_unary_tf_words[m_stemmed_word] = round(1 / p_length, 2)

    def __update_binary_score(self, m_stemmed_word_w1, m_stemmed_word_w2, p_length):
        if m_stemmed_word_w1 != STRINGS.S_EMPTY:
            m_binary_stemmed_word = m_stemmed_word_w1 + " " + m_stemmed_word_w2
            if m_binary_stemmed_word in self.m_binary_tf_words:
                m_tf_binary_score = self.m_binary_tf_words[m_binary_stemmed_word]
                m_tf_binary_score = round(((m_tf_binary_score * p_length) + 1) / p_length, 3)
                self.m_binary_tf_words[m_binary_stemmed_word] = m_tf_binary_score
            else:
                self.m_binary_tf_words[m_binary_stemmed_word] = round(1 / p_length, 3)

        pass

    def __generate_score(self, p_text):

        # New Line and Tab Remover
        p_text = p_text.replace('\\n', ' ')
        p_text = p_text.replace('\\t', ' ')
        p_text = p_text.replace('\\r', ' ')

        # Lower Case
        p_text = p_text.lower()

        # Remove Special Character
        p_text = re.sub('[^A-Za-z0-9]+', ' ', p_text)

        # Tokenizer
        m_word_list = p_text.split()

        # Word Checking
        m_last_word = STRINGS.S_EMPTY
        for m_word in m_word_list:
            m_valid_status = spell_checker_handler.get_instance().validate_word(m_word)
            if m_valid_status is True:
                m_stemmed_word = spell_checker_handler.get_instance().stem_word(m_word)
                self.__update_unary_score(m_stemmed_word, len(m_word_list))
                self.__update_binary_score(m_last_word, m_stemmed_word, len(m_word_list)/4)
                m_last_word = m_word

    # ----------------- Data Recievers -----------------

    def __get_title(self):
        return helper_method.strip_special_character(self.m_title).strip()

    def __get_description(self):
        clean_description = helper_method.strip_special_character(self.m_description)

        return clean_description

    def __get_score(self):
        self.__generate_score(self.__get_html_text() + " " + self.m_title + " " + self.m_meta_description)
        return self.m_unary_tf_words, self.m_binary_tf_words

    def __get_validity_score(self):
        m_rank = ((len(self.m_unary_tf_words) + len(self.m_binary_tf_words)) > 10) * 10 + (len(self.m_sub_url) > 0) * 5
        return m_rank

    def __get_content_type(self):
        if (len(self.m_unary_tf_words) + len(self.m_binary_tf_words))>0:
            self.m_content_type = topic_classifier_controller.get_instance().invoke_trigger(TOPIC_CLASSFIER_COMMANDS.S_PREDICT_CLASSIFIER, [self.m_title, self.m_description," ".join(self.m_unary_tf_words.keys())])

        return self.m_content_type

    def __get_static_file(self):
        return self.m_sub_url, self.m_image_url, self.m_doc_url, self.m_video_url

    def parse_html_files(self):
        m_title = self.__get_title()
        m_description = self.__get_description()
        m_unary_tf_words, m_binary_tf_words = self.__get_score()
        m_validity_score = self.__get_validity_score()
        m_content_type = self.__get_content_type()
        m_sub_url, m_images, m_doc, m_vid = self.__get_static_file()

        return m_title, m_description, m_unary_tf_words, m_binary_tf_words, m_validity_score, m_content_type, m_sub_url, m_images, m_doc, m_vid
