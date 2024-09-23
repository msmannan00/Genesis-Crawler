# Local Imports
import requests
import stem as stem
from requests.adapters import HTTPAdapter
from stem.control import Controller
from urllib3 import Retry
from crawler.constants.app_status import APP_STATUS
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.constants.keys import TOR_KEYS
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS, TOR_PROXIES
from crawler.crawler_services.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS
from crawler.crawler_services.helper_services.env_handler import env_handler
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler
from crawler.crawler_instance.tor_controller.tor_enums import TOR_CONTROL_PROXIES
from crawler.crawler_services.helper_services.scheduler import RepeatedTimer
from stem import Signal


class tor_controller(request_handler):
  __instance = None
  __m_controller = []
  __m_session = None
  __redis_controller = None  # Redis controller instance

  @staticmethod
  def get_instance():
    if tor_controller.__instance is None:
      tor_controller()
    return tor_controller.__instance

  def __init__(self):
    tor_controller.__instance = self
    self.m_request_index = 0
    self.__on_init()

  def __on_init(self):
    # Initialize Redis controller instance
    self.__redis_controller = redis_controller.get_instance()

    self.__session = requests.Session()
    retries = Retry(total=1, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    adapter = requests.adapters.HTTPAdapter(pool_connections=1000, pool_maxsize=1000, max_retries=retries)
    self.__session.mount('http://', adapter)

    if APP_STATUS.DOCKERIZED_RUN:
      for connection_controller in TOR_CONTROL_PROXIES:
        m_temp_controller = Controller(stem.socket.ControlPort(connection_controller["proxy"], connection_controller["port"]))
        m_temp_controller.authenticate(env_handler.get_instance().env('TOR_PASSWORD'))
        self.__m_controller.append(m_temp_controller)
        RepeatedTimer(CRAWL_SETTINGS_CONSTANTS.S_TOR_NEW_CIRCUIT_INVOKE_DELAY, self.__invoke_new_circuit, False, m_temp_controller)
        self.__invoke_new_circuit(m_temp_controller)

  def __invoke_new_circuit(self, m_temp_controller):
    try:
      m_temp_controller.signal(Signal.NEWNYM)
    except Exception as ex:
      print(ex, flush=True)
      pass

  # Tor Helper Methods
  def __on_create_session(self, p_tor_based):
    headers = {
      TOR_KEYS.S_USER_AGENT: CRAWL_SETTINGS_CONSTANTS.S_USER_AGENT,
      'Cache-Control': 'no-cache'
    } if p_tor_based else {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
      'Cache-Control': 'no-cache'
    }
    return self.__session, headers

  def __on_proxy(self):
    if not APP_STATUS.DOCKERIZED_RUN:
      proxies = {
        "http": "socks5h://localhost:9150",
        "https": "socks5h://localhost:9150"
      }
      return proxies, 100
    else:

      current_index = int(self.__redis_controller.invoke_trigger(REDIS_COMMANDS.S_GET_INT, ["tor_queue_index", -1, None])) + 1
      self.__redis_controller.invoke_trigger(REDIS_COMMANDS.S_SET_INT, ["tor_queue_index", current_index, None])

      return TOR_PROXIES[current_index % len(TOR_PROXIES)], current_index % len(TOR_PROXIES)

  # Request Triggers
  def invoke_trigger(self, p_command, p_data=None):
    if p_command == TOR_COMMANDS.S_CREATE_SESSION:
      return self.__on_create_session(p_data[0])
    elif p_command == TOR_COMMANDS.S_PROXY:
      return self.__on_proxy()