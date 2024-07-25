import sys
from abc import ABC
from crawler.constants.strings import MANAGE_CRAWLER_MESSAGES
from crawler.crawler_instance.application_controller.application_enums import APPICATION_COMMANDS
from crawler.crawler_instance.crawl_controller.crawl_enums import CRAWL_CONTROLLER_COMMANDS
from crawler.crawler_instance.custom_filter_controller.custom_filter_controller import custom_filter_controller
from crawler.crawler_services.crawler_services.topic_manager.topic_classifier_controller import topic_classifier_controller
from crawler.crawler_services.crawler_services.topic_manager.topic_classifier_enums import TOPIC_CLASSFIER_COMMANDS
from crawler.crawler_instance.crawl_controller.crawl_controller import crawl_controller
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler
import warnings
warnings.filterwarnings("ignore")

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
        topic_classifier_controller.get_instance().invoke_trigger(TOPIC_CLASSFIER_COMMANDS.S_LOAD_CLASSIFIER)

    # External Reuqest Callbacks
    def __on_start(self):
        log.g().i(MANAGE_CRAWLER_MESSAGES.S_APPLICATION_STARTING)
        custom_filter_controller.get_instance().init_filter()
        self.__initializations()
        self.__m_crawl_controller.invoke_trigger(CRAWL_CONTROLLER_COMMANDS.S_RUN_CRAWLER)

    # External Reuqest Manager
    def  invoke_triggers(self, p_command):
        if p_command == APPICATION_COMMANDS.S_START_APPLICATION_DIRECT:
            return self.__on_start()

        elif p_command == APPICATION_COMMANDS.S_START_APPLICATION_DOCKERISED:
            return self.__on_start()
