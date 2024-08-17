import asyncio
import gc
from _weakref import ProxyType

import aiohttp

from aiohttp_socks import ProxyConnector
from raven.transport import requests

from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.constants.keys import TOR_KEYS
from crawler.crawler_instance.tor_controller.tor_controller import tor_controller
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS

class webRequestManager:

    def __init__(self):
        pass

    async def fetch(self, p_url, p_proxy, headers):
        try:
            # Manually setting up the proxy connector with the correct SOCKS5 protocol
            connector = ProxyConnector(
                proxy_type=ProxyType.SOCKS5,
                host="127.0.0.1",
                port=9150,  # Port for Tor SOCKS proxy
                rdns=True  # This is important for resolving DNS via the proxy
            )

            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(p_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    response.raise_for_status()
                    text = await response.text()
                    return text, response.status, str(response.url)
        except Exception as ex:
            return str(ex), None, None

    def load_url(self, p_url, p_custom_proxy):
        try:
            p_url = "https://bbc.com"
            m_request_handler, headers = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_CREATE_SESSION, [True])
            m_html, m_status, m_url_redirect = asyncio.run(self.fetch(p_url, p_custom_proxy["http"], headers))

            m_request_handler.close()
            del m_request_handler
            if m_html == "" or m_status != 200:
                return str(p_url), False, m_status
            else:
                return str(m_url_redirect), True, str(m_html)

        except Exception:
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
