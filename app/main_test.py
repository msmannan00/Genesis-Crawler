import urllib3
from bs4 import BeautifulSoup

from crawler.crawler_instance.tor_controller.tor_controller import tor_controller
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS

pool = urllib3.PoolManager()
m_request_handler, headers = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_CREATE_SESSION, [True])

ss = pool.request('GET', url="https://bbc.com", timeout=1, headers=headers)
m_content_type = ss.headers['Content-Type'].split('/')[0]
m_file_type = ss.headers['Content-Type'].split('/')[1]
m_url_path = ss.headers['Content-Type'].split('/')[1]
print(len(ss.data))
