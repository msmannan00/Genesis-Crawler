# Local Imports

from libs.pyprobables.probables import BloomFilter


class duplication_handler:
    __m_bloom_filter = None

    # Initializations
    def __init__(self):
        self.__m_bloom_filter = BloomFilter(50000, 0.1)

    # Helper Methods
    def validate_duplicate(self, p_key):
        if self.__m_bloom_filter.check(p_key) is False:
            return False
        else:
            return True

    def insert(self, p_url):
        self.__m_bloom_filter.add(p_url)

    def clear_filter(self):
        self.__m_bloom_filter.clear()
