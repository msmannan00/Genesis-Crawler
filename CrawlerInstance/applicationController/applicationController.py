# Libraries
import json
import os
import sys

from GenesisCrawlerServices.mongoDBService.mongoDBController import mongoDBController

sys.path.append('C:\Workspace\Genesis-Crawler-Python')
from GenesisCrawlerServices.classifiers.topicClassifier import topicClassifier
from CrawlerInstance.logManager.LogManager import log
from GenesisCrawlerServices.constants import strings, keys
from CrawlerInstance.constants import status, constants
from GenesisCrawlerServices.constants.enums import CrawlerInterfaceCommands, TorCommands, ErrorMessages, ServerResponse, \
    ApplicationResponse, TorStatus, CrawlerStatus, MongoDBCommands
from CrawlerInstance.crawlController.CrawlController import CrawlController
from CrawlerInstance.torController.torController import TorController


class ApplicationController:
    __instance = None
    m_crawl_controller = None
    postDataController = None

    # Initializations
    @staticmethod
    def getInstance():
        if ApplicationController.__instance is None:
            ApplicationController()
        return ApplicationController.__instance

    def __init__(self):
        topicClassifier.getInstance().initialize()
        if ApplicationController.__instance is not None:
            raise Exception(ErrorMessages.singleton_exception)
        else:
            self.m_crawl_controller = CrawlController()
            #self.postDataController = PostDataController();
            ApplicationController.__instance = self


    # External Reuqest Callbacks
    def create(self, p_data):
        self.updateCrawlerStatus(p_data)
        TorController.getInstance().releasePorts()
        TorController.getInstance().releasePorts()
        return ServerResponse.response001.value

    def start(self):
        if status.crawler_status == CrawlerStatus.pause:
            status.crawler_status = CrawlerStatus.running
            return ServerResponse.response006.value
        elif status.crawler_status != CrawlerStatus.running:
            TorController.getInstance().invokeTor(TorCommands.start_command)
            if status.crawler_status != CrawlerStatus.pause:
                self.m_crawl_controller.setEntryURL()
                self.m_crawl_controller.run()
            else:
                status.crawler_status = CrawlerStatus.running
            return ServerResponse.response001.value
        else:
            return ServerResponse.response007.value

    def pause(self):
        if status.crawler_status == CrawlerStatus.running:
            status.crawler_status = CrawlerStatus.pause

    def save(self):
        log.g().i(ApplicationResponse.response009.value)
        status.crawler_status = CrawlerStatus.backing
        self.m_crawl_controller.onStop()
        log.g().i(ApplicationResponse.response002.value)
        self.start()

    def stop(self):
        log.g().i(ApplicationResponse.response001.value)
        status.crawler_status = CrawlerStatus.backing
        self.m_crawl_controller.onStop()
        TorController.getInstance().invokeTor(TorStatus.stop)
        status.crawler_status = CrawlerStatus.stop

    def forceStop(self):
        TorController.getInstance().invokeTor(TorStatus.stop)
        return ApplicationResponse.response003.value

    # Crawl Instance Helper Methods
    def createInfo(self):
        return "Process ID : " + str(os.getpid()) + "<br><div class=\"dropdown-divider\"></div>" + \
               "Crawl Status : " + str(status.crawler_status) + "<br><div class=\"dropdown-divider\"></div>" + \
               "Thread Catagory : " + str(constants.m_thread_catagory) + "<br><div class=\"dropdown-divider\"></div>" + \
               "Thread Repeatable : " + str(constants.m_thread_repeatable) + "<br><div class=\"dropdown-divider\"></div>" + \
               "Total Sub Threads : " + str(constants.m_max_crawler_count) + "<br><div class=\"dropdown-divider\"></div>" + \
               "Max Allowed Depth : " + str(constants.m_max_crawling_depth) + "<br><div class=\"dropdown-divider\"></div>" + \
               "Filter Token : " + str(constants.m_filter_token) + "<br><div class=\"dropdown-divider\"></div>" + \
               "Filter Catagory : " + str(constants.m_filter_catagory) + "<br><div class=\"dropdown-divider\"></div>" + \
               "Filter Type : " + str(constants.m_filter_type) + "<br><div class=\"dropdown-divider\"></div>" + \
               "Tor Status : " + str(status.tor_status) + "<br>"

    def updateCrawlerStatus(self, p_data):
        if p_data is not None:
            constants.m_start_url = p_data[keys.m_start_url]
            constants.m_max_crawler_count = int(p_data[keys.m_max_crawler_count])
            constants.m_max_crawling_depth = int(p_data[keys.m_max_crawling_depth])
            constants.m_thread_catagory = str(p_data[keys.m_thread_catagory])
            if p_data[keys.m_thread_repeatable] == "0":
                constants.m_thread_repeatable = False
            else:
                constants.m_thread_repeatable = True
            constants.m_filter_token = str(p_data[keys.m_filter_token])
            constants.m_filter_catagory = bool(p_data[keys.m_filter_catagory])
            constants.m_filter_type = bool(p_data[keys.m_filter_type])
            status.tor_control_port = str(9052+int(p_data[keys.m_thread_id])*2+1)
            status.tor_connection_port = str(9052+int(p_data[keys.m_thread_id])*2)
            return constants.m_start_url + strings.linebreak

    # Message Listener
    def pipeManagerRead(self):
        try:
            while True:
                nextline = sys.stdin.readline()
                if nextline == strings.empty or status.crawler_status == CrawlerStatus.stop:
                    self.forceStop()
                    break
                else:
                    m_log = self.invokeCrawler(nextline)
                    self.pipeManagerWrite(m_log + strings.linebreak)
        except KeyboardInterrupt:
            self.forceStop()

    # Message Sender
    def pipeManagerWrite(self, p_log):
        sys.stdout.write("# " + p_log)
        sys.stdout.flush()

    # External Reuqest Manager
    def invokeCrawler(self, p_json):
        m_json = json.loads(p_json)
        m_command = m_json[keys.m_command]
        m_data = m_json[keys.m_data]
        if m_command == CrawlerInterfaceCommands.force_stop_command.value:
            return self.forceStop()
        if m_command == CrawlerInterfaceCommands.info_command.value:
            return self.createInfo()
        elif status.crawler_status == CrawlerStatus.backing:
            return ServerResponse.response009.value
        elif m_command == CrawlerInterfaceCommands.start_command.value:
            return self.start()
        elif m_command == CrawlerInterfaceCommands.create_command.value:
            return self.create(m_data)
        elif m_command == CrawlerInterfaceCommands.stop_command.value:
            self.stop()
            return ServerResponse.response002.value
        elif m_command == CrawlerInterfaceCommands.pause_command.value:
            self.pause()
            return ServerResponse.response003.value
        elif m_command == CrawlerInterfaceCommands.save_command.value:
            self.save()
            return ServerResponse.response005.value
        elif m_command == CrawlerInterfaceCommands.fetch_info_logs_command.value:
            return json.dumps(log.g().getInfoLogs())
        elif m_command == CrawlerInterfaceCommands.fetch_error_logs_command.value:
            return json.dumps(log.g().getInfoLogs())
        elif m_command == CrawlerInterfaceCommands.restart_tor_command.value:
            TorController.getInstance().invokeTor(TorCommands.restart_command)
            return ServerResponse.response008.value

# ApplicationController.getInstance().pipeManagerRead()
# topicClassifier.getInstance().generateClassifier()
# mongoDBController.getInstance().onRequest(MongoDBCommands.mongoDB_clear_data_invoke, strings.empty)
mongoDBController.getInstance().onRequest(MongoDBCommands.mongoDB_clear_data_invoke, strings.empty)
ApplicationController.getInstance().invokeCrawler('{"m_data": {"m_max_crawling_depth": "3", "m_max_crawler_count": "30", "m_thread_repeatable": 0, "m_thread_catagory": "default", "m_thread_name": "c_default", "m_start_url": "http://p53lf57qovyuvwsc6xnrppyply3vtqm7l6pcobkmyqsiofyeznfu5uqd.onion/", "m_filter_token": "", "m_filter_catagory": "", "m_filter_type": "", "m_thread_id": "1"}, "m_command": "genesis : create-application"}')
ApplicationController.getInstance().start()
# time.sleep(5)
# ApplicationController.getInstance().forceStop()