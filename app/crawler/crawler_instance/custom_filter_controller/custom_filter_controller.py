from eventlet.hubs import threading
from crawler.constants.strings import MANAGE_CRAWLER_MESSAGES

class custom_filter_controller:
    __instance = None
    __S_CUSTOM_FILTER_HASH = set()
    lock = threading.Lock()

    # Initializations
    @staticmethod
    def get_instance():
        if custom_filter_controller.__instance is None:
            custom_filter_controller()
        return custom_filter_controller.__instance

    def __init__(self):
        if custom_filter_controller.__instance is not None:
            raise Exception(MANAGE_CRAWLER_MESSAGES.S_SINGLETON_EXCEPTION)
        else:
            custom_filter_controller.__instance = self

    def init_filter(self):
        with open("filtered_url.txt", 'r') as file:
            for line in file:
                self.__S_CUSTOM_FILTER_HASH.add(line.strip())
                print(line.strip())

    def validate_custom_html_filter(self, p_html, m_validity_score):
        return m_validity_score

    def write_data(self, p_url):
        if p_url not in self.__S_CUSTOM_FILTER_HASH:
            self.__S_CUSTOM_FILTER_HASH.add(p_url)
            file_path = './filtered_url.txt'
            with self.lock:
                with open(file_path, 'a') as file:
                    file.write(p_url + '\n')
