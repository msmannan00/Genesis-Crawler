from pathlib import Path


class RAW_PATH_CONSTANTS:

    S_SIGWIN_PATH = str(Path(__file__).parent.parent.parent.parent.parent) + "/cygwin64/bin/bash.exe --login"
    S_PROJECT_PATH = str(Path(__file__).parent.parent.parent.parent)
    S_RAW_PATH = S_PROJECT_PATH + "/"
    S_DATASET_PATH = "/crawler/crawler_services/raw/crawled_classifier_websites.csv"
    S_CRAWLER_IMAGE_CACHE_PATH = str(Path(__file__).parent.parent.parent.parent.parent) + "/crawler_image_cache/"
    S_LOGS_DIRECTORY = str(Path(__file__).parent.parent.parent.parent.parent) +"/logs/"

class TOR_CONSTANTS:

    S_SHELL_CONFIG_PATH = RAW_PATH_CONSTANTS.S_PROJECT_PATH + "/crawler/crawler_services/raw/config_script.sh"
    S_TOR_PATH = RAW_PATH_CONSTANTS.S_PROJECT_PATH + "/genesis_onion_proxy"
    S_TOR_PROXY_PATH = S_TOR_PATH + "/9052"

class CRAWL_SETTINGS_CONSTANTS:

    # Allowed Extentions
    S_DOC_TYPES = [".pdf", ".msword", ".document", ".docx", ".doc"]

    # Local URL
    S_START_URL = "https://drive.google.com/uc?export=download&id=1ZG7D2NsI-NrVyp3SDq9q4zcrgFi3jhaG"

    # Total Thread Instances Allowed
    S_MAX_THREAD_COUNT_PER_INSTANCE = 30

    # Total Thread Instances Allowed
    S_UPDATE_STATUS_TIMEOUT = 300
    S_UPDATE_STATUS_URL = "https://167.86.99.31/update_status/?pRequest=m_crawler"

    # Time Delay to Invoke New Url Requests
    S_ICRAWL_INVOKE_DELAY = 2
    S_CRAWLER_INVOKE_DELAY = 2
    S_ICRAWL_IMAGE_INVOKE_DELAY = 2
    S_TOR_NEW_CIRCUIT_INVOKE_DELAY = 300
    S_LOCAL_FILE_CRAWLER_INVOKE_DELAY = 1
    S_LOCAL_FILE_CRAWLER_INVOKE_DELAY_LONG = 10

    # Max Allowed Depth
    S_MAX_ALLOWED_DEPTH = 2
    S_DEFAULT_DEPTH = 0

    # Max URL Timeout
    S_URL_TIMEOUT = 11170
    S_HEADER_TIMEOUT = 30

    # Max Host Queue Size
    S_MAX_HOST_QUEUE_SIZE = 100
    S_MAX_SUBHOST_QUEUE_SIZE = 100

    # Max URL Size
    S_MAX_URL_SIZE = 480

    # Backup Time
    S_BACKUP_TIME_DELAY = 86400
    S_BACKUP_FETCH_LIMIT = 50

    # Min Image Content Size
    S_MIN_CONTENT_LENGTH = 50000

    # User Agent
    S_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'

    # Crawl Catagory
    S_THREAD_CATEGORY_GENERAL = "general"
    S_THREAD_CATEGORY_UNKNOWN = "unknown"

    # Max Static Images
    S_STATIC_PARSER_LIST_MAX_SIZE = 10
    S_MIN_CONTENT_LENGTH = 50000

    # Duplication Fuzzy Logic Score
    S_HOST_DATA_FUZZY_SCORE = 75
    S_SUB_HOST_DATA_FUZZY_SCORE = 50
