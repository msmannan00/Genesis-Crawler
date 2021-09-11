import eventlet

from CrawlerInstance.constants import constants
from CrawlerInstance.logManager.LogManager import log
from GenesisCrawlerServices.constants import strings, keys
from GenesisCrawlerServices.constants.enums import InfoMessages
from CrawlerInstance.torController.torController import TorController
# pip install -U requests[socks]


class WebRequestHandler:

    def __init__(self):
        pass

    # Load URL - used to request url for parsing to actually crawl the hidden web
    def loadURL(self, p_url):

        m_request_handler, proxies, headers = TorController.getInstance().createSession()

        try:
            with eventlet.Timeout(constants.m_url_timeout):
                page = m_request_handler.get(p_url, headers=headers, timeout=(constants.m_url_timeout, 27), proxies=proxies, allow_redirects=True, )
                m_html = page.content.decode(strings.utf_8)

            if page == "" or page.status_code != 200:
                return p_url, False, None
            else:
                return page.url, True, m_html

        except Exception as e:
            log.g().i(strings.url_processing_error + " : " + p_url + " : " + str(e))
            return p_url, False, None

    # Load Header - used to get header without actually downloading the content
    def loadHeader(self, p_url):
        m_request_handler, proxies, headers = TorController.getInstance().createSession()

        try:
            with eventlet.Timeout(constants.m_header_timeout):
                headers = {keys.k_user_agent: constants.m_user_agent}
                page = m_request_handler.head(p_url, headers=headers, timeout=(constants.m_header_timeout, 27), proxies=proxies, allow_redirects=True, verify=False)
                return True, page.headers

        except Exception as e:
            log.g().i(strings.url_processing_error + " : " + p_url + " : " + str(e))
            return False, None

    def echoIP(self, p_request_handler, p_proxies, p_headers):
        m_request_handler, m_proxies, m_headers = p_request_handler, p_proxies, p_headers
        result = m_request_handler.get(constants.m_ip_ping_url, headers=m_headers, timeout=(constants.m_header_timeout, 27), proxies=m_proxies, allow_redirects=True, verify=False)
        ip = result.json()[keys.k_ip]
        log.g().i(InfoMessages.your_ip.value + ip)
