# Local Imports
from crawler.crawler_services.helper_services.duplication_handler import duplication_handler


class content_duplication_controller:

    __instance = None
    __m_duplication_content_handler = None
    __m_parsed = {}

    # Initializations

    def __init__(self):
        content_duplication_controller.__instance = self
        self.__m_duplication_content_handler = duplication_handler()

    @staticmethod
    def get_instance():
        if content_duplication_controller.__instance is None:
            content_duplication_controller()
        return content_duplication_controller.__instance

    def verify_content_duplication(self, p_text):
        if self.__m_duplication_content_handler.validate_duplicate(p_text) is False:
            return False
        else:
            return True

    def on_insert_content(self, p_text):
        self.__m_duplication_content_handler.insert(p_text)
