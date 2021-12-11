from crawler_instance.constants.app_status import TOR_STATUS


class GENERIC_STRINGS:
    S_EMPTY = ""
    S_EMPTY_SPACE = " "
    S_SEPERATOR = " : "
    S_UTF8_ENCODING = "utf-8"
    S_ONION_EXTENTION = ".onion"
    S_ISO = "ISO-8859-1"

class TOR_STRINGS:
    S_SOCKS_HTTP_PROXY = "socks5h://127.0.0.1:"
    S_SOCKS_HTTPS_PROXY = "socks5h://127.0.0.1:"
    S_RELEASE_PORT = 'for /f "tokens=5" %a in (\'netstat -aon ^| find "' + str(TOR_STATUS.S_TOR_CONNECTION_PORT) + '"\') do taskkill /f /pid %a'

class PARSE_STRINGS:
    S_CONTENT_LENGTH_HEADER = 'content-length'

class MESSAGE_STRINGS:
    S_URL_PROCESSING_ERROR = "ERROR PROCESSING"
    S_FILE_PARSED = "[1] Successfully Parsed File"
    S_URL_PARSED = "[1] Successfully Parsed URL"
    S_BACKUP_PARSED = "[1] Successfully Saved Backup URL"
    S_PROCESS_FINISHED_FAILURE = "[1] Processing Finished Failure"
    S_PROCESSING_URL = "Processing URL"
    S_PROCESS_FINISHED_SUCCESS = "[2] Processing Finished Success"

class SPELL_CHECKER_STRINGS:
    S_STOPWORD_LANGUAGE = "english"
