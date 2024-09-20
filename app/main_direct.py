from crawler.constants.app_status import APP_STATUS
from crawler.constants.constant import RAW_PATH_CONSTANTS, CRAWL_SETTINGS_CONSTANTS

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
  RAW_PATH_CONSTANTS.LOG_DIRECTORY = "/logs"
  CRAWL_SETTINGS_CONSTANTS.S_START_URL = "http://localhost:8080//feeder"
  CRAWL_SETTINGS_CONSTANTS.S_PARSERS_URL = "http://localhost:8080//parser"

  application_controller.get_instance().invoke_triggers(APPICATION_COMMANDS.S_START_APPLICATION_DIRECT)
except Exception as ex:
  pass
