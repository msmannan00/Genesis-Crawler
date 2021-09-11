# Local Imports
from CrawlerInstance.constants import constants

from GenesisCrawlerServices.duplicationHandlerService.DuplicationHandlerGlobal import DuplicationHandlerGlobal
from GenesisCrawlerServices.duplicationHandlerService.DuplicationHandlerLocal import DuplicationHandlerLocal
from GenesisCrawlerServices.helperService.HelperMethod import HelperMethod


class DuplicationHandlerManager:
    m_duplication_handler = None
    __instance = None

    @staticmethod
    def getInstance():
        if DuplicationHandlerManager.__instance is None:
            DuplicationHandlerManager()
        return DuplicationHandlerManager.__instance

    # Initializations
    def __init__(self):
        DuplicationHandlerManager.__instance = self
        self.initialize()

    def initialize(self):
        if constants.m_thread_repeatable:
            self.m_duplication_handler = DuplicationHandlerLocal()
        else:
            self.m_duplication_handler = DuplicationHandlerGlobal.getInstance()

    # Helper Methods
    def isURLDuplicate(self, p_url):
        return self.m_duplication_handler.isURLDuplicate(p_url)

    def insertURL(self, p_url):
        if self.m_duplication_handler != DuplicationHandlerGlobal.getInstance():
            DuplicationHandlerGlobal.getInstance().insertURL(p_url)
        return self.m_duplication_handler.insertURL(p_url)


    # Local Duplicate Cache Handler - Used in case of server or system failure to resume previous state
    def getFilter(self):
        return self.m_duplication_handler.getFilter()

    def clearFilter(self):
        self.m_duplication_handler.clearFilter()

    def clearData(self):
        self.m_duplication_handler.clearData()

    def saveObject(self):
        HelperMethod.saveObject(constants.m_duplication_filter_backup_path_1, DuplicationHandlerGlobal(self.m_bloom_filter, True))
