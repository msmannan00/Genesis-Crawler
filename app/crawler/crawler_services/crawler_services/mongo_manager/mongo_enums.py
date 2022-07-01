import enum


class MONGODB_COMMANDS(enum.Enum):
    S_INSTALL_CRAWLABLE_URL = 1
    S_GET_CRAWLABLE_URL_DATA = 2
    S_RESET_CRAWLABLE_URL = 3
    S_REMOVE_DEAD_CRAWLABLE_URL = 4
    S_CLOSE_INDEX_ON_COMPLETE = 5
    S_UPDATE_INDEX = 6
    S_GET_INDEX = 7


class MONGODB_COLLECTIONS:
    S_MONGO_INDEX_MODEL = 'index_model'


class MONGO_CONNECTIONS:
    S_DATABASE_NAME = 'genbot-crawler'
    S_DATABASE_PORT = 27017
    S_DATABASE_IP = 'mongo'


class MONGO_CRUD(enum.Enum):
    S_CREATE = '1'
    S_READ = '2'
    S_UPDATE = '3'
    S_DELETE = '4'
    S_RESET = '5'
    S_COUNT = '6'


class MONGODB_KEYS:
    S_DOCUMENT = 'm_document'
    S_FILTER = 'm_filter'
    S_VALUE = 'm_value'
