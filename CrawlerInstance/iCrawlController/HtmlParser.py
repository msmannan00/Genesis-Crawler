# Local Imports
import json
from abc import ABC
from html.parser import HTMLParser
from bs4 import BeautifulSoup

from CrawlerInstance.classModels.IndexModel import UrlObjectEncoder
from CrawlerInstance.classModels.TFModel import TFModel
from CrawlerInstance.constants import constants
from CrawlerInstance.logManager.LogManager import log
from GenesisCrawlerServices.constants import strings
from GenesisCrawlerServices.constants.enums import ParserTags, CrawlURLIntensity
from GenesisCrawlerServices.helperService.HelperMethod import HelperMethod
from GenesisCrawlerServices.helperService.SpellCheckHandler import SpellCheckHandler
import pathlib
import requests
import nltk as nltk
import re
import mimetypes
import validators


# class to parse html raw duplicationHandlerService
class HtmlParser(HTMLParser, ABC):

    def __init__(self, m_base_url, m_html):
        super().__init__()
        self.title = strings.empty
        self.desc = strings.empty
        self.keywords = strings.empty
        self.m_html = m_html
        self.m_content_type = "General"
        self.sub_url = []
        self.image_URL = []
        self.doc_URL = []
        self.vid_URL = []
        self.rec = ParserTags.none
        self.m_base_url = m_base_url
        self.m_total_keywords = 0

    # find url type and populate the list respectively
    def insertURL(self, p_url):
        if p_url is not None and not str(p_url).__contains__("#"):
            mime = mimetypes.MimeTypes().guess_type(p_url)[0]
            if len(p_url) <= constants.m_max_url_size:

                # Joining Relative URL
                if not p_url.startswith("https://") and not p_url.startswith("http://") and not p_url.startswith(
                        "ftp://"):
                    m_temp_base_url = self.m_base_url
                    if not m_temp_base_url.endswith("/"):
                        m_temp_base_url = m_temp_base_url + "/"
                    p_url = requests.compat.urljoin(m_temp_base_url, p_url)
                    p_url = p_url.replace(" ", "%20")
                    p_url = HelperMethod.cleanURL(HelperMethod.normalize_slashes(p_url))

                if validators.url(p_url):
                    suffix = ''.join(pathlib.Path(p_url).suffixes)
                    if mime is None or mime == "text/html":
                        if suffix in constants.doc_types:
                            self.doc_URL.append(p_url)
                        elif str(mime).startswith("video"):
                            self.vid_URL.append(p_url)
                        else:
                            self.sub_url.append(p_url)
                        # elif str(mime).startswith("image"):
                        #     self.image_URL.append(m_url)

    # extract duplicationHandlerService by tags
    def handle_starttag(self, p_tag, p_attrs):
        if p_tag == "a":
            for name, value in p_attrs:
                if name == "href":
                    self.insertURL(value)

        if p_tag == 'img':
            for value in p_attrs:
                if value[0] == 'src' and not HelperMethod.isURLBase64(value[1]):
                    # Joining Relative URL
                    m_temp_base_url = self.m_base_url
                    if not m_temp_base_url.endswith("/"):
                        m_temp_base_url = m_temp_base_url + "/"
                    m_url = requests.compat.urljoin(m_temp_base_url, value[1])
                    m_url = HelperMethod.cleanURL(HelperMethod.normalize_slashes(m_url))
                    self.image_URL.append(m_url)

        elif p_tag == 'title':
            self.rec = ParserTags.title

        elif p_tag == 'h1':
            self.rec = ParserTags.header

        elif p_tag == 'p':
            self.rec = ParserTags.paragraph

        elif p_tag == 'meta':
            if p_attrs[0][1] == 'description':
                if len(p_attrs) > 1 and len(p_attrs[1]) > 0 and p_attrs[1][0] == 'content':
                    self.desc = p_attrs[1][1]
            elif p_attrs[0][1] == 'keywords':
                if len(p_attrs) > 1 and len(p_attrs[1]) > 0 and p_attrs[1][0] == 'content':
                    self.keywords = p_attrs[1][1].replace(",", " ")
        else:
            self.rec = ParserTags.none

    # error printing while parsing html
    def error(self, p_message):
        log.g().e(p_message)

    def handle_data(self, p_data):
        if self.rec == ParserTags.title:
            self.title = p_data
        if self.rec == ParserTags.header:
            self.desc = self.desc + " " + p_data
        elif self.rec == ParserTags.meta and len(self.title)>0:
            self.title = p_data
        elif self.rec == ParserTags.paragraph:
            self.desc = self.desc + " " + p_data

    def handle_endtag(self, p_tag):
        if p_tag == 'title' or p_tag == 'h1' or p_tag == 'p':
            self.rec = ParserTags.none

    # duplicationHandlerService Getters
    def getTitle(self):
        return ' '.join(self.title.split())

    # creating keyword model for webpage representation
    def setKeywordModel(self, p_valid_keywords, p_invalid_keywords):
        return p_valid_keywords, p_invalid_keywords

    # extract relavent keywords from html for its representation
    def getKeyword(self):

        m_valid_keywords_model, m_invalid_keywords_model = self.text_preprocessing(self.keywords)
        m_valid_keywords_model_filtered_1, m_invalid_keywords_model_filtered_1 = self.setKeywordModel(m_valid_keywords_model, m_invalid_keywords_model)

        m_valid_keywords_model, m_invalid_keywords_model = self.text_preprocessing(self.title)
        m_valid_keywords_model_filtered_2, m_invalid_keywords_model_filtered_2 = self.setKeywordModel(m_valid_keywords_model, m_invalid_keywords_model)

        m_valid_keywords_model, m_invalid_keywords_model = self.text_preprocessing(self.desc)
        m_valid_keywords_model_filtered_3, m_invalid_keywords_model_filtered_3 = self.setKeywordModel(m_valid_keywords_model, m_invalid_keywords_model)

        m_valid_keywords_model, m_invalid_keywords_model = self.text_preprocessing(self.getText())
        m_valid_keywords_model_filtered_4, m_invalid_keywords_model_filtered_4 = self.setKeywordModel(m_valid_keywords_model, m_invalid_keywords_model)

        return (m_valid_keywords_model_filtered_1 + m_valid_keywords_model_filtered_2 +
                m_valid_keywords_model_filtered_3 + m_valid_keywords_model_filtered_4), \
                m_invalid_keywords_model_filtered_2

    # extract local inbound and outbound url
    def getSubURL(self, p_html):
        m_allowed_tokens = constants.m_filter_token.split(",")

        if constants.m_filter_catagory == "General" and ((constants.m_filter_catagory == "hard" and (any(x in self.title for x in m_allowed_tokens)) or (any(x in self.desc for x in m_allowed_tokens)) and (constants.m_filter_catagory == "soft" and (any(x in self.getText() for x in m_allowed_tokens))))) or self.m_content_type is constants.m_filter_catagory or ((constants.m_filter_catagory == "hard" and (any(x in self.title for x in m_allowed_tokens)) or (any(x in self.desc for x in m_allowed_tokens)) or (constants.m_filter_catagory == "soft" and (any(x in self.getText() for x in m_allowed_tokens))))):
            if constants.m_crawling_url_intensity == CrawlURLIntensity.high.value:
                sub_url = re.findall(r'(?:https?://)?(?:www)?\S*?\.onion\S*', p_html)
                for m_url in sub_url:
                    m_url = HelperMethod.appendProtocol(m_url)
                    m_url = m_url.replace("/<br>", "")
                    if validators.url(m_url):
                        self.insertURL(m_url)
        return self.sub_url

    # extract website description from raw duplicationHandlerService
    def getDescription(self):
        sentences = nltk.sent_tokenize(self.getText())
        sentences_joined = ""
        for sentence in sentences[2:]:
            m_is_sentence_valid = SpellCheckHandler.getInstance().sentenceValidator(sentence)
            if m_is_sentence_valid:
                sentences_joined = sentences_joined + " " + sentence

        if len(self.desc) < 450 and len(sentences_joined) > 10:
            if len(self.desc) > 5:
                self.desc = self.desc + ". " + sentences_joined
            else:
                self.desc = sentences_joined

        clean_description = self.clearDescription(self.desc)
        return clean_description

    # give validity score to identify if website is worth showing to user
    def getValidityScore(self, p_keyword):
        m_rank = (len(p_keyword) > 10) * 10 + (len(self.sub_url) > 0) * 5
        return m_rank

    # give illegal rank to website content in order to show warning to user
    def getIllegalContentClassifier(self, p_illegal_content_classifier):
        pass

    def getContentType(self):
        return  self.m_content_type

    # extract text from raw html
    def getText(self):
        m_soup = BeautifulSoup(self.m_html, "html.parser")
        m_text = m_soup.get_text(separator=u' ')

        m_text = m_text.replace('\n', ' ')
        m_text = m_text.replace('\t', ' ')
        m_text = m_text.replace('\r', ' ')
        m_text = re.sub(' +', ' ', m_text)
        return m_text

    # --------------- Text Preprocessing --------------- #

    def clearDescription(self, p_desc):
        p_desc = p_desc.lower().strip("_+\n\r!@#|$?^\'\"~ #$%&*(\>.< ")
        return p_desc[0:500]

    def incorrect_word_cleaner(self, p_words):
        p_words = re.sub('[^A-Za-z0-9]+', ' ', p_words)
        m_word_list = p_words.split()

        return SpellCheckHandler.getInstance().invalidValidationHandler(m_word_list)

    def is_incorrect_word_validity_checker(self, p_word):

        non_alpha_character = len(re.findall(r'[^a-zA-Z ]', p_word))
        alpha_character = len(p_word) - non_alpha_character

        if len(p_word) > 3 and len(p_word) < 20 and bool(re.search(r'[a-zA-Z].*', p_word)) is True and \
                '.onion' not in p_word and 'http' not in p_word and \
                (alpha_character / (alpha_character + non_alpha_character)) > 0.7:
            return True
        else:
            return False

    def getTFIDFModel(self, p_correct_keyword, p_incorrect_keyword):
        m_doc_collection = []
        m_text = self.getText()
        for m_word in set(p_correct_keyword):
            m_count = m_text.count(m_word)
            if m_count!=0:
                mTFIDF = TFModel(m_word, format(m_count / self.m_total_keywords))
                m_doc_collection.append(mTFIDF)

                for m_bi_word in p_correct_keyword:
                    m_bi_count = m_text.count(m_word + " " + m_bi_word)
                    if m_bi_count!=0:
                        mTFIDF.setBigram(float(m_bi_count / (m_count / 2)), m_bi_word)
                        mTFIDF.m_bigram = json.loads(UrlObjectEncoder().encode(mTFIDF.m_bigram))

        for m_word in set(p_incorrect_keyword):
            m_count = m_text.count(m_word)
            if m_count!=0:
                mTFIDF = TFModel(m_word, format(m_count / self.m_total_keywords))
                m_doc_collection.append(mTFIDF)
                for m_bi_word in p_correct_keyword:
                    m_bi_count = m_text.count(m_word + " " + m_bi_word)
                    if m_bi_count!=0:
                        mTFIDF.setBigram(float(m_bi_count / (m_count / 2)), m_bi_word)
                        mTFIDF.m_bigram = json.loads(UrlObjectEncoder().encode(mTFIDF.m_bigram))

        return m_doc_collection

    def getBigram(self, mWord):
        mBigramList = []

        return []

    def text_preprocessing(self, p_text):

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
        incorrect_word, correct_word = SpellCheckHandler.getInstance().validationHandler(word_list)

        # Cleaning Incorrect Words
        incorrect_word_cleaned = []
        for inc_word in incorrect_word:
            incorrect_word_filter, correct_word_filter, m_is_stop_word = self.incorrect_word_cleaner(inc_word)
            if len(correct_word_filter) > 0 and len(correct_word_filter) + 1 >= len(incorrect_word_filter):
                correct_word = correct_word + correct_word_filter
            elif self.is_incorrect_word_validity_checker(inc_word) and not (m_is_stop_word is True and len(incorrect_word_filter) <= 1):
                incorrect_word_cleaned.append(inc_word)

        # Remove Special Character
        word_list = [re.sub('[^a-zA-Z0-9]+', '', _) for _ in incorrect_word_cleaned]
        incorrect_word_cleaned = list(filter(None, word_list))

        # if len(correct_word)>0:
        #     self.m_content_type = topicClassifier.getInstance().predictClassifier(" ".join(correct_word))
        correct_word = list(set(correct_word))

        return correct_word, incorrect_word_cleaned
