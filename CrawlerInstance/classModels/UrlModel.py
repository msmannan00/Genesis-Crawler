# Non Parsed URL Model
from GenesisCrawlerServices.helperService.HelperMethod import HelperMethod


# Model representing information of url to be put in backup queue
class UrlModel:

    # Local Variables
    m_redirected_host = ""
    m_redirected_subhost = ""
    m_url = ""
    m_depth = 0

    # Initializations
    def __init__(self, p_url, p_depth):
        self.m_url = p_url
        self.m_redirected_host = p_url
        self.m_depth = p_depth

    # Getter Setters
    def setRedirectedURL(self, m_url):
        self.m_redirected_host, self.m_redirected_subhost = HelperMethod.splitHostURL(m_url)

    def getRedirectedURL(self):
        return self.m_redirected_host + self.m_redirected_subhost

    def getHostURL(self):
        return self.m_redirected_host

    def getURL(self):
        return self.m_url

    def getDepth(self):
        return self.m_depth
