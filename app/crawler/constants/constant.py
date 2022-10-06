from pathlib import Path


class RAW_PATH_CONSTANTS:
    S_SIGWIN_PATH = str(Path(__file__).parent.parent.parent.parent.parent) + "/cygwin64/bin/bash.exe --login"
    S_PROJECT_PATH = str(Path(__file__).parent.parent)
    S_CRAWLER_IMAGE_CACHE_PATH = str(Path(__file__).parent.parent.parent) + "/global_raw/crawler_image_cache/"


class NETWORK_MONITOR:
    S_PING_URL = "https://duckduckgo.com"


class LOG_CONSTANTS:
    S_LOGS_KEY = "70be40974f068bb7abd5b441b0b8386b"


class TOR_CONSTANTS:
    S_SHELL_CONFIG_PATH = str(Path(__file__).parent.parent.parent) + "/crawler/crawler_services/raw/config_script.sh"
    S_TOR_PATH = str(Path(__file__).parent.parent.parent.parent) + "/tor_proxy"
    S_TOR_PROXY_PATH = S_TOR_PATH + "/9052"


class TOR_CONNECTION_CONSTANTS:
    S_TOR_CONNECTION_PORT = 9052
    S_TOR_CONTROL_PORT = 9053


class SPELL_CHECK_CONSTANTS:
    S_DICTIONARY_PATH = RAW_PATH_CONSTANTS.S_PROJECT_PATH + "/crawler_services/raw/dictionary"
    S_DICTIONARY_MINI_PATH = RAW_PATH_CONSTANTS.S_PROJECT_PATH + "/crawler_services/raw/dictionary_small"


class CLASSIFIER_CONSTANTS:
    S_CLASSIFIER_PICKLE_PATH = "/crawler_services/raw/classifier_output/web_classifier.sav"
    S_VECTORIZER_PATH = "/crawler_services/raw/classifier_output/class_vectorizer.csv"
    S_SELECTKBEST_PATH = "/crawler_services/raw/classifier_output/feature_vector.sav"
    S_IMAGE_CLASSIFIER_PATH = str(Path(__file__).parent.parent.parent) + "/libs/nudenet/.NudeNet/classifier_lite.onnx"


class CRAWL_SETTINGS_CONSTANTS:
    # Allowed Extentions
    S_DOC_TYPES = [".pdf", ".msword", ".document", ".docx", ".doc"]

    # Local URL
    S_START_URL = "https://167.86.99.31/crawl_url"
    # S_START_URL = "https://drive.google.com/uc?export=download&id=1ZG7D2NsI-NrVyp3SDq9q4zcrgFi3jhaG"

    # Total Thread Instances Allowed
    S_UPDATE_STATUS_TIMEOUT = 200
    S_UPDATE_NETWORK_STATUS_TIMEOUT = 60
    S_UPDATE_STATUS_URL = "https://167.86.99.31/update_status/?pRequest=m_crawler"

    # Time Delay to Invoke New Url Requests
    S_ICRAWL_IMAGE_INVOKE_DELAY = 2
    S_TOR_NEW_CIRCUIT_INVOKE_DELAY = 600
    S_LOCAL_FILE_CRAWLER_INVOKE_DELAY = 1
    S_LOCAL_FILE_CRAWLER_INVOKE_DELAY_LONG = 10
    S_CELERY_RESTART_DELAY = 3600
    S_CELERY_INFO_DELAY = 60

    # Max Allowed Depth
    S_MAX_ALLOWED_DEPTH = 2
    S_DEFAULT_DEPTH = 0

    # Max URL Timeout
    S_URL_TIMEOUT = 60
    S_HEADER_TIMEOUT = 30

    # Max Host Queue Size
    S_MAX_HOST_QUEUE_SIZE = 100
    S_MAX_SUBHOST_QUEUE_SIZE = 500
    S_MAX_CRAWL_SIZE = 100

    # Max URL Size
    S_MAX_URL_SIZE = 480

    # Min Image Content Size
    S_MIN_CONTENT_LENGTH = 50000

    # User Agent
    S_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'

    # Crawl Catagory
    S_THREAD_CATEGORY_GENERAL = "general"
    S_THREAD_CATEGORY_UNKNOWN = "unknown"

    # Max Static Images
    S_STATIC_PARSER_LIST_MAX_SIZE = 10

    # Max Thread Size
    S_MAX_THREAD_COUNT = 150
