# Local Imports
import nltk
from nltk.corpus import stopwords
from CrawlerInstance.constants import constants
from GenesisCrawlerServices.constants import strings

# English Spell Check Handler
from GenesisCrawlerServices.constants.enums import ERROR_MESSAGES
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
            self.__spell_check = set(open(constants.S_DICTIONARY_PATH).read().split())
            spell_checker_handler.__instance = self
            self.__nltk_stopwords = stopwords.words(strings.S_STOPWORD_LANGUAGE)

    def init_dict(self):
        self.__spell_check = set(open(constants.S_DICTIONARY_MINI_PATH).read().split())

    # List Word Validator - Divides the list into 2 list of valid and invalid words
    def validation_handler(self, p_word_list):
        invalid = []
        valid = []

        if len(p_word_list) > 1:
            for word in set(p_word_list):
                if word not in strings.S_STOPWORDS:
                    if word in self.__spell_check and word not in valid:
                        valid.append(word)
                    elif word not in invalid:
                        invalid.append(word)
            return list(invalid), list(valid)
        else:
            return p_word_list,p_word_list

    # List Word Validator - Divides the list into 2 list of valid and invalid words along with stopwords if any
    def invalid_validation_handler(self, p_word_list):
        invalid = []
        valid = []
        m_is_stop_word = False

        for word in p_word_list:
            if word not in strings.S_STOPWORDS:
                if word in self.__spell_check and word not in valid:
                    valid.append(word)
                elif word not in invalid and not word.isnumeric():
                    invalid.append(word)
            else:
                m_is_stop_word = True
        return list(invalid), list(valid), m_is_stop_word

    # Calculates the probability of sentence validity
    def sentence_validator(self, p_sentence):
        p_sentence = p_sentence.lower()
        m_valid_count = 0
        m_invalid_count = 0
        m_sentence_list = p_sentence.split()
        for word in m_sentence_list:
            if word in strings.S_STOPWORDS or word in self.__spell_check:
                m_valid_count += 1
            else:
                m_invalid_count += 1

        if m_valid_count > 0 and m_valid_count/(m_valid_count+m_invalid_count) >= 0.60:
            return True
        else:
            return False
