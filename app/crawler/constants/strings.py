from crawler.constants.constant import TOR_CONNECTION_CONSTANTS


class STRINGS:
    S_EMPTY = ""
    S_EMPTY_SPACE = " "
    S_SEPERATOR = " : "
    S_UTF8_ENCODING = "utf-8"
    S_ONION_EXTENTION = ".onion"
    S_ISO = "unicode-escape"


class TOR_STRINGS:
    S_SOCKS_HTTP_PROXY = "socks5h://10.0.0.6:"
    S_SOCKS_HTTPS_PROXY = "socks5h://10.0.0.6:"
    S_RELEASE_PORT = 'for /f "tokens=5" %a in (\'netstat -aon ^| find "' + str(TOR_CONNECTION_CONSTANTS.S_TOR_CONNECTION_PORT) + '"\') do taskkill /f /pid %a'


class PARSE_STRINGS:
    S_CONTENT_LENGTH_HEADER = 'content-length'


class MANAGE_CRAWLER_MESSAGES:
    S_APPLICATION_STARTING = "[0] ----------------------- APPLICATION STARTING -----------------------"
    S_WEB_REQUEST_PROCESSING_ERROR = "[1] Error Fetching response from server"
    S_FILE_PARSED = "[2] Successfully Parsed File"
    S_LOW_YIELD_URL = "[3] Low Yield URL"
    S_REINITIALIZING_CRAWLABLE_URL = "[4] Re-initializing Crawlable URL"
    S_INSTALLED_URL = "[5] Successfully Installed URL"
    S_LOCAL_URL_PARSED = "[6] Successfully Parsed Local URL"
    S_UNIQUE_URL_CACHE_LOAD_FAILURE = "[7] Unique URL Duplication Handler Failure"
    S_ELASTIC_ERROR = "[8] Elastic Commands Failed"
    S_SINGLETON_EXCEPTION = "[9] This class is a singleton"
    S_LOCAL_URL_PARSED_FAILED = "[10] Error during loading Local URL"
    S_INTERNET_CONNECTION_ISSUE = "[11] internet connection issue ..."
    S_PARSING_STARTING = "[12] URL parsing started"
    S_DUPLICATE_CONTENT = "[14] Dupicate URL Content"
    S_DUPLICATE_HOST_CONTENT = "[15] Dupicate Host Content"
    S_TOO_MANY_FAILURE = "[16] Too many host failure droping"
    S_DUPLICATE_HOST_HASH = "[16] Dupicate Host Hash"


class MANAGE_MONGO_MESSAGES:
    S_INSERT_FAILURE = "[1] Something unexpected happened while inserting"
    S_INSERT_SUCCESS = "[2] Document Created Successfully"
    S_UPDATE_FAILURE = "[3] Something unexpected happened while updating"
    S_UPDATE_SUCCESS = "[4] Data Updated Successfully"
    S_DELETE_FAILURE = "[5] Something unexpected happened while deleting"
    S_DELETE_SUCCESS = "[6] Data Deleted Successfully"
    S_READ_FAILURE = "[7] Something unexpected happened while reading"
    S_READ_SUCCESS = "[8] Data Read Successfully"
    S_COUNT_FAILURE = "[9] Something unexpected happened while counting"


class MANAGE_ELASTIC_MESSAGES:
    S_REQUEST_FAILURE = "[1] Something happened while connecting to elastic server"
    S_REQUEST_SUCCESS = "[2] Elastic server successfully sent a response"
