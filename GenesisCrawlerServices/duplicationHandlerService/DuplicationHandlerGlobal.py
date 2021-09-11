# Local Imports
from probables import BloomFilter
from CrawlerInstance.constants import constants
from GenesisCrawlerServices.constants.enums import ErrorMessages
from GenesisCrawlerServices.helperService.HelperMethod import HelperMethod


# Handle Duplicate URL - Handle url request that have already been parsed or requested
class DuplicationHandlerGlobal:
    m_bloom_filter = None
    __instance = None

    # Initializations
    @staticmethod
    def getInstance():
        if DuplicationHandlerGlobal.__instance is None:
            DuplicationHandlerGlobal(None, False)
        return DuplicationHandlerGlobal.__instance

    @staticmethod
    def setInstance(p_backed_instance):
        DuplicationHandlerGlobal.__instance = p_backed_instance
        p_backed_instance.loadObject()

    def __init__(self, m_bloom_filter, m_savable):
        if m_savable is True:
            self.m_bloom_filter = m_bloom_filter
            DuplicationHandlerGlobal.__instance = self
        else:
            self.m_bloom_filter = BloomFilter(est_elements=10000000, false_positive_rate=0.01)
            if DuplicationHandlerGlobal.__instance is not None:
                raise Exception(ErrorMessages.singleton_exception)
            else:
                DuplicationHandlerGlobal.__instance = self

    # Helper Methods
    def isURLDuplicate(self, p_url):
        if self.m_bloom_filter.check(p_url) is False:
            return False
        else:
            return True

    def insertURL(self, p_url):
        self.m_bloom_filter.add(p_url)

    def clearData(self):
        self.m_bloom_filter.clear()

    # Local Duplicate Cache Handler - Used in case of server or system failure to resume previous state
    def saveObject(self):
        HelperMethod.saveObject(constants.m_duplication_filter_backup_path_1, DuplicationHandlerGlobal(self.m_bloom_filter, True))

    def saveObjectBackup(self):
        HelperMethod.saveObject(constants.m_duplication_filter_backup_path_2, DuplicationHandlerGlobal(self.m_bloom_filter, True))

    def loadObject(self):
        DuplicationHandlerGlobal.setInstance(HelperMethod.loadObject(constants.m_duplication_filter_backup_path_2))

