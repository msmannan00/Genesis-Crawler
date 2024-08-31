from crawler.constants.app_status import APP_STATUS
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.crawler_services.crawler_services.elastic_manager.elastic_enums import ELASTIC_CONNECTIONS

APP_STATUS.DOCKERIZED_RUN = False
from crawler.constants.strings import TOR_STRINGS
from crawler.crawler_instance.application_controller.application_controller import application_controller
from crawler.crawler_instance.application_controller.application_enums import APPICATION_COMMANDS
from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGO_CONNECTIONS
from crawler.crawler_services.crawler_services.redis_manager.redis_enums import REDIS_CONNECTIONS

try:
  MONGO_CONNECTIONS.S_DATABASE_IP = "localhost"
  TOR_STRINGS.S_SOCKS_HTTPS_PROXY = "socks5h://127.0.0.1:"
  TOR_STRINGS.S_SOCKS_HTTP_PROXY = "socks5h://127.0.0.1:"
  REDIS_CONNECTIONS.S_DATABASE_IP = "localhost"
  REDIS_CONNECTIONS.S_DATABASE_PASSWORD = ""
  MONGO_CONNECTIONS.S_DATABASE_PORT = 27017
  ELASTIC_CONNECTIONS.S_DATABASE_IP = "http://0.0.0.0:8070/crawl_index/"
  # CRAWL_SETTINGS_CONSTANTS.S_START_URL = "https://drive.google.com/uc?export=download&id=19-5Q4VwzLM6nLRVhtoZLG_ZynQ3_ThV7"
  # CRAWL_SETTINGS_CONSTANTS.S_PARSERS_URL = "https://drive.usercontent.google.com/download?id=1OMkk1X-OQpH2tXyD3VmQ77cJQ-BxrUTZ&export=download&authuser=0&confirm=t&uuid=b3c07c03-8755-4acd-b307-b1b78a0ee7ba&at=AO7h07cHHGXbls9nafAROAZTZSDU%3A1725023431358"

  application_controller.get_instance().invoke_triggers(APPICATION_COMMANDS.S_START_APPLICATION_DIRECT)
except Exception as ex:
  pass
