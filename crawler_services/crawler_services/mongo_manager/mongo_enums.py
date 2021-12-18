import enum

class MONGODB_COMMANDS(enum.Enum):
    S_RESET = -1
    S_CLEAR_DATA_INVOKE = 0
    S_SAVE_BACKUP = 1
    S_SAVE_PARSE_URL = 2
    S_BACKUP_URL = 3
    S_GET_PARSE_URL = 4
    S_FETCH_UNIQUE_HOST = 6
    S_ADD_UNIQUE_HOST = 7
    S_CLEAR_DATA = 8
    S_INSTALL_CRAWLABLE_URL = 9
    S_CLEAR_CRAWLABLE_URL_DATA = 10
    S_GET_CRAWLABLE_URL_DATA = 11
    S_UPDATE_CRAWLABLE_URL_DATA = 12
    S_CLEAR_CACHE = 13
    S_RESET_CRAWLABLE_URL = 14
    S_CLEAR_INDEX = 15
    S_CLEAR_BACKUP = 16
    S_CLEAR_TFIDF = 17
    S_CLEAR_UNIQUE_HOST = 18
    S_REMOVE_BACKUP = 19
    S_GET_UNPARSED_URL = 20
    S_SET_BACKUP_URL = 21
    S_GET_BACKUP_URL = 22
    S_COUNT_CRAWLED_URL = 23

class MONGODB_COLLECTIONS:
    S_INDEX_MODEL = 'index_model'
    S_BACKUP_MODEL = 'backup_model'
    S_UNIQUE_HOST_MODEL = 'unique_host'
    S_TFIDF_MODEL = 'tfidf_model'
    S_CRAWLABLE_URL_MODEL = 'crawlable_url_model'

class MONGO_CRUD(enum.Enum):
    S_CREATE = '1'
    S_READ = '2'
    S_UPDATE = '3'
    S_DELETE = '4'
    S_CREATE_UNIQUE = '5'
    S_COUNT = '6'

class MONGODB_KEYS:
    S_DOCUMENT = 'm_document'
    S_FILTER = 'm_filter'
    S_VALUE = 'm_value'

class MANAGE_USER_MESSAGES:
    S_INSERT_FAILURE = "[1] Something unexpected happened while inserting"
    S_INSERT_SUCCESS = "[2] Document Created Successfully"
    S_UPDATE_FAILURE = "[3] Something unexpected happened while updating"
    S_UPDATE_SUCCESS = "[4] Data Updated Successfully"
    S_DELETE_FAILURE = "[5] Something unexpected happened while deleting"
    S_DELETE_SUCCESS = "[6] Data Deleted Successfully"
    S_READ_FAILURE = "[5] Something unexpected happened while reading"
    S_READ_SUCCESS = "[6] Data Read Successfully"
    S_COUNT_FAILURE = "[1] Something unexpected happened while counting"
