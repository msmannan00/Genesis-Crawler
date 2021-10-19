# Libraries
import sys

from GenesisCrawlerServices.crawlerServices.mongoDB.mongoController import mongo_controller
from GenesisCrawlerServices.crawlerServices.webClassifier import topicClassifier

sys.path.append('C:\Workspace\Genesis-Crawler')
from CrawlerInstance.sharedModel.requestHandler import requestHandler
from CrawlerInstance.constants.enums import APPICATION_COMMANDS, CRAWL_MODEL_COMMANDS, CRAWL_CONTROLLER_COMMANDS
from GenesisCrawlerServices.crawlerServices.webClassifier.topicClassifier import TopicClassifier
from GenesisCrawlerServices.constants.enums import TOR_COMMANDS, ERROR_MESSAGES, MONGODB_COMMANDS, \
    TOPIC_CLASSFIER_COMMANDS
from CrawlerInstance.crawlController.crawlController import crawlController
from CrawlerInstance.torController.torcontroller import torController


class applicationController(requestHandler):
    __instance = None
    __m_crawl_controller = None

    # Initializations
    @staticmethod
    def get_instance():
        if applicationController.__instance is None:
            applicationController()
        return applicationController.__instance

    def __init__(self):
        if applicationController.__instance is not None:
            raise Exception(ERROR_MESSAGES.S_SINGLETON_EXCEPTION)
        else:
            self.__m_crawl_controller = crawlController()
            applicationController.__instance = self


    # External Reuqest Callbacks
    def __on_create(self):
        torController.get_instance().invoke_trigger(TOR_COMMANDS.S_RELEASE_SESSION)

    def __on_start(self):
        torController.get_instance().invoke_trigger(TOR_COMMANDS.S_START)
        self.__m_crawl_controller.invoke_trigger(CRAWL_CONTROLLER_COMMANDS.S_RUN_GENERAL_CRAWLER)

    def __on_start_classifier_crawl(self):
        self.__m_crawl_controller.invoke_trigger(CRAWL_CONTROLLER_COMMANDS.S_RUN_TOPIC_CLASSIFIER_CRAWLER)

    # External Reuqest Manager
    def invoke_trigger(self, p_command, p_data=None):
        if p_command == APPICATION_COMMANDS.S_START_APPLICATION:
            return self.__on_start()
        if p_command == APPICATION_COMMANDS.S_CRAWL_TOPIC_CLASSIFIER_DATASET:
            return self.__on_start_classifier_crawl()
        if p_command == APPICATION_COMMANDS.S_INSTALL_TOPIC_CLASSIFIER:
            TopicClassifier.get_instance().invoke_trigger(TOPIC_CLASSFIER_COMMANDS.S_GENERATE_CLASSIFIER)

# mongo_controller.get_instance().invoke_trigger(MONGODB_COMMANDS.S_CLEAR_DATA, None)
# applicationController.get_instance().invoke_trigger(APPICATION_COMMANDS.S_CRAWL_TOPIC_CLASSIFIER_DATASET)
applicationController.get_instance().invoke_trigger(APPICATION_COMMANDS.S_INSTALL_TOPIC_CLASSIFIER)
print(TopicClassifier.get_instance().invoke_trigger(TOPIC_CLASSFIER_COMMANDS.S_PREDICT_CLASSIFIER,["XXX sex porn", "XXX sex porn", "XXX sex porn"]))