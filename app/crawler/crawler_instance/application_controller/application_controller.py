import warnings
from abc import ABC
from crawler.constants.strings import MANAGE_CRAWLER_MESSAGES
from crawler.crawler_instance.application_controller.application_enums import APPICATION_COMMANDS
from crawler.crawler_instance.crawl_controller.crawl_enums import CRAWL_CONTROLLER_COMMANDS
from crawler.crawler_instance.crawl_controller.crawl_controller import crawl_controller
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler
warnings.filterwarnings("ignore", category=DeprecationWarning)


class application_controller(request_handler, ABC):
    __instance = None
    __m_crawl_controller = None

    # Initializations
    @staticmethod
    def get_instance():
        if application_controller.__instance is None:
            application_controller()
        return application_controller.__instance

    def __init__(self):
        if application_controller.__instance is not None:
            raise Exception(MANAGE_CRAWLER_MESSAGES.S_SINGLETON_EXCEPTION)
        else:
            self.__m_crawl_controller = crawl_controller()
            application_controller.__instance = self

    def __initializations(self):
        pass

    # External Reuqest Callbacks
    def __on_start(self):
        log.g().i(MANAGE_CRAWLER_MESSAGES.S_APPLICATION_STARTING)
        self.__initializations()
        self.__m_crawl_controller.invoke_trigger(CRAWL_CONTROLLER_COMMANDS.S_RUN_CRAWLER)

    # External Reuqest Manager
    def invoke_triggers(self, p_command):
        if p_command == APPICATION_COMMANDS.S_START_APPLICATION_DIRECT:
            return self.__on_start()

        elif p_command == APPICATION_COMMANDS.S_START_APPLICATION_DOCKERISED:
            return self.__on_start()
