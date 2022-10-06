# Local Imports


class duplication_handler:
    __m_bloom_filter = {''}

    # Initializations
    def __init__(self):
        pass

    # Helper Methods
    def validate_duplicate(self, p_key):
        if p_key in self.__m_bloom_filter is False:
            return False
        else:
            return True

    def insert(self, p_url):
        self.__m_bloom_filter.add(p_url)

    def clear_filter(self):
        self.__m_bloom_filter.clear()
