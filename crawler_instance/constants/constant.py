class RAW_PATH_CONSTANTS:

    S_PROJECT_PATH = "C:\\Workspace\\Genesis-Crawler"
    S_RAW_PATH = S_PROJECT_PATH + "\\"
    S_DATASET_PATH = "/genesis_crawler_services/raw/crawled_classifier_websites.csv"
    S_SIGWIN_PATH = S_PROJECT_PATH + "/libs/cygwin64/bin/bash.exe --login"
    S_CRAWLER_IMAGE_CACHE_PATH = S_PROJECT_PATH + "\\crawler_instance\\raw\\"

class TOR_CONSTANTS:

    S_SHELL_CONFIG_PATH = RAW_PATH_CONSTANTS.S_PROJECT_PATH + "\\genesis_crawler_services\\raw\\config_script.sh"
    S_TOR_PATH = RAW_PATH_CONSTANTS.S_PROJECT_PATH + "\\genesis_onion_proxy"

class CRAWL_SETTINGS_CONSTANTS:

    # Allowed Extentions
    S_DOC_TYPES = [".pdf", ".msword", ".document", ".docx", ".doc"]

    # Local URL
    S_START_URL = "https://drive.google.com/uc?export=download&id=1ZG7D2NsI-NrVyp3SDq9q4zcrgFi3jhaG"

    # Total Thread Instances Allowed
    S_MAX_THREAD_COUNT_PER_INSTANCE = 1

    # Time Delay to Invoke New Url Requests
    S_ICRAWL_INVOKE_DELAY = 2
    S_CRAWLER_INVOKE_DELAY = 2
    S_ICRAWL_IMAGE_INVOKE_DELAY = 2
    S_TOR_NEW_CIRCUIT_INVOKE_DELAY = 60

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

    # Max Static Images
    S_STATIC_PARSER_LIST_MAX_SIZE = 10
    S_MIN_CONTENT_LENGTH = 50000

