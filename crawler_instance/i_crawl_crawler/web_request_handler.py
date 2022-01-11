import eventlet
from bs4 import BeautifulSoup

from crawler_instance.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler_instance.constants.strings import MESSAGE_STRINGS, STRINGS
from crawler_instance.tor_controller.tor_controller import tor_controller
from crawler_instance.tor_controller.tor_enums import TOR_COMMANDS
from crawler_services.constants.keys import tor_keys
from crawler_shared_directory.log_manager.log_controller import log


class webRequestManager:

    def __init__(self):
        pass

    # Load URL - used to request url for parsing to actually crawl the hidden web
    def load_url(self, p_url):

        m_request_handler, proxies, headers = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_CREATE_SESSION)

        try:
            with eventlet.Timeout(CRAWL_SETTINGS_CONSTANTS.S_URL_TIMEOUT):
                page = m_request_handler.get(p_url, headers=headers, timeout=CRAWL_SETTINGS_CONSTANTS.S_URL_TIMEOUT, proxies=proxies, allow_redirects=True, )
                soup = BeautifulSoup(page.content.decode('utf-8', 'ignore'),features="lxml")

            if page == "" or page.status_code != 200:
                return p_url, False, None
            else:
                return page.url, True, str(soup)

        except Exception as e:
            log.g().e("WEB REQUEST E1 : " + MESSAGE_STRINGS.S_URL_PROCESSING_ERROR + " : " + p_url + " : " + str(e))
            return p_url, False, None


    def load_header(self, p_url):
        m_request_handler, proxies, headers = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_CREATE_SESSION)

        try:
            with eventlet.Timeout(CRAWL_SETTINGS_CONSTANTS.S_HEADER_TIMEOUT):
                try:
                    headers = {tor_keys.S_USER_AGENT: CRAWL_SETTINGS_CONSTANTS.S_USER_AGENT}
                    page = m_request_handler.head(p_url, headers=headers, timeout=(CRAWL_SETTINGS_CONSTANTS.S_HEADER_TIMEOUT, 27), proxies=proxies, allow_redirects=True, verify=False)
                except Exception as e:
                    log.g().e( "WEB REQUEST E2 : " + MESSAGE_STRINGS.S_URL_PROCESSING_ERROR + STRINGS.S_SEPERATOR + p_url + STRINGS.S_SEPERATOR + str(e))
                    return False, None
                return True, page.headers
        except:
            log.g().e("WEB REQUEST E3 : ")
            return False, None

    # Load Header - used to get header without actually downloading the content
    def download_image(self, p_url):
        m_request_handler, proxies, headers = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_CREATE_SESSION)

        try:
            with eventlet.Timeout(CRAWL_SETTINGS_CONSTANTS.S_URL_TIMEOUT):
                response = m_request_handler.get(p_url, headers=headers, timeout=CRAWL_SETTINGS_CONSTANTS.S_URL_TIMEOUT, proxies=proxies, allow_redirects=True, )
                return True, response
        except Exception as e:
            log.g().e("WEB REQUEST E3 : " + MESSAGE_STRINGS.S_URL_PROCESSING_ERROR + STRINGS.S_SEPERATOR + p_url + STRINGS.S_SEPERATOR + str(e))
            return False, None
