# Non Parsed URL Model
from GenesisCrawlerServices.helperServices.helperMethod import helper_method


# Model representing information of url to be put in backup queue
class urlModel:

    # Local Variables
    m_redirected_host = ""
    m_redirected_subhost = ""
    m_url = ""
    m_depth = 0
    m_type = ""

    # Initializations
    def __init__(self, p_url, p_depth, p_type):
        self.m_url = p_url
        self.m_redirected_host = p_url
        self.m_depth = p_depth
        self.m_type = p_type

    # Getter Setters
    def setRedirectedURL(self, m_url):
        self.m_redirected_host, self.m_redirected_subhost = helper_method.split_host_url(m_url)

    def getRedirectedURL(self):
        return self.m_redirected_host + self.m_redirected_subhost

    def getHostURL(self):
        return self.m_redirected_host

    def getURL(self):
        return self.m_url

    def getDepth(self):
        return self.m_depth
