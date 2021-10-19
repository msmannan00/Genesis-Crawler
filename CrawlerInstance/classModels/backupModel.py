# Local Imports

class backupModel:
    # Local Variables
    m_host = False
    m_parsed = False
    m_thread_catagory = "general"
    m_url_data = []

    # Initializations
    def __init__(self, p_host, p_sub_host, p_depth, p_catagory):
        self.m_host = p_host
        self.m_parsed = False
        self.m_thread_catagory = p_catagory
        self.m_url_data.clear()
        self.m_url_data.append(subHostModel(p_sub_host, p_depth))


# child sharedModel of backup-sharedModel to represent list
class subHostModel:

    # Local Variables
    m_sub_host = False
    m_depth = None

    # Initializations
    def __init__(self, p_sub_host, p_depth):
        self.m_sub_host = p_sub_host
        self.m_depth = p_depth
