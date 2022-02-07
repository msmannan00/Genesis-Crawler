# Local Imports
from crawler.crawler_services.helper_services.duplication_handler import duplication_handler


class url_duplication_controller:

    __instance = None
    __m_duplication_content_handler = None
    __m_parsed = {}

    # Initializations

    def __init__(self):
        url_duplication_controller.__instance = self
        self.__m_duplication_content_handler = duplication_handler()

    @staticmethod
    def get_instance():
        if url_duplication_controller.__instance is None:
            url_duplication_controller()
        return url_duplication_controller.__instance

    def verify_content_duplication(self, p_url):
        if self.__m_duplication_content_handler.validate_duplicate(p_url) is False:
            return False
        else:
            return True

    def on_insert_content(self, p_url):
        self.__m_duplication_content_handler.insert(p_url)

    def on_set_parsed_content(self, p_url, p_state):
        self.__m_parsed[p_url] = p_state

    def on_get_parsed_content(self, p_url):
        return self.__m_parsed[p_url]

    def on_reset(self):
        self.__m_duplication_content_handler.clear_filter()
        self.__m_parsed.clear()

    def clear_filter(self):
        self.__m_duplication_content_handler.clear_filter()
        self.__m_parsed.clear()
