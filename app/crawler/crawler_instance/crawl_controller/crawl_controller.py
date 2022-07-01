# Local Imports

import schedule
from eventlet import sleep

from raven.transport import requests

from crawler.constants.app_status import APP_STATUS
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.crawler_instance.crawl_controller.crawl_enums import CRAWL_CONTROLLER_COMMANDS, CRAWL_MODEL_COMMANDS
from crawler.crawler_instance.crawl_controller.crawl_model import crawl_model
from crawler.crawler_instance.tor_controller.tor_enums import TOR_STATUS
from crawler.crawler_services.helper_services.scheduler import RepeatedTimer
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler


class crawl_controller(request_handler):

    # Local Variables
    __m_crawl_model = None

    # Initializations
    def __init__(self):
        self.__m_crawl_model = crawl_model()

    def __update_status(self):
        requests.get(CRAWL_SETTINGS_CONSTANTS.S_UPDATE_STATUS_URL, timeout=100)

    def __wait_for_tor(self):

        while APP_STATUS.S_TOR_STATUS != TOR_STATUS.S_RUNNING:
            sleep(10)
            continue

    def __on_start(self):
        RepeatedTimer(CRAWL_SETTINGS_CONSTANTS.S_UPDATE_STATUS_TIMEOUT, self.__update_status)
        self.__wait_for_tor()
        self.__m_crawl_model.invoke_trigger(CRAWL_MODEL_COMMANDS.S_INIT)

    def invoke_trigger(self, p_command, p_data=None):
        if p_command == CRAWL_CONTROLLER_COMMANDS.S_RUN_CRAWLER:
            self.__on_start()

