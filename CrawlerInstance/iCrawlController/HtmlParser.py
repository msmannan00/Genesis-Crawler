# Local Imports

from abc import ABC
from html.parser import HTMLParser

import nltk
from bs4 import BeautifulSoup
from CrawlerInstance.constants import constants
from GenesisCrawlerServices.constants import strings
from GenesisCrawlerServices.constants.enums import PARSE_TAGS
from GenesisCrawlerServices.helperServices.helperMethod import helper_method
from GenesisCrawlerServices.helperServices.spellCheckerHandler import spell_checker_handler

import pathlib
import requests
import re
import mimetypes
import validators


# class to parse html raw duplicationHandlerService
class htmlParser(HTMLParser, ABC):

    def __init__(self, m_base_url, m_html):
        super().__init__()
        self.m_title = strings.S_EMPTY
        self.m_description = strings.S_EMPTY
        self.m_keywords = strings.S_EMPTY
        self.m_html = m_html
        self.m_content_type = "General"
        self.m_sub_url = []
        self.m_image_url = []
        self.m_doc_url = []
        self.m_video_url = []
        self.m_base_url = m_base_url
        self.m_total_keywords = 0

        self.rec = PARSE_TAGS.S_NONE
        self.m_paragraph_count = 0

    # find url type and populate the list respectively
    def __insert_external_url(self, p_url):
        if  1==1: # HelperMethod.getHostURL(p_url).__contains__(".onion") and len(HelperMethod.getHostURL(p_url))>60)
            if p_url is not None and not str(p_url).__contains__("#"):
                mime = mimetypes.MimeTypes().guess_type(p_url)[0]
                if len(p_url) <= constants.S_MAX_URL_SIZE:

                    # Joining Relative URL
                    if not p_url.startswith("https://") and not p_url.startswith("http://") and not p_url.startswith(
                            "ftp://"):
                        m_temp_base_url = self.m_base_url
                        if not m_temp_base_url.endswith("/"):
                            m_temp_base_url = m_temp_base_url + "/"
                        p_url = requests.compat.urljoin(m_temp_base_url, p_url)
                        p_url = p_url.replace(" ", "%20")
                        p_url = helper_method.on_clean_url(helper_method.normalize_slashes(p_url))

                    if validators.url(p_url):
                        suffix = ''.join(pathlib.Path(p_url).suffixes)
                        if mime is None or mime == "text/html":
                            if suffix in constants.S_DOC_TYPES and len(self.m_image_url)<20:
                                self.m_doc_url.append(p_url)
                            elif str(mime).startswith("video") and len(self.m_video_url)<20:
                                self.m_video_url.append(p_url)
                            else:
                                self.m_sub_url.append(p_url)

    # extract duplicationHandlerService by tags
    def handle_starttag(self, p_tag, p_attrs):
        if p_tag == "a":
            for name, value in p_attrs:
                if name == "href":
                    self.__insert_external_url(value)

        if p_tag == 'img':
            for value in p_attrs:
                if value[0] == 'src' and not helper_method.is_url_base_64(value[1]) and len(self.m_image_url)<20:
                    # Joining Relative URL
                    m_temp_base_url = self.m_base_url
                    if not m_temp_base_url.endswith("/"):
                        m_temp_base_url = m_temp_base_url + "/"
                    m_url = requests.compat.urljoin(m_temp_base_url, value[1])
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
                    if len(p_attrs) > 1 and len(p_attrs[1]) > 0 and p_attrs[1][0] == 'content' and p_attrs[1][1] is not None:
                        self.m_description = p_attrs[1][1]
                elif p_attrs[0][1] == 'keywords':
                    if len(p_attrs) > 1 and len(p_attrs[1]) > 0 and p_attrs[1][0] == 'content' and p_attrs[1][1] is not None:
                        self.m_keywords = p_attrs[1][1].replace(",", " ")
            except Exception:
                pass
        else:
            self.rec = PARSE_TAGS.S_NONE

    def handle_data(self, p_data):
        if self.rec == PARSE_TAGS.S_HEADER:
            self.m_description = self.m_description + self.__get_validated_sentence(p_data)
        if self.rec == PARSE_TAGS.S_TITLE:
            self.m_title = p_data
        elif self.rec == PARSE_TAGS.S_META and len(self.m_title)>0:
            self.m_title = p_data
        elif self.rec == PARSE_TAGS.S_PARAGRAPH: #  and self.m_paragraph_count <4:
            self.m_description = self.m_description + self.__get_validated_sentence(p_data)
            self.m_paragraph_count+=1

    def __get_validated_sentence(self, p_sentence):
        sentences = nltk.sent_tokenize(self.__strip_special_character(p_sentence))
        for sentence in sentences:
            m_is_sentence_valid = spell_checker_handler.get_instance().sentence_validator(sentence)
            if m_is_sentence_valid:
                return " - " + sentence
        return strings.S_EMPTY

    # creating keyword sharedModel for webpage representation
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

    def __strip_special_character(self, p_desc):
        p_desc = re.sub('[^A-Za-z0-9 @#_+-]+', '', p_desc)
        p_desc = re.sub(' +', ' ', p_desc)
        return p_desc

    def __word_cleaner(self, p_words):
        p_words = re.sub('[^A-Za-z0-9]+', ' ', p_words)
        m_word_list = p_words.split()

        return spell_checker_handler.get_instance().invalid_validation_handler(m_word_list)

    def __word_validity_checker(self, p_word):

        non_alpha_character = len(re.findall(r'[^a-zA-Z ]', p_word))
        alpha_character = len(p_word) - non_alpha_character

        if 3 < len(p_word) < 20 and bool(re.search(r'[a-zA-Z].*', p_word)) is True and \
                '.onion' not in p_word and 'http' not in p_word and \
                (alpha_character / (alpha_character + non_alpha_character)) > 0.7:
            return True
        else:
            return False

    def __clean_html(self, m_query):
        m_query = re.sub('\W+', ' ', m_query)
        m_query = m_query.lower().split()

        m_range = 0
        for m_count in range(len(m_query)):
            if m_query[m_range] in strings.S_STOPWORDS:
                del m_query[m_range]
            else:
                m_range +=1

        return ' '.join(m_query)

    def __text_preprocessing(self, p_text):

        # New Line and Tab Remover
        p_text = ' '.join(p_text.split())
        p_text = p_text.replace('\\n', ' ')
        p_text = p_text.replace('\\t', ' ')
        p_text = p_text.replace('\\r', ' ')

        # Tokenizer
        word_list = p_text.split()

        # Lower Case
        word_list = [x.lower() for x in word_list]

        # Word Checking
        self.m_total_keywords = len(word_list)
        incorrect_word, correct_word = spell_checker_handler.get_instance().validation_handler(word_list)

        # Cleaning Incorrect Words
        incorrect_word_cleaned = []
        for inc_word in incorrect_word:
            incorrect_word_filter, correct_word_filter, m_is_stop_word = self.__word_cleaner(inc_word)
            if len(correct_word_filter) > 0 and len(correct_word_filter) + 1 >= len(incorrect_word_filter):
                correct_word = correct_word + correct_word_filter
            elif self.__word_validity_checker(inc_word) and not (m_is_stop_word is True and len(incorrect_word_filter) <= 1):
                incorrect_word_cleaned.append(inc_word)

        # Remove Special Character
        word_list = [re.sub('[^a-zA-Z0-9]+', '', _) for _ in incorrect_word_cleaned]
        incorrect_word_cleaned = list(filter(None, word_list))

        # if len(correct_word)>0:
        #     self.m_content_type = topic_classifier.get_instance().predict_classifier(" ".join(correct_word))
        correct_word = list(set(correct_word))

        return correct_word, incorrect_word_cleaned

    # ----------------- Data Recievers -----------------

    # duplicationHandlerService Getters
    def get_title(self):
        return self.__strip_special_character(self.m_title).strip()

    # extract relavent keywords from html for its representation
    def get_keyword(self):

        m_valid_keywords_model, m_invalid_keywords_model = self.__text_preprocessing(self.m_keywords)
        m_valid_keywords_model_filtered_1, m_invalid_keywords_model_filtered_1 = self.__set_keyword_model(m_valid_keywords_model, m_invalid_keywords_model)

        m_valid_keywords_model, m_invalid_keywords_model = self.__text_preprocessing(self.m_title)
        m_valid_keywords_model_filtered_2, m_invalid_keywords_model_filtered_2 = self.__set_keyword_model(m_valid_keywords_model, m_invalid_keywords_model)

        m_valid_keywords_model, m_invalid_keywords_model = self.__text_preprocessing(self.m_description)
        m_valid_keywords_model_filtered_3, m_invalid_keywords_model_filtered_3 = self.__set_keyword_model(m_valid_keywords_model, m_invalid_keywords_model)

        m_valid_keywords_model, m_invalid_keywords_model = self.__text_preprocessing(self.__get_html_text())
        m_valid_keywords_model_filtered_4, m_invalid_keywords_model_filtered_4 = self.__set_keyword_model(m_valid_keywords_model, m_invalid_keywords_model)

        return (m_valid_keywords_model_filtered_1 + m_valid_keywords_model_filtered_2 +
                m_valid_keywords_model_filtered_3 + m_valid_keywords_model_filtered_4), \
                m_invalid_keywords_model_filtered_2

    # extract local inbound and outbound url
    def get_sub_url(self):
        return self.m_sub_url

    # extract website description from raw duplicationHandlerService
    def get_description(self):
        clean_description = self.__strip_special_character(self.m_description)
        return clean_description

    # give validity score to identify if website is worth showing to user
    def get_validity_score(self, p_keyword):
        m_rank = (len(p_keyword) > 10) * 10 + (len(self.m_sub_url) > 0) * 5
        return m_rank

    def get_content_type(self):
        return  self.m_content_type

    def get_tfidf_score(self, p_correct_keyword, p_incorrect_keyword):
        m_doc_collection = {}
        m_text = self.__get_html_text()
        for m_word in set(p_correct_keyword):
            m_count = m_text.count(m_word)
            if m_count!=0 and m_word != 'language':
                m_doc_collection[m_word] = format(round(m_count / self.m_total_keywords, 3))

        for m_word in set(p_incorrect_keyword):
            m_count = m_text.count(m_word)
            if m_count!=0 and m_word != 'language':
                m_doc_collection[m_word] = format(round(m_count / self.m_total_keywords, 3))

        return m_doc_collection

    def get_tfidf_binary_score(self, p_correct_keyword, p_incorrect_keyword):
        m_doc_collection = {}
        m_text = self.__clean_html(self.__get_html_text())
        for m_word in set(p_correct_keyword):
            m_count = m_text.count(m_word)
            if m_count!=0 and m_word != 'language':

                for m_bi_word in p_correct_keyword:
                    m_bi_count = m_text.count(m_word + " " + m_bi_word)
                    if m_bi_count!=0 and m_bi_word!=m_word:
                        m_doc_collection[m_word + " " + m_bi_word] = float(round(m_bi_count / (m_count / 2), 3))


        for m_word in set(p_incorrect_keyword):
            m_count = m_text.count(m_word)
            if m_count!=0 and m_word != 'language':

                for m_bi_word in p_correct_keyword:
                    m_bi_count = m_text.count(m_word + " " + m_bi_word)
                    if m_bi_count!=0 and m_bi_word!=m_word:
                        m_doc_collection[m_word + " " + m_bi_word] = float(round(m_bi_count / (m_count / 2), 3))

        return m_doc_collection
