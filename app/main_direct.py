from crawler.constants.app_status import APP_STATUS
from crawler.constants.strings import TOR_STRINGS
from crawler.crawler_instance.application_controller.application_controller import application_controller
from crawler.crawler_instance.application_controller.application_enums import APPICATION_COMMANDS
from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGO_CONNECTIONS

try:
    MONGO_CONNECTIONS.S_DATABASE_IP = "localhost"
    APP_STATUS.DOCKERIZED_RUN = False
    TOR_STRINGS.S_SOCKS_HTTPS_PROXY = "socks5h://127.0.0.1:"
    TOR_STRINGS.S_SOCKS_HTTP_PROXY = "socks5h://127.0.0.1:"

    application_controller.get_instance().invoke_triggers(APPICATION_COMMANDS.S_START_APPLICATION_DIRECT)
except KeyboardInterrupt:
    pass
