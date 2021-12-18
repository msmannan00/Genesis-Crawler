from crawler_instance.constants.app_status import TOR_STATUS


class STRINGS:
    S_EMPTY = ""
    S_EMPTY_SPACE = " "
    S_SEPERATOR = " : "
    S_UTF8_ENCODING = "utf-8"
    S_ONION_EXTENTION = ".onion"
    S_ISO = "unicode-escape"

class TOR_STRINGS:
    S_SOCKS_HTTP_PROXY = "socks5h://127.0.0.1:"
    S_SOCKS_HTTPS_PROXY = "socks5h://127.0.0.1:"
    S_RELEASE_PORT = 'for /f "tokens=5" %a in (\'netstat -aon ^| find "' + str(TOR_STATUS.S_TOR_CONNECTION_PORT) + '"\') do taskkill /f /pid %a'

class PARSE_STRINGS:
    S_CONTENT_LENGTH_HEADER = 'content-length'

class MESSAGE_STRINGS:
    S_URL_PROCESSING_ERROR = "[1] ERROR PROCESSING"
    S_FILE_PARSED = "[2] Successfully Parsed File"
    S_URL_PARSED = "[3] Successfully Parsed URL"
    S_BACKUP_PARSED = "[4] Successfully Saved Backup URL"
    S_PROCESS_FINISHED_FAILURE = "[5] Processing Finished Failure"
    S_PROCESSING_URL = "[6] Processing URL"
    S_PROCESS_FINISHED_SUCCESS = "[7] Processing Finished Success"
    S_LOW_YIELD_URL = "[8] Low Yield URL"
    S_REINITIALIZING_CRAWLABLE_URL = "[1] REINITIALIZING CRAWLABLE URLS"
    S_LOADING_BACKUP_URL = "[2] Loading Backup URL"
    S_BACKUP_QUEUE_EMPTY = "[3] Backup Queue Empty"

class SPELL_CHECKER_STRINGS:
    S_STOPWORD_LANGUAGE = "english"

class ERROR_MESSAGES:
    S_SINGLETON_EXCEPTION = "This class is a singleton"
    S_DATABASE_FETCH_ERROR = "Database Load Error : Database Empty"
