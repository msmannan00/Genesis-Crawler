# Local Imports
from probables import BloomFilter


# Handle Duplicate URL - Handle url request that have already been parsed or requested
class DuplicationHandlerLocal:
    m_bloom_filter = None
    __instance = None

    # Initializations
    def __init__(self):
        self.m_bloom_filter = BloomFilter(est_elements=10000000, false_positive_rate=0.01)

    # Helper Methods
    def isURLDuplicate(self, p_url):
        if self.m_bloom_filter.check(p_url) is False:
            return False
        else:
            return True

    def insertURL(self, p_url):
        self.m_bloom_filter.add(p_url)

    # Local Duplicate Cache Handler - Used in case of server or system failure to resume previous state
    def getFilter(self):
        return self.m_bloom_filter

    def clearFilter(self):
        self.m_bloom_filter = BloomFilter(est_elements=10000000, false_positive_rate=0.01)

    def clearData(self):
        self.m_bloom_filter.clear()
