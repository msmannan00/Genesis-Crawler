# Local Imports
import time

from CrawlerInstance.duplicationHandlerService.DuplicationHandlerManager import DuplicationHandlerManager
from CrawlerInstance.logManager.LogManager import log
from CrawlerInstance.constants import constants
from GenesisCrawlerServices.constants import strings
from GenesisCrawlerServices.constants.enums import CrawlerStatus, MongoDBCommands
from GenesisCrawlerServices.helperService.HelperMethod import HelperMethod
from CrawlerInstance.iCrawlController.Parser import Parser
from CrawlerInstance.classModels.IndexModel import IndexModel
from CrawlerInstance.iCrawlController.WebRequestHandler import WebRequestHandler

# Standalone Crawling Instance
from GenesisCrawlerServices.mongoDBService.mongoDBController import mongoDBController


class ICrawlController:

    thread_instance = None
    mHtmlParser = None
    mWebRequestHandler = None
    m_url_model = None

    m_thread_status = CrawlerStatus.running
    m_index_model = IndexModel()

    # url health measure
    m_start_time = 0
    m_failed_url = 0

    def __init__(self):
        self.mHtmlParser = Parser()
        self.mWebRequestHandler = WebRequestHandler()

    # Set Thread Info Of Crawler
    def setThreadInstance(self, p_thread_instance):
        self.thread_instance = p_thread_instance

    # Web Request To Get Physical URL HTML
    def fetchURL(self, p_url_model):
        m_redirected_url, response, html = self.mWebRequestHandler.loadURL(p_url_model.getURL())

        p_url_model.setRedirectedURL(m_redirected_url)
        try:
            m_index_model_temp = self.mHtmlParser.parseHtml(html, p_url_model, response)
            m_index_model_temp.setThreadID(self.thread_instance.ident)
        except Exception as e:
            print("asd")

        p_url_model.setRedirectedURL(HelperMethod.cleanURL(HelperMethod.normalize_slashes(m_redirected_url + "////")))
        if response:
            if not DuplicationHandlerManager.getInstance().isURLDuplicate(m_redirected_url):
                DuplicationHandlerManager.getInstance().insertURL(m_redirected_url)
            elif p_url_model.getURL() != m_redirected_url:
                m_index_model_temp.m_response = False
                return m_index_model_temp

            if strings.onion_str in HelperMethod.getHostURL(m_redirected_url) and m_index_model_temp.m_validity_score >= 15:
                mongoDBController.getInstance().onRequest(MongoDBCommands.mongoDB_save_parse_url, m_index_model_temp)
            else:
                print("Low Yield URL : " + m_redirected_url)
        else:
            self.m_failed_url += 1
            m_index_model_temp.m_response = False

        return m_index_model_temp

    def checkThreadDeadlock(self):
        if time.perf_counter() - self.m_start_time > constants.m_max_thread_life \
                or self.m_failed_url > constants.m_max_failed_url_allowed:
            log.g().i(strings.i_crawl_deadlock + " : " + str(self.thread_instance.ident))
            return True
        else:
            return False

    # Wait For Crawl Manager To Provide URL From Queue
    def startCrawlerInstance(self, p_url_model):
        self.m_url_model = p_url_model
        self.m_index_model.setBaseURL(self.m_url_model)
        self.m_start_time = time.perf_counter()
        while True:
            try:
                if self.m_thread_status == CrawlerStatus.running:
                    self.m_index_model = self.fetchURL(self.m_url_model)
                    self.m_thread_status = CrawlerStatus.pause
                elif self.m_thread_status == CrawlerStatus.pause:
                    time.sleep(constants.m_icrawler_invoke_delay)
                else:
                    break
            except Exception as e:
                print(e)
                self.m_thread_status = CrawlerStatus.pause
                break

    # Crawl Manager Makes Request To Get Crawl duplicationHandlerService
    def getCrawlerData(self):
        return self.checkThreadDeadlock(), self.m_index_model, self.thread_instance, self.m_thread_status

    # Crawl Manager Awakes Crawler Instance From Sleep
    def invokeThread(self, p_status, p_url_model):
        if p_status is True:
            self.m_url_model = p_url_model
            self.m_thread_status = CrawlerStatus.running
        else:
            self.m_thread_status = CrawlerStatus.stop
