import sys

sys.path.append('C:\Workspace\Genesis-Crawler')
from genesis_crawler_services.crawler_services.topic_manager.topic_classifier_controller import topic_classifier_controller
from genesis_crawler_services.crawler_services.topic_manager.topic_classifier_enums import TOPIC_CLASSFIER_COMMANDS
from crawler_instance.log_manager.log_enums import ERROR_MESSAGES
from crawler_instance.tor_controller.tor_controller import tor_controller
from crawler_instance.tor_controller.tor_enums import TOR_COMMANDS
from genesis_crawler_services.crawler_services.mongo_manager.mongo_controller import mongo_controller
from genesis_crawler_services.crawler_services.mongo_manager.mongo_enums import MONGODB_COMMANDS
from crawler_instance.application_controller.application_enums import APPICATION_COMMANDS
from crawler_instance.crawl_controller.crawl_enums import CRAWL_CONTROLLER_COMMANDS
from crawler_instance.shared_model.request_handler import request_handler
from crawler_instance.crawl_controller.crawl_controller import crawl_controller

class application_controller(request_handler):
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
            raise Exception(ERROR_MESSAGES.S_SINGLETON_EXCEPTION)
        else:
            self.__m_crawl_controller = crawl_controller()
            application_controller.__instance = self


    # External Reuqest Callbacks
    def __on_start(self):
        topic_classifier_controller.get_instance().invoke_trigger(TOPIC_CLASSFIER_COMMANDS.S_LOAD_CLASSIFIER)
        tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_START, None)
        mongo_controller.get_instance().invoke_trigger(MONGODB_COMMANDS.S_RESET, None)
        self.__m_crawl_controller.invoke_trigger(CRAWL_CONTROLLER_COMMANDS.S_RUN_GENERAL_CRAWLER)

    # External Reuqest Manager
    def invoke_trigger(self, p_command, p_data=None):
        if p_command == APPICATION_COMMANDS.S_START_APPLICATION:
            return self.__on_start()

# mongo_controller.get_instance().invoke_trigger(MONGODB_COMMANDS.S_CLEAR_CRAWLABLE_URL_DATA, None)
mongo_controller.get_instance().invoke_trigger(MONGODB_COMMANDS.S_CLEAR_DATA, None)
mongo_controller.get_instance().invoke_trigger(MONGODB_COMMANDS.S_RESET, None)
application_controller.get_instance().invoke_trigger(APPICATION_COMMANDS.S_START_APPLICATION)

