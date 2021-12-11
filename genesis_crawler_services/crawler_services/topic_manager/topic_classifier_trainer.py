from genesis_crawler_services.constants.strings import generic_strings
from genesis_crawler_services.crawler_services.topic_manager.topic_classifier_enums import TOPIC_CLASSFIER_TRAINER
from genesis_crawler_services.helper_services.spell_check_handler import spell_checker_handler
from genesis_crawler_services.shared_model.request_handler import request_handler


class topic_classifier_trainer(request_handler):

    def __init__(self):
        pass

    def __clean_data(self, p_text):
        # New Line and Tab Remover
        p_text = p_text.replace('\\n', generic_strings.S_SPACE)
        p_text = p_text.replace('\\t', generic_strings.S_SPACE)
        p_text = p_text.replace('\\r', generic_strings.S_SPACE)

        # Tokenizer
        word_list = p_text.split()

        # Lower Case
        word_list = [x.lower() for x in word_list]

        # Word Checking
        incorrect_word, correct_word = spell_checker_handler.get_instance().validation_handler(word_list)

        if len(correct_word)>3:
            return generic_strings.S_SPACE.join(correct_word)
        else:
            return generic_strings.S_SPACE.join(correct_word)

    def invoke_trigger(self, p_command, p_data=None):
        if p_command == TOPIC_CLASSFIER_TRAINER.S_CLEAN_DATA:
            return self.__clean_data(p_data[0])
