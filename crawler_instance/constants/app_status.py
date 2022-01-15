# External DB Queue Exists And Not Empty
import sys

from crawler_instance.tor_controller.tor_enums import TOR_STATUS

class APP_STATUS:
    S_USER_CRAWL_ONLY = True

class CRAWL_STATUS:
    S_QUEUE_BACKUP_STATUS = True

class TOR_STATUS:
    S_TOR_STATUS = TOR_STATUS.S_READY
    S_TOR_CONNECTION_PORT = 9052
    S_TOR_CONTROL_PORT = 9053
