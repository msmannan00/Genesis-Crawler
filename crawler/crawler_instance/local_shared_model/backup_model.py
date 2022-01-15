# Local Imports
from crawler.crawler_instance.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.crawler_instance.constants.strings import STRINGS


class backup_model:

    # Local Variables
    m_parsed = False
    m_host = STRINGS.S_EMPTY
    m_category = CRAWL_SETTINGS_CONSTANTS.S_THREAD_CATEGORY_GENERAL
    m_url_data = []

    # Initializations
    def __init__(self, p_host, p_sub_host, p_depth, p_catagory):
        self.m_parsed = False
        self.m_host = p_host
        self.m_category = p_catagory
        self.m_url_data.clear()
        self.m_url_data.append(subHostModel(p_sub_host, p_depth))


# child request_manager1 of backup-request_manager1 to represent list
class subHostModel:

    # Local Variables
    m_sub_host = False
    m_depth = None

    # Initializations
    def __init__(self, p_sub_host, p_depth):
        self.m_sub_host = p_sub_host
        self.m_depth = p_depth
