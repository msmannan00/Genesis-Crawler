# Local Libraries
from CrawlerInstance.classModels.backupModel import backupModel
from CrawlerInstance.duplicationHandlerService.DuplicationHandlerManager import DuplicationHandlerManager
from GenesisCrawlerServices.duplicationHandlerService.DuplicationHandlerGlobal import DuplicationHandlerGlobal
from CrawlerInstance.constants import constants, status
from GenesisCrawlerServices.constants import strings, keys
from GenesisCrawlerServices.constants.enums import MongoDBCommands, InfoMessages, ErrorMessages
from GenesisCrawlerServices.helperService.HelperMethod import HelperMethod
from CrawlerInstance.classModels.IndexModel import UrlObjectEncoder
from CrawlerInstance.classModels.UrlModel import UrlModel
from CrawlerInstance.iCrawlController.WebRequestHandler import WebRequestHandler
from CrawlerInstance.logManager.LogManager import log
from GenesisCrawlerServices.mongoDBService.mongoDBController import mongoDBController


# URL Queue Manager
class QueueController:
    # Local Queues
    m_url_queue = {}
    m_active_queue = []
    m_inactive_queue = []

    # Local Variables
    local_database_handler = WebRequestHandler()

    # Helper Methods
    def __init__(self):
        self.m_url_queue = dict()

    def calculateDepth(self, p_url, p_base_url_model):

        depth = 1
        new_url_host = HelperMethod.getHostURL(p_url)
        parent_host = HelperMethod.getHostURL(p_base_url_model.m_base_url_model.getHostURL())
        m_onion_extention = strings.onion_extention
        m_onion_str = strings.onion_str

        if m_onion_extention not in new_url_host and m_onion_extention not in parent_host:
            depth = constants.m_max_crawling_depth
        elif (m_onion_extention not in new_url_host and m_onion_extention
              in parent_host):
            if m_onion_str in p_url or m_onion_str in p_base_url_model.m_correct_keyword \
                    or m_onion_str in p_base_url_model.m_incorrect_keyword:
                depth = constants.m_max_crawling_depth - 1
            else:
                depth = constants.m_max_crawling_depth
        elif m_onion_extention in new_url_host and m_onion_extention in parent_host:
            if new_url_host == parent_host:
                try:
                    depth = p_base_url_model.m_base_url_model.getDepth() + 1
                except Exception as e:
                    log.g().e(str(e))
            else:
                if not DuplicationHandlerManager.getInstance().isURLDuplicate(new_url_host):
                    depth = 0
                else:
                    depth = constants.m_max_crawling_depth - 1
        return depth

    # Max Host Depth - In case of url queue exceeded size of > 100 start putting them in database
    def insertLoadedBackupURL(self, p_url, p_depth):
        m_url_host = HelperMethod.getHostURL(p_url)
        if m_url_host not in self.m_url_queue.keys():
            m_fresh_url_model = UrlModel(p_url, p_depth)
            self.m_url_queue[m_url_host] = [m_fresh_url_model]
            self.m_inactive_queue.append(m_url_host)
        else:
            self.m_url_queue[m_url_host].append(UrlModel(p_url, p_depth))

    # Insert To Database - Insert URL to database after parsing them
    def insertURL(self, p_url, p_depth):
        m_url_host = HelperMethod.getHostURL(p_url)
        if m_url_host not in self.m_url_queue.keys():
            if len(self.m_url_queue) < constants.m_max_host_queue_size:
                if status.backup_queue_status is not True:
                    m_fresh_url_model = UrlModel(p_url, p_depth)
                    self.m_url_queue[m_url_host] = [m_fresh_url_model]
                    if not DuplicationHandlerManager.getInstance().isURLDuplicate(m_url_host):
                        DuplicationHandlerManager.getInstance().insertURL(m_url_host)
                        self.m_url_queue[m_url_host].insert(0, UrlModel(m_url_host, p_depth))
                    self.m_inactive_queue.append(m_url_host)
            else:
                self.saveBackupURLToDrive(p_url, p_depth)
                status.backup_queue_status = True
        else:
            if "?" in p_url:
                self.m_url_queue[m_url_host].append(UrlModel(p_url, p_depth))
            else:
                self.m_url_queue[m_url_host].insert(0, UrlModel(p_url, p_depth))

    # Prepare URL By Depth
    def prepareURL(self, p_url, p_base_url_model):
        m_url_depth = self.calculateDepth(p_url, p_base_url_model)
        if m_url_depth < constants.m_max_crawling_depth:
            self.insertURL(p_url, m_url_depth)

    # Remove Already Parsed Host
    def removeHost(self, p_url):
        m_host_url = HelperMethod.getHostURL(p_url)
        del self.m_url_queue[m_host_url]
        self.m_active_queue.remove(m_host_url)

    # Extract Fresh Host URL
    def getHostURL(self):
        if len(self.m_inactive_queue) <= 0:
            if status.backup_queue_status is True:
                self.loadBackupURL()

        if len(self.m_inactive_queue) > 0:
            m_url_key = self.m_inactive_queue.pop(len(self.m_inactive_queue) - 1)
            self.m_active_queue.append(m_url_key)
            m_url_model = self.m_url_queue.get(m_url_key).pop(len(self.m_url_queue.get(m_url_key)) - 1)

            return True, m_url_model
        else:
            return False, None

    # Extract Sub URL - Extract url in relation to host extracted in above ^ function
    def getSubURL(self, p_host_url):
        m_url_host = HelperMethod.getHostURL(p_host_url)
        if m_url_host in self.m_url_queue and len(self.m_url_queue[m_url_host]) > 0:
            m_url_model = self.m_url_queue.get(m_url_host).pop(0)
            return True, m_url_model
        else:
            self.m_active_queue.remove(m_url_host)
            self.m_url_queue.pop(m_url_host, None)
            return False, None

    # Local Queue Cache Handler - Used in case of server or system failure to resume previous state
    def loadQueueFromAwake(self):
        self.m_inactive_queue = list(self.m_url_queue.keys())
        m_temp_list = list(self.m_url_queue.keys())
        for item in m_temp_list:
            if len(self.m_url_queue[item]) <= 0:
                self.m_url_queue.pop(item, None)
            else:
                self.m_inactive_queue.append(item)

    def saveBackupURLToDrive(self, p_url, p_url_depth):
        status.backup_queue_status = True
        m_host = HelperMethod.getHostURL(p_url)
        m_subhost = p_url.replace(m_host, "")
        m_data = backupModel(m_host, m_subhost, p_url_depth, constants.m_thread_catagory)
        response = mongoDBController.getInstance().onRequest(MongoDBCommands.mongoDB_save_backup_url, m_data)

    def loadBackupURL(self):
        try:
            m_data = backupModel(strings.empty, strings.empty, strings.empty, constants.m_thread_catagory)
            response, data = mongoDBController.getInstance().onRequest(MongoDBCommands.mongoDB_get_backup_url, m_data)
            if response is True:
                for data_item in data:
                    for m_url_model in data_item[keys.k_url_data]:
                        self.insertLoadedBackupURL(data_item[keys.k_host] + m_url_model[keys.k_sub_host],
                                                   int(m_url_model[keys.k_depth]))
                log.g().i(InfoMessages.loaded_backup_URL.value)
                if len(data) < constants.m_mongoDB_backup_url_fetch_limit:
                    log.g().e(InfoMessages.backup_queue_empty.value)
                    status.backup_queue_status = False
            else:
                log.g().e(ErrorMessages.database_error_fetch)
                status.backup_queue_status = False
        except Exception as e:
            log.g().e(e)

    def onStop(self):
        for m_url_host in self.m_active_queue:
            for m_url_item in self.m_url_queue[m_url_host]:
                self.saveBackupURLToDrive(m_url_item.getURL(), m_url_item.getDepth())

        for m_url_host in self.m_inactive_queue:
            for m_url_item in self.m_url_queue[m_url_host]:
                self.saveBackupURLToDrive(m_url_item.getURL(), m_url_item.getDepth())

    def isQueueEmpty(self):
        return len(self.m_url_queue)<=0 and len(self.m_active_queue)<=0 and len(self.m_inactive_queue)<=0