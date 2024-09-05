import gc
from raven.transport import requests
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.constants.keys import TOR_KEYS
from crawler.crawler_instance.helper_services.helper_method import helper_method
from crawler.crawler_instance.tor_controller.tor_controller import tor_controller
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS
from crawler.crawler_services.helper_services.crypto_handler import crypto_handler


class webRequestManager:

  def __init__(self):
    pass

  def fetch(self, p_url, p_proxy, headers):
    try:
      proxy_url = next(iter(p_proxy.values()))
      ip_port = proxy_url.split('//')[1]
      ip, port = ip_port.split(':')
      proxy_host = p_proxy.get('host', ip)
      proxy_port = p_proxy.get('port', port)

      proxies = {
        "http": f"socks5h://{proxy_host}:{proxy_port}",
        "https": f"socks5h://{proxy_host}:{proxy_port}"
      }

      response = requests.get(p_url, headers=headers, proxies=proxies, timeout=CRAWL_SETTINGS_CONSTANTS.S_URL_TIMEOUT)
      response.raise_for_status()
      return response.text, response.status_code, response.url

    except Exception as ex:
      return str(ex), None, None

  def load_url(self, p_url, p_custom_proxy):
    try:
      m_request_handler, headers = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_CREATE_SESSION, [True])
      m_html, m_status, m_url_redirect = self.fetch(p_url, p_custom_proxy, headers)

      m_request_handler.close()
      del m_request_handler
      if m_html == "" or m_status != 200:
        return str(p_url), False, m_status
      else:
        return helper_method.on_clean_url(str(m_url_redirect)), True, str(m_html)

    except Exception as ex:
      print(ex)
      return p_url, False, None

  def request_server_post(self, url, data=None, params=None, timeout=1000):
    try:
      crypto = crypto_handler.get_instance()
      secret_token = crypto.generate_secret_token()

      headers = {
        'pSecretToken': f'Bearer {secret_token}',
        'Content-Type': 'application/json'
      }

      response = requests.post(url, json=data, params=params, headers=headers, timeout=timeout)
      response.raise_for_status()
      return response.json(), response.status_code

    except Exception as ex:
      return None, str(ex)

  def request_server_get(self, url, params=None, timeout=1000):
    try:
      crypto = crypto_handler.get_instance()
      secret_token = crypto.generate_secret_token()

      headers = {
        'pSecretToken': f'{secret_token}'
      }

      response = requests.get(url, params=params, headers=headers, timeout=timeout, allow_redirects=True)
      response.raise_for_status()
      return response.content, response.status_code

    except Exception as ex:
      return None, str(ex)

  def load_header(self, p_url, p_custom_proxy):
    m_request_handler, headers = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_CREATE_SESSION, [True])

    try:
      headers = {TOR_KEYS.S_USER_AGENT: CRAWL_SETTINGS_CONSTANTS.S_USER_AGENT}
      with m_request_handler.head(p_url, headers=headers, timeout=(CRAWL_SETTINGS_CONSTANTS.S_HEADER_TIMEOUT, CRAWL_SETTINGS_CONSTANTS.S_HEADER_TIMEOUT), proxies=p_custom_proxy, allow_redirects=True, verify=False) as page:
        m_request_handler.close()
        gc.collect()
        return True, page.headers

    except Exception as ex:
      m_request_handler.close()
      gc.collect()
      return False, None
