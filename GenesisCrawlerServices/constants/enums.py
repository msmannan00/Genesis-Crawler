import enum

# HTML Parsing Manager
from CrawlerInstance.constants import constants

class ERROR_MESSAGES(enum.Enum):
    S_SINGLETON_EXCEPTION = "This class is a singleton"
    S_DATABASE_FETCH_ERROR = "Database Load Error : Database Empty"


class INFO_MESSAGES(enum.Enum):
    S_LOADING_BACKUP_URL = "[1] Loading Backup URL"
    S_BACKUP_QUEUE_EMPTY = "Backup Queue Empty"


class PARSE_TAGS(enum.Enum):
    S_TITLE = 1
    S_META = 2
    S_KEYWORD = 3
    S_HEADER = 4
    S_PARAGRAPH = 5
    S_NONE = -1


class CRAWLER_STATUS(enum.Enum):
    S_CLOSED = 0
    S_RUNNING = 1
    S_PAUSE = 2
    S_STOP = 3
    S_BACKUP = 4


class TOR_COMMANDS(enum.Enum):
    S_START = 1
    S_RESTART = 2
    S_GENERATED_CIRCUIT = 3
    S_RELEASE_SESSION = 4
    S_CREATE_SESSION = 5


class TOR_CMD_COMMANDS(enum.Enum):
    S_START = constants.S_SIGWIN_PATH + " " + constants.S_SHELL_CONFIG_PATH + " " + constants.S_TOR_PATH + " " + "build-start-tor"


class TOR_STATUS(enum.Enum):
    S_RUNNING = 1
    S_PAUSE = 2
    S_STOP = 3
    S_READY = 4
    S_START = 5
    S_CLOSE = 6


class MONGODB_COMMANDS(enum.Enum):
    S_CLEAR_DATA = '-1'
    S_CLEAR_DATA_INVOKE = '0'
    S_SAVE_BACKUP = '1'
    S_SAVE_PARSE_URL = '2'
    S_BACKUP_URL = '3'
    S_GET_PARSE_URL = '4'
    S_RESET_BACKUP_URL = '5'
    S_FETCH_UNIQUE_HOST = '6'
    S_HOST_EXISTING = '7'


class MONGODB_COLLECTIONS(enum.Enum):
    S_INDEX_MODEL = 'index_model'
    S_BACKUP_MODEL = 'backup_model'
    S_UNIQUE_HOST_MODEL = 'unique_host'
    S_TFIDF_MODEL = 'tfidf_model'

class TOPIC_CLASSFIER_COMMANDS(enum.Enum):
    S_GENERATE_CLASSIFIER = 1
    S_PREDICT_CLASSIFIER = 2

class TOPIC_CLASSFIER_MODEL(enum.Enum):
    S_PREDICT_CLASSIFIER = 1

class TOPIC_CLASSFIER_TRAINER(enum.Enum):
    S_GENERATE_CLASSIFIER = 1
    S_CLEAN_DATA = 2
