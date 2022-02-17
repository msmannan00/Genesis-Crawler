import threading

from time import sleep
from raven.transport import requests
from crawler.crawler_instance.constants.strings import ERROR_MESSAGES
from crawler.crawler_instance.crawl_controller.crawl_enums import NETWORK_STATUS


class network_monitor:
    __instance = None
    __m_running = False

    # Initializations
    @staticmethod
    def get_instance():
        if network_monitor.__instance is None:
            network_monitor()
        return network_monitor.__instance

    def __init__(self):
        if network_monitor.__instance is not None:
            raise Exception(ERROR_MESSAGES.S_SINGLETON_EXCEPTION)
        else:
            network_monitor.__instance = self

    def __start_monitoring(self):
        try:
            while True:
                url = "https://www.google.com"
                timeout = 5
                try:
                    requests.head(url, timeout=timeout)
                    self.__m_running = True
                except:
                    self.__m_running = False
                sleep(60)
        except KeyboardInterrupt:
            pass

    def init(self):
        thread_instance = threading.Thread(target=self.__start_monitoring,args=())
        thread_instance.start()

    def get_network_status(self):
        if self.__m_running:
            return NETWORK_STATUS.S_ONLINE
        else :
            return NETWORK_STATUS.S_OUTAGE

