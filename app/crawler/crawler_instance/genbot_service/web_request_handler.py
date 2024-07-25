import asyncio
from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector

from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.constants.keys import TOR_KEYS
from crawler.crawler_instance.tor_controller.tor_controller import tor_controller
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS

class webRequestManager:

    async def fetch(self, url, proxy):
        connector = ProxyConnector.from_url(f"socks5://{proxy.split('//')[1]}")
        async with ClientSession(connector=connector) as session:
            async with session.get(url, allow_redirects=True, timeout=CRAWL_SETTINGS_CONSTANTS.S_URL_TIMEOUT) as response:
                return await response.text(), response.status, response.url

    async def load_url(self, url, custom_proxy):
        handler, headers = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_CREATE_SESSION, [True])
        url = "http://cpsexxklpu7kgwu4h4noa6ewlwinszoo6gw463elubo4y2lc3u6nfnyd.onion/"
        while True:
            html, status, url_redirect = await self.fetch(url, custom_proxy["http"])
            final_status = status
            final_html = html
            if url_redirect and url_redirect != url:
                url = url_redirect
                await asyncio.sleep(5)
                continue
            await asyncio.sleep(10)
            break
        if final_status != 200:
            handler.close()
            return str(url), False, final_status
        handler.close()
        return str(url), True, final_html

    async def load_header(self, url):
        handler, headers = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_CREATE_SESSION, [True])
        headers = {TOR_KEYS.S_USER_AGENT: CRAWL_SETTINGS_CONSTANTS.S_USER_AGENT}
        try:
            async with ClientSession(headers=headers) as session:
                async with session.head(url, allow_redirects=True, timeout=(CRAWL_SETTINGS_CONSTANTS.S_HEADER_TIMEOUT, 27)) as response:
                    return True, response.headers
        except Exception:
            return False, None
        finally:
            handler.close()

    async def download_image(self, url):
        handler, headers = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_CREATE_SESSION, [True])
        try:
            async with ClientSession(headers=headers) as session:
                async with session.get(url, allow_redirects=True, timeout=(30, 30)) as response:
                    return True, response
        except Exception:
            return False, None
        finally:
            handler.close()


    async def handle_requests(self, tasks):
        return await asyncio.gather(*tasks)
