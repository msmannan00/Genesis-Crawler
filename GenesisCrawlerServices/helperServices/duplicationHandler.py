# Local Imports
from probables import BloomFilter


# Handle Duplicate URL - Handle url request that have already been parsed or requested
class DuplicationHandler:
    __m_bloom_filter = None
    __instance = None

    # Initializations
    def __init__(self):
        self.__m_bloom_filter = BloomFilter(est_elements=10000000, false_positive_rate=0.01)

    # Helper Methods
    def validate_duplicate_url(self, p_url):
        if self.__m_bloom_filter.check(p_url) is False:
            return False
        else:
            return True

    def insert_url(self, p_url):
        self.__m_bloom_filter.add(p_url)

    # Local Duplicate Cache Handler - Used in case of server or system failure to resume previous state
    def get_filter(self):
        return self.__m_bloom_filter

    def clear_filter(self):
        self.__m_bloom_filter = BloomFilter(est_elements=10000000, false_positive_rate=0.01)

    def clear_data(self):
        self.__m_bloom_filter.clear()
