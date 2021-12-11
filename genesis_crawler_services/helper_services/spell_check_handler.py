# Local Imports
import re
import nltk

from nltk.corpus import stopwords
from crawler_instance.constants.strings import GENERIC_STRINGS
from crawler_instance.log_manager.log_enums import ERROR_MESSAGES
from genesis_crawler_services.constants.constant import spell_check_constants
from genesis_crawler_services.helper_services.helper_method import helper_method

nltk.download('stopwords')
nltk.download('punkt')

class spell_checker_handler:
    __instance = None
    __spell_check = None
    __nltk_stopwords = None

    # Initializations
    @staticmethod
    def get_instance():
        if spell_checker_handler.__instance is None:
            spell_checker_handler()
        return spell_checker_handler.__instance

    def __init__(self):
        if spell_checker_handler.__instance is not None:
            raise Exception(ERROR_MESSAGES.S_SINGLETON_EXCEPTION)
        else:
            self.__spell_check = set(open(spell_check_constants.S_DICTIONARY_PATH).read().split())
            spell_checker_handler.__instance = self
            self.__nltk_stopwords = stopwords.words(spell_check_constants.S_SPELL_CHECK_LANGUAGE)

    def init_dict(self):
        self.__spell_check = set(open(spell_check_constants.S_DICTIONARY_MINI_PATH).read().split())

    # List Word Validator - Divides the list into 2 list of valid and invalid words
    def validation_handler(self, p_word_list):
        invalid = []
        valid = []

        if len(p_word_list) > 1:
            for word in set(p_word_list):
                if helper_method.is_stop_word(word) is False:
                    if word in self.__spell_check and word not in valid:
                        valid.append(word)
                    elif word not in invalid:
                        invalid.append(word)
            return list(invalid), list(valid)
        else:
            return p_word_list,p_word_list

    def binary_validation_handler(self, p_word_list):
        m_tokens = []
        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')

        if len(p_word_list) > 1:
            for word in p_word_list:
                if helper_method.is_stop_word(word) is False and word.isnumeric() is False and len(word)<11 and regex.search(word) is None and len(re.sub("[^0-9]", "", word)) < 3:
                    m_tokens.append(word)
        return m_tokens

    # List Word Validator - Divides the list into 2 list of valid and invalid words along with stopwords if any
    def invalid_validation_handler(self, p_word):
        p_words = re.sub('[^A-Za-z0-9]+', ' ', p_word)
        m_word_list = p_words.split()
        invalid = []
        valid = []

        for word in m_word_list:
            if helper_method.is_stop_word(word) is False:
                if word in self.__spell_check and word not in valid:
                    valid.append(word)
                elif word not in invalid and not word.isnumeric():
                    invalid.append(word)
        return list(invalid), list(valid)

    def incorrect_word_validator(self, p_word):
        non_alpha_character = len(re.findall(r'[^a-zA-Z ]', p_word))
        alpha_character = len(p_word) - non_alpha_character

        if 3 < len(p_word) < 20 and bool(re.search(r'[a-zA-Z].*', p_word)) is True and '.onion' not in p_word and 'http' not in p_word and (alpha_character / (alpha_character + non_alpha_character)) > 0.7:
            return True
        else:
            return False

    # Calculates the probability of sentence validity
    def sentence_validator(self, p_sentence):
        p_sentence = p_sentence.lower()
        m_valid_count = 0
        m_invalid_count = 0
        m_sentence_list = p_sentence.split()
        for word in m_sentence_list:
            if helper_method.is_stop_word(word) is True or word in self.__spell_check:
                m_valid_count += 1
            else:
                m_invalid_count += 1

        if m_valid_count > 0 and m_valid_count/(m_valid_count+m_invalid_count) >= 0.60:
            return True
        else:
            return False

    def extract_valid_validator(self, p_sentence):
        sentences = nltk.sent_tokenize(p_sentence)
        for sentence in sentences:
            m_is_sentence_valid = self.sentence_validator(sentence)
            if m_is_sentence_valid:
                return " - " + sentence
        return GENERIC_STRINGS.S_EMPTY
