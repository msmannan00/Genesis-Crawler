import eventlet

from CrawlerInstance.constants import constants
from CrawlerInstance.logManager.logManager import log
from GenesisCrawlerServices.constants import strings, keys
from CrawlerInstance.torController.torcontroller import torController
from GenesisCrawlerServices.constants.enums import TOR_COMMANDS


class webRequestManager:

    def __init__(self):
        pass

    # Load URL - used to request url for parsing to actually crawl the hidden web
    def load_url(self, p_url):

        m_request_handler, proxies, headers = torController.get_instance().invoke_trigger(TOR_COMMANDS.S_CREATE_SESSION)

        try:
            with eventlet.Timeout(constants.S_URL_TIMEOUT):
                page = m_request_handler.get(p_url, headers=headers, timeout=constants.S_URL_TIMEOUT, proxies=proxies, allow_redirects=True, )
                m_html = page.content.decode(strings.S_ISO)

            if page == "" or page.status_code != 200:
                return p_url, False, None
            else:
                return page.url, True, m_html

        except Exception as e:
            log.g().i(strings.S_URL_PROCESSING_ERROR + " : " + p_url + " : " + str(e))
            return p_url, False, None

    # Load Header - used to get header without actually downloading the content
    def load_header(self, p_url):
        m_request_handler, proxies, headers = torController.get_instance().invoke_trigger(TOR_COMMANDS.S_CREATE_SESSION)

        try:
            with eventlet.Timeout(constants.S_HEADER_TIMEOUT):
                headers = {keys.K_USER_AGENT: constants.S_USER_AGENT}
                page = m_request_handler.head(p_url, headers=headers, timeout=(constants.S_HEADER_TIMEOUT, 27), proxies=proxies, allow_redirects=True, verify=False)
                return True, page.headers

        except Exception as e:
            log.g().i(strings.S_URL_PROCESSING_ERROR + " : " + p_url + " : " + str(e))
            return False, None

    # Load Header - used to get header without actually downloading the content
    def download_image(self, p_url):
        m_request_handler, proxies, headers = torController.get_instance().invoke_trigger(TOR_COMMANDS.S_CREATE_SESSION)

        try:
            with eventlet.Timeout(constants.S_URL_TIMEOUT):
                response = m_request_handler.get(p_url, headers=headers, timeout=constants.S_URL_TIMEOUT, proxies=proxies, allow_redirects=True, )
                return True, response
        except Exception as e:
            log.g().i(strings.S_URL_PROCESSING_ERROR + " : " + p_url + " : " + str(e))
            return False, None


