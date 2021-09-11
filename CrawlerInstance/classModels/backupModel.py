# Local Imports


# model representing information of any particular url
from GenesisCrawlerServices.constants.strings import MongoDB_backup_type_general


class backupModel:
    # Local Variables
    m_host = False
    m_thread_catagory = MongoDB_backup_type_general
    m_url_data = []

    # Initializations
    def __init__(self, p_host, p_sub_host, p_depth, p_catagory):
        self.m_host = p_host
        self.m_thread_catagory = p_catagory
        self.m_url_data.clear()
        self.m_url_data.append(subhostModel(p_sub_host, p_depth))


# child model of backup-model to represent list
class subhostModel:
    # Local Variables
    m_sub_host = False
    m_depth = None

    # Initializations
    def __init__(self, p_sub_host, p_depth):
        self.m_sub_host = p_sub_host
        self.m_depth = p_depth
