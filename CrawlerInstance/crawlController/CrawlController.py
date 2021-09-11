# Local Imports
import threading
import time

from CrawlerInstance.constants import constants, status
from CrawlerInstance.duplicationHandlerService.DuplicationHandlerManager import DuplicationHandlerManager
from CrawlerInstance.logManager.LogManager import log
from GenesisCrawlerServices.constants import strings
from GenesisCrawlerServices.constants.enums import CrawlerStatus, TorStatus, TorCommands, ErrorMessages
from CrawlerInstance.crawlController.QueueController import QueueController
from GenesisCrawlerServices.duplicationHandlerService.DuplicationHandlerGlobal import DuplicationHandlerGlobal
from GenesisCrawlerServices.helperService.HelperMethod import HelperMethod
from CrawlerInstance.iCrawlController.ICrawlController import ICrawlController
from CrawlerInstance.torController.torController import TorController


class CrawlController:
    # Local Variables
    m_thread_index = 0
    m_queue_controller = None
    m_counter = 0
    m_empty_duration = 0

    # Crawler Instances & Threads
    m_main_thread = None

    # Crawler Instances & Threads
    m_crawler_thread_list = []
    m_crawler_instance_list = []

    # Initializations
    def __init__(self):
        self.m_queue_controller = QueueController()

    # Helper Methods
    def saveUrl(self, p_url, p_base_url_model):
        if DuplicationHandlerManager.getInstance().isURLDuplicate(p_url) is False:
            DuplicationHandlerManager.getInstance().insertURL(p_url)
            self.m_queue_controller.prepareURL(p_url, p_base_url_model)

    def cleanSaveURL(self, p_base_url_model):
        for m_url in p_base_url_model.m_sub_url:
            m_url = HelperMethod.cleanURL(HelperMethod.normalize_slashes(m_url + "////"))
            self.saveUrl(m_url, p_base_url_model)

    # Start Crawler Manager
    def run(self):
        status.crawler_status = CrawlerStatus.running
        self.m_main_thread = threading.Thread(target=self.crawlThreadManager)
        self.m_main_thread.start()

    # Input Default URL
    def setEntryURL(self):
        m_start_url = constants.m_start_url.split(",")
        for m_url in m_start_url:
            if DuplicationHandlerManager.getInstance().isURLDuplicate(m_url) is False:
                DuplicationHandlerManager.getInstance().insertURL(m_url)
                self.m_queue_controller.saveBackupURLToDrive(m_url, 0)

    # ICrawler Manager
    def crawlThreadManager(self):
        while status.crawler_status == CrawlerStatus.running or status.crawler_status == CrawlerStatus.pause:
            try:
                if status.crawler_status != CrawlerStatus.pause and status.tor_status == TorStatus.running:
                    self.iCrawlerInvoke()
                    if len(self.m_crawler_thread_list) < constants.m_max_crawler_count:
                        m_status, m_url_model = self.m_queue_controller.getHostURL()
                        if m_status and m_url_model.getHostURL():
                            # Creating Thread Instace
                            m_i_cralwer = ICrawlController()
                            thread_instance = threading.Thread(target=m_i_cralwer.startCrawlerInstance, args=[m_url_model])
                            thread_instance.start()

                            # Saving Thread Instace
                            self.m_crawler_instance_list.append(m_i_cralwer)
                            self.m_crawler_thread_list.append(thread_instance)
                            m_i_cralwer.setThreadInstance(thread_instance)
                time.sleep(constants.m_crawler_invoke_delay)
                self.m_counter += 1
                self.counterBasedCommands()
            except Exception as e:
                #log.g().i(ErrorMessages.critical_exception_crawl + " : " + e)
                break

    # Stop Port
    def onStop(self):
        while len(self.m_crawler_instance_list) > 0:
            try:
                for m_Crawl_instance in self.m_crawler_instance_list:
                    m_deadlock_status, m_index_model, thread_instance, m_thread_status = m_Crawl_instance.getCrawlerData()
                    if m_thread_status == CrawlerStatus.stop or m_deadlock_status is True or m_thread_status == CrawlerStatus.pause:
                        m_Crawl_instance.invokeThread(False, None)
                        self.m_crawler_instance_list.remove(m_Crawl_instance)
                        if self.m_crawler_thread_list.__contains__(thread_instance):
                            self.m_crawler_thread_list.remove(thread_instance)
                        if m_thread_status == CrawlerStatus.pause:
                            self.cleanSaveURL(m_index_model)
            except Exception as e:
                print(e)
        self.m_queue_controller.onStop()
        DuplicationHandlerManager.getInstance().saveObjectBackup()
        log.g().i("Thread Finished : " + str(len(self.m_crawler_instance_list)))

    # Awake Crawler From Sleep
    def iCrawlerInvoke(self):
        m_live_thread = 0

        for m_Crawl_instance in self.m_crawler_instance_list:
            m_deadlock_status, m_index_model, thread_instance, m_thread_status = m_Crawl_instance. \
                getCrawlerData()
            if m_thread_status == CrawlerStatus.stop:
                self.m_crawler_instance_list.remove(m_Crawl_instance)
            elif m_deadlock_status is True:
                m_Crawl_instance.invokeThread(False, None)
                self.m_crawler_instance_list.remove(m_Crawl_instance)
                self.m_crawler_thread_list.remove(thread_instance)
                self.m_queue_controller.removeHost(m_index_model.m_base_url_model.m_url)
            elif m_thread_status == CrawlerStatus.pause:
                m_status, m_url_model = self.iCrawlerRequest(m_index_model, thread_instance)
                m_Crawl_instance.invokeThread(m_status, m_url_model)
                m_live_thread += m_status is True
            elif m_thread_status == CrawlerStatus.running:
                m_live_thread += 1
        log.g().i("\n" + strings.invoked_status + " : " + str(m_live_thread))


    # Try To Get Job For Crawler Instance
    def iCrawlerRequest(self, p_index_model, p_thread_instance):

        if p_index_model is None:
            return False, None
        if p_index_model.m_response is True:
            self.cleanSaveURL(p_index_model)
        m_status, m_url_model = self.m_queue_controller.getSubURL(
            p_index_model.m_base_url_model.getURL())
        if not m_status:
            self.m_crawler_thread_list.remove(p_thread_instance)
            return False, None
        else:
            return m_status, m_url_model

    # Create Backup - After specific time has elapsed create backup for entire system
    def counterBasedCommands(self):
        if self.m_counter % constants.m_new_circuit_delay == 0:
            TorController.getInstance().invokeTor(TorCommands.generate_circuit_command)
        if self.m_counter % constants.m_backup_time_delay == 0:
            log.g().i("Backing Up Duplication URL")
            DuplicationHandlerGlobal.getInstance().saveObject()
            log.g().i("Duplication URL Backup Created")
        if self.m_counter % constants.restart_crawler_delay == 0:
            if constants.m_thread_repeatable and status.backup_queue_status == False and self.m_queue_controller.isQueueEmpty():
                if self.m_empty_duration>0:
                    self.m_empty_duration = 0
                    log.g().i("Restarting Crawler")
                    DuplicationHandlerGlobal.getInstance().clearFilter()
                    self.setEntryURL()
                    log.g().i("Crawler Restarted")
                self.m_empty_duration += 1
