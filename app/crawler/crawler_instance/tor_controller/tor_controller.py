# Local Imports
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from crawler.constants.app_status import APP_STATUS
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.constants.keys import TOR_KEYS
from crawler.crawler_instance.application_controller.application_enums import APPICATION_COMMANDS
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS, TOR_PROXIES
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler


class tor_controller(request_handler):
    __instance = None

    # Initializations
    @staticmethod
    def get_instance():
        if tor_controller.__instance is None:
            tor_controller()
        return tor_controller.__instance

    def __init__(self):
        tor_controller.__instance = self
        self.m_queue_index = 0

    # Tor Helper Methods
    def __on_create_session(self, p_tor_based):
        m_request_handler = requests.Session()
        retries = Retry(total=1, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        m_request_handler.mount("http://", HTTPAdapter(max_retries=retries))

        if p_tor_based:
            headers = {
                TOR_KEYS.S_USER_AGENT: CRAWL_SETTINGS_CONSTANTS.S_USER_AGENT,
            }
        else:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
            }
        return m_request_handler, headers

    def __on_proxy(self):
        if not APP_STATUS.DOCKERIZED_RUN:
            return {
                "http": "socks5h://127.0.0.1:" + "9150",
                "https": "socks5h://127.0.0.1:" + "9150"
            }, 100
        else:
            self.m_queue_index += 1
            return TOR_PROXIES[self.m_queue_index % len(TOR_PROXIES)], self.m_queue_index % len(TOR_PROXIES)

    # Request Triggers
    def invoke_trigger(self, p_command, p_data=None):
        if p_command is TOR_COMMANDS.S_CREATE_SESSION:
            return self.__on_create_session(p_data[0])
        elif p_command is TOR_COMMANDS.S_PROXY:
            return self.__on_proxy()
