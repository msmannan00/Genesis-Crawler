# Local Imports
import nltk
from nltk.corpus import stopwords
from CrawlerInstance.constants import constants
from GenesisCrawlerServices.constants import strings

# English Spell Check Handler
from GenesisCrawlerServices.constants.enums import ErrorMessages
nltk.download('stopwords')
nltk.download('punkt')

class SpellCheckHandler:
    __instance = None
    spell_check = None
    nltk_stopwords = None

    # Initializations
    @staticmethod
    def getInstance():
        if SpellCheckHandler.__instance is None:
            SpellCheckHandler()
        return SpellCheckHandler.__instance

    def __init__(self):
        if SpellCheckHandler.__instance is not None:
            raise Exception(ErrorMessages.singleton_exception)
        else:
            self.spell_check = set(open(constants.m_dict_path).read().split())
            SpellCheckHandler.__instance = self
            self.nltk_stopwords = stopwords.words(strings.stopword_language)

    def initDict(self):
        self.spell_check = set(open(constants.m_dict_small_path).read().split())

    # List Word Validator - Divides the list into 2 list of valid and invalid words
    def validationHandler(self, p_word_list):
        invalid = []
        valid = []

        if len(p_word_list) > 1:
            for word in set(p_word_list):
                if word not in strings.stop_words:
                    if word in self.spell_check and word not in valid:
                        valid.append(word)
                    elif word not in invalid:
                        invalid.append(word)
            return list(invalid), list(valid)
        else:
            return p_word_list,p_word_list

    # List Word Validator - Divides the list into 2 list of valid and invalid words along with stopwords if any
    def invalidValidationHandler(self, p_word_list):
        invalid = []
        valid = []
        m_is_stop_word = False

        for word in p_word_list:
            if word not in strings.stop_words:
                if word in self.spell_check and word not in valid:
                    valid.append(word)
                elif word not in invalid and not word.isnumeric():
                    invalid.append(word)
            else:
                m_is_stop_word = True
        return list(invalid), list(valid), m_is_stop_word

    # Calculates the probability of sentence validity
    def sentenceValidator(self, p_sentence):
        m_valid_count = 0
        m_invalid_count = 0
        m_sentence_list = p_sentence.split()
        for word in m_sentence_list:
            if word in strings.stop_words or word in self.spell_check:
                m_valid_count += 1
            else:
                m_invalid_count += 1

        if m_valid_count > 0 and m_valid_count/(m_valid_count+m_invalid_count) > 0.60:
            return True
        else:
            return False
