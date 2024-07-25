import re
import nltk
from nltk import PorterStemmer
from crawler.constants.constant import SPELL_CHECK_CONSTANTS
from crawler.constants.strings import MANAGE_CRAWLER_MESSAGES, STRINGS
from crawler.crawler_instance.helper_services.helper_method import helper_method

# Precompile regular expressions and nltk download
NON_ALPHANUMERIC_REGEXP = re.compile('[^A-Za-z0-9]+')
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class spell_checker_handler:
    __instance = None

    @staticmethod
    def get_instance():
        if spell_checker_handler.__instance is None:
            spell_checker_handler.__instance = spell_checker_handler()
        return spell_checker_handler.__instance

    def __init__(self):
        if spell_checker_handler.__instance is not None:
            raise Exception(MANAGE_CRAWLER_MESSAGES.S_SINGLETON_EXCEPTION)
        self.spell_check = set(open(SPELL_CHECK_CONSTANTS.S_DICTIONARY_PATH).read().split())
        self.porter_stemmer = PorterStemmer()

    def load_mini_dict(self):
        self.spell_check = set(open(SPELL_CHECK_CONSTANTS.S_DICTIONARY_MINI_PATH).read().split())

    def validate_word(self, word):
        return word in self.spell_check

    def clean_sentence(self, text):
        text = NON_ALPHANUMERIC_REGEXP.sub(' ', text)
        tokens = nltk.word_tokenize(text)
        cleaned_text = STRINGS.S_EMPTY

        for token in tokens:
            if not helper_method.is_stop_word(token) and self.validate_word(token):
                cleaned_text += " " + token

        return cleaned_text.strip()

    def clean_paragraph(self, text):
        sentences = nltk.sent_tokenize(text)
        cleaned_sentences = []

        for sentence in sentences:
            words = sentence.lower().split()
            valid_count = sum(1 for word in words if helper_method.is_stop_word(word) or self.validate_word(word))
            total_count = len(words)

            if total_count > 0 and valid_count / total_count >= 0.60:
                cleaned_sentences.append(sentence)

        return " - ".join(cleaned_sentences)
