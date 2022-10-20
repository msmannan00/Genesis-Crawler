from bs4 import BeautifulSoup
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.constants.keys import TOR_KEYS
from crawler.crawler_instance.tor_controller.tor_controller import tor_controller
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS


class webRequestManager:

    def __init__(self):
        pass

    def load_url(self, p_url, p_custom_proxy):
        m_request_handler, headers = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_CREATE_SESSION, [True])

        try:
            pass
            page = m_request_handler.get(p_url, headers=headers, timeout=CRAWL_SETTINGS_CONSTANTS.S_URL_TIMEOUT, proxies=p_custom_proxy, allow_redirects=True, )
            soup = page.content
            if page == "" or page.status_code != 200:
                return p_url, False, page.status_code
            else:
                return page.url, True, str(soup)

        except Exception as ex:
            return p_url, False, None

    def load_header(self, p_url, p_custom_proxy):
        m_request_handler, headers = tor_controller.get_instance().invoke_trigger(
            TOR_COMMANDS.S_CREATE_SESSION, [True])

        try:
            headers = {TOR_KEYS.S_USER_AGENT: CRAWL_SETTINGS_CONSTANTS.S_USER_AGENT}
            page = m_request_handler.head(p_url, headers=headers, timeout=(CRAWL_SETTINGS_CONSTANTS.S_HEADER_TIMEOUT, 27), proxies=p_custom_proxy, allow_redirects=True, verify=False)
            return True, page.headers

        except Exception:
            return False, None

    # Load Header - used to get header without actually downloading the content
    def download_image(self, p_url, p_custom_proxy):
        m_request_handler, headers = tor_controller.get_instance().invoke_trigger(
            TOR_COMMANDS.S_CREATE_SESSION, [True])

        try:
            response = m_request_handler.get(p_url, headers=headers, timeout=CRAWL_SETTINGS_CONSTANTS.S_URL_TIMEOUT, proxies=p_custom_proxy, allow_redirects=True, )
            return True, response
        except Exception as ex:
            return False, None
