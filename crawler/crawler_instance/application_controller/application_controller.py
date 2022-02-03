import sys
import warnings

from crawler.crawler_services.helper_services.internet_monitor import network_monitor
from crawler.crawler_instance.constants.strings import ERROR_MESSAGES
from crawler.crawler_services.crawler_services.topic_manager.topic_classifier_controller import topic_classifier_controller
from crawler.crawler_services.crawler_services.topic_manager.topic_classifier_enums import TOPIC_CLASSFIER_COMMANDS
from crawler.crawler_instance.tor_controller.tor_controller import tor_controller
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS
from crawler.crawler_services.crawler_services.mongo_manager.mongo_controller import mongo_controller
from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGODB_COMMANDS, MONGO_CRUD
from crawler.crawler_instance.application_controller.application_enums import APPICATION_COMMANDS
from crawler.crawler_instance.crawl_controller.crawl_enums import CRAWL_CONTROLLER_COMMANDS
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler
from crawler.crawler_instance.crawl_controller.crawl_controller import crawl_controller

sys.path.append('C:\Workspace\Genesis-Crawler')
warnings.filterwarnings("ignore", category=DeprecationWarning)

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

    def __on_reset_backup(self):
        m_document_count = mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_READ, [MONGODB_COMMANDS.S_COUNT_CRAWLED_URL, [None],[None]]).count()
        if m_document_count>0:
            mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_UPDATE,[MONGODB_COMMANDS.S_RESET, [None], [None]])

    # External Reuqest Callbacks
    def __on_start(self):
        tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_START, None)
        tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_START, None)
        tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_START, None)
        network_monitor.get_instance().init()
        topic_classifier_controller.get_instance().invoke_trigger(TOPIC_CLASSFIER_COMMANDS.S_LOAD_CLASSIFIER)
        self.__on_reset_backup()
        self.__m_crawl_controller.invoke_trigger(CRAWL_CONTROLLER_COMMANDS.S_RUN_GENERAL_CRAWLER)

    # External Reuqest Manager
    def invoke_triggers(self, p_command, p_data=None):
        if p_command == APPICATION_COMMANDS.S_START_APPLICATION:
            return self.__on_start()
