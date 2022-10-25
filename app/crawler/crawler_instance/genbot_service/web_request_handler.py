import asyncio
import gc
from asyncio import open_connection

import aiohttp
from aiohttp_socks import ProxyConnector

from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.constants.keys import TOR_KEYS
from crawler.crawler_instance.tor_controller.tor_controller import tor_controller
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS

class webRequestManager:

    def __init__(self):
        pass

    async def fetch(self, p_url, p_proxy, headers):
            connector = ProxyConnector.from_url('socks5://'+p_proxy.split('//')[1])
            async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
                async with session.get(p_url, allow_redirects=True, timeout=CRAWL_SETTINGS_CONSTANTS.S_URL_TIMEOUT) as response:
                    return await response.text(), response.status, response.url


    def load_url(self, p_url, p_custom_proxy):
        try:
            m_request_handler, headers = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_CREATE_SESSION, [True])
            m_html, m_status, m_url_redirect = asyncio.run(self.fetch(p_url, p_custom_proxy["http"], headers))

            m_request_handler.close()
            gc.collect()
            del  m_request_handler
            if m_html == "" or m_status != 200:
                return p_url, False, m_status
            else:
                return m_url_redirect, True, str(m_html)

        except Exception as ex:
            gc.collect()
            return p_url, False, None

    def load_header(self, p_url, p_custom_proxy):
        m_request_handler, headers = tor_controller.get_instance().invoke_trigger(
            TOR_COMMANDS.S_CREATE_SESSION, [True])

        try:
            headers = {TOR_KEYS.S_USER_AGENT: CRAWL_SETTINGS_CONSTANTS.S_USER_AGENT}
            with m_request_handler.head(p_url, headers=headers, timeout=(CRAWL_SETTINGS_CONSTANTS.S_HEADER_TIMEOUT, 27), proxies=p_custom_proxy, allow_redirects=True, verify=False) as page:
                m_request_handler.close()
                gc.collect()
                return True, page.headers

        except Exception:
            m_request_handler.close()
            gc.collect()
            return False, None

    # Load Header - used to get header without actually downloading the content
    def download_image(self, p_url, p_custom_proxy):
        m_request_handler, headers = tor_controller.get_instance().invoke_trigger(
            TOR_COMMANDS.S_CREATE_SESSION, [True])

        try:
            with m_request_handler.get(p_url, headers=headers, timeout=(30,30), proxies=p_custom_proxy, allow_redirects=True, ) as response:
                m_request_handler.close()
                gc.collect()
                return True, response
        except Exception as ex:
            m_request_handler.close()
            gc.collect()
            return False, None
