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
from crawler_instance.constants.strings import GENERIC_STRINGS
from crawler_instance.helper_services.helper_method import helper_method
from crawler_instance.i_crawl_crawler.i_crawl_enums import PARSE_TAGS
from genesis_crawler_services.crawler_services.topic_manager.topic_classifier_controller import topic_classifier_controller
from genesis_crawler_services.crawler_services.topic_manager.topic_classifier_enums import TOPIC_CLASSFIER_COMMANDS
from genesis_crawler_services.helper_services.spell_check_handler import spell_checker_handler

# class to parse html raw duplicationHandlerService
class html_parse_manager(HTMLParser, ABC):

    def __init__(self, m_base_url, m_html):
        super().__init__()
        self.m_html = m_html

        self.m_title = GENERIC_STRINGS.S_EMPTY
        self.m_description = GENERIC_STRINGS.S_EMPTY
        self.m_keywords = GENERIC_STRINGS.S_EMPTY
        self.m_content_type = CRAWL_SETTINGS_CONSTANTS.S_THREAD_CATEGORY_GENERAL
        self.m_sub_url = []
        self.m_image_url = []
        self.m_doc_url = []
        self.m_video_url = []

        self.m_base_url = m_base_url
        self.m_paragraph_count = 0
        self.rec = PARSE_TAGS.S_NONE
        self.m_base_host_url = helper_method.get_host_url(m_base_url.m_url)

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
                    if mime is None or mime != "text/html":
                        m_host_url = helper_method.get_host_url(p_url)
                        if suffix in CRAWL_SETTINGS_CONSTANTS.S_DOC_TYPES and len(self.m_doc_url) < 10:
                            self.m_doc_url.append(p_url)
                        elif str(mime).startswith("video") and len(self.m_video_url) < 10:
                            self.m_video_url.append(p_url)
                        elif m_host_url.__contains__(".onion"):
                            self.m_sub_url.append(p_url)


    def handle_starttag(self, p_tag, p_attrs):
        if p_tag == "a":
            for name, value in p_attrs:
                if name == "href":
                    self.__insert_external_url(value)

        if p_tag == 'img':
            for value in p_attrs:
                if value[0] == 'src' and not helper_method.is_url_base_64(value[1]) and len(self.m_image_url)<50:
                    # Joining Relative URL
                    m_temp_base_url = self.m_base_url
                    if not m_temp_base_url.m_url.endswith("/"):
                        m_temp_base_url.m_url = m_temp_base_url.m_url + "/"
                    m_url = requests.compat.urljoin(m_temp_base_url.m_url, value[1])
                    m_url = helper_method.on_clean_url(helper_method.normalize_slashes(m_url))
                    self.m_image_url.append(m_url)

        elif p_tag == 'title':
            self.rec = PARSE_TAGS.S_TITLE

        elif p_tag == 'h1':
            self.rec = PARSE_TAGS.S_HEADER

        elif p_tag == 'p':
            self.rec = PARSE_TAGS.S_PARAGRAPH

        elif p_tag == 'meta':
            try:
                if p_attrs[0][1] == 'description':
                    if len(p_attrs) > 1 and len(p_attrs[1]) > 0 and p_attrs[1][0] == 'content' and p_attrs[1][
                        1] is not None:
                        self.m_description = p_attrs[1][1]
                elif p_attrs[0][1] == 'keywords':
                    if len(p_attrs) > 1 and len(p_attrs[1]) > 0 and p_attrs[1][0] == 'content' and p_attrs[1][
                        1] is not None:
                        self.m_keywords = p_attrs[1][1].replace(",", " ")
            except Exception:
                pass
        else:
            self.rec = PARSE_TAGS.S_NONE

    def handle_data(self, p_data):
        if self.rec == PARSE_TAGS.S_HEADER:
            self.m_description = self.m_description + spell_checker_handler.get_instance().extract_valid_validator(p_data)
        if self.rec == PARSE_TAGS.S_TITLE:
            self.m_title = p_data
        elif self.rec == PARSE_TAGS.S_META and len(self.m_title) > 0:
            self.m_title = p_data
        elif self.rec == PARSE_TAGS.S_PARAGRAPH:
            self.m_description = self.m_description + spell_checker_handler.get_instance().extract_valid_validator(p_data)
            self.m_paragraph_count += 1
        self.rec = PARSE_TAGS.S_NONE
        # creating keyword shared_model for webpage representation

    def __set_keyword_model(self, p_valid_keywords, p_invalid_keywords):
        return p_valid_keywords, p_invalid_keywords

        # extract text from raw html

    def __get_html_text(self):
        m_soup = BeautifulSoup(self.m_html, "html.parser")
        m_text = m_soup.get_text(separator=u' ')

        m_text = m_text.replace('\n', ' ')
        m_text = m_text.replace('\t', ' ')
        m_text = m_text.replace('\r', ' ')
        m_text = re.sub(' +', ' ', m_text)
        return m_text

        # --------------- Text Preprocessing --------------- #

    def __clean_html(self, m_query):
        m_query = re.sub('\W+', ' ', m_query)
        m_query = m_query.lower().split()

        m_range = 0
        for m_count in range(len(m_query)):
            if helper_method.is_stop_word(m_query[m_range]):
                del m_query[m_range]
            else:
                m_range += 1

        return ' '.join(m_query)

    def __text_preprocessing(self, p_text):

        # New Line and Tab Remover
        p_text = p_text.replace('\\n', ' ')
        p_text = p_text.replace('\\t', ' ')
        p_text = p_text.replace('\\r', ' ')

        # Tokenizer
        word_list = p_text.split()

        # Lower Case
        word_list = [x.lower() for x in word_list]

        # Word Checking
        incorrect_word, correct_word = spell_checker_handler.get_instance().validation_handler(word_list)

        # Cleaning Incorrect Words
        incorrect_word_cleaned = []
        for m_word in incorrect_word:
            incorrect_word_filter, correct_word_filter = spell_checker_handler.get_instance().invalid_validation_handler(
                m_word)
            if len(correct_word_filter) > 0 and len(correct_word_filter) + 1 >= len(incorrect_word_filter):
                correct_word = correct_word + correct_word_filter
            elif spell_checker_handler.get_instance().incorrect_word_validator(m_word) is True and len(
                    incorrect_word_filter) <= 1:
                incorrect_word_cleaned.append(m_word)

        # Remove Special Character
        word_list = [re.sub('[^a-zA-Z0-9]+', '', _) for _ in incorrect_word_cleaned]
        incorrect_word_cleaned = list(filter(None, word_list))

        correct_word = list(set(correct_word))
        return correct_word, incorrect_word_cleaned

        # ----------------- Data Recievers -----------------



    def __get_title(self):
        return helper_method.strip_special_character(self.m_title).strip()

    def __get_description(self):
        clean_description = helper_method.strip_special_character(self.m_description)
        return clean_description

    def __get_keyword(self):

        m_valid_keywords_model, m_invalid_keywords_model = self.__text_preprocessing(self.m_keywords)
        m_valid_keywords_model_filtered_1, m_invalid_keywords_model_filtered_1 = self.__set_keyword_model(m_valid_keywords_model, m_invalid_keywords_model)

        m_valid_keywords_model, m_invalid_keywords_model = self.__text_preprocessing(self.m_title)
        m_valid_keywords_model_filtered_2, m_invalid_keywords_model_filtered_2 = self.__set_keyword_model(m_valid_keywords_model, m_invalid_keywords_model)

        m_valid_keywords_model, m_invalid_keywords_model = self.__text_preprocessing(self.m_description)
        m_valid_keywords_model_filtered_3, m_invalid_keywords_model_filtered_3 = self.__set_keyword_model(m_valid_keywords_model, m_invalid_keywords_model)

        m_valid_keywords_model, m_invalid_keywords_model = self.__text_preprocessing(self.__get_html_text())
        m_valid_keywords_model_filtered_4, m_invalid_keywords_model_filtered_4 = self.__set_keyword_model(m_valid_keywords_model, m_invalid_keywords_model)

        return (m_valid_keywords_model_filtered_1 + m_valid_keywords_model_filtered_2 + m_valid_keywords_model_filtered_3 + m_valid_keywords_model_filtered_4), m_invalid_keywords_model_filtered_2, m_valid_keywords_model_filtered_4, m_invalid_keywords_model_filtered_4

    def __get_validity_score(self, p_keyword):
        m_rank = (len(p_keyword) > 10) * 10 + (len(self.m_sub_url) > 0) * 5
        return m_rank

    def __get_content_type(self, p_correct_word):
        if len(p_correct_word)>0:
            self.m_content_type = topic_classifier_controller.get_instance().invoke_trigger(TOPIC_CLASSFIER_COMMANDS.S_PREDICT_CLASSIFIER, [self.m_title, self.m_description," ".join(p_correct_word)])

        return self.m_content_type

    def __get_tfidf_score(self, p_correct_keyword, p_incorrect_keyword, p_total_keywords):
        m_doc_collection = {}
        m_text = self.__clean_html(self.__get_html_text())
        for m_word in set(p_correct_keyword):
            m_count = m_text.count(m_word)
            if m_count != 0 :
                m_doc_collection[m_word] = format(round(m_count / p_total_keywords, 3))

        for m_word in set(p_incorrect_keyword):
            m_count = m_text.count(m_word)
            if m_count != 0 :
                m_doc_collection[m_word] = format(round(m_count / p_total_keywords, 3))

        return m_doc_collection

    def __get_tfidf_binary_score(self):
        m_text = self.__clean_html(self.__get_html_text())

        m_text = m_text.replace('\\n', ' ')
        m_text = m_text.replace('\\t', ' ')
        m_text = m_text.replace('\\r', ' ')

        # Tokenizer
        word_list = m_text.split()

        # Lower Case
        word_list = [x.lower() for x in word_list]

        # Word Checking
        word_list = spell_checker_handler.get_instance().binary_validation_handler(word_list)

        # Cleaning Incorrect Words
        m_word_count = len(word_list)/2
        m_tfidf = {}

        for count in range(0, len(word_list)):
            if len(word_list) <= count*2+1:
                break

            m_bigram = word_list[count*2] + " " + word_list[count*2+1]
            if m_bigram in m_tfidf:
                m_bi_count = (m_tfidf[m_bigram] * m_word_count) + 2
            else:
                m_bi_count = 2

            m_tfidf[m_bigram] = float(round(m_bi_count / m_word_count, 3))

        return m_tfidf

    def __get_static_file(self):
        return self.m_sub_url, self.m_image_url, self.m_doc_url, self.m_video_url

    def parse_html_files(self):
        m_title = self.__get_title()
        m_description = self.__get_description()
        m_correct_keyword, m_incorrect_keyword,m_full_valid_keyword, m_full_invalid_keyword = self.__get_keyword()
        m_uniary_tfidf_score = self.__get_tfidf_score(m_correct_keyword, m_incorrect_keyword, len(m_correct_keyword) + len(m_incorrect_keyword))
        m_binary_tfidf_score = self.__get_tfidf_binary_score()
        m_validity_score = self.__get_validity_score(m_correct_keyword + m_incorrect_keyword)
        m_content_type = self.__get_content_type(m_correct_keyword)
        m_sub_url, m_images, m_doc, m_vid = self.__get_static_file()

        return m_title, m_description, m_correct_keyword, m_incorrect_keyword, m_uniary_tfidf_score, m_binary_tfidf_score, m_validity_score,m_content_type,  m_sub_url, m_images, m_doc, m_vid
