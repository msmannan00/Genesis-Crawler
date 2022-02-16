# Local Imports
import pymongo

from pymongo import WriteConcern

from crawler.crawler_services.constants.strings import MANAGE_MONGO_MESSAGES
from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGO_CRUD, MONGODB_KEYS, MONGO_CONNECTIONS
from crawler.crawler_services.crawler_services.mongo_manager.mongo_request_generator import mongo_request_generator
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler


class mongo_controller(request_handler):
    __instance = None
    __m_connection = None
    __m_mongo_request_generator = None

    # Initializations
    @staticmethod
    def get_instance():
        if mongo_controller.__instance is None:
            mongo_controller()
        return mongo_controller.__instance

    def __init__(self):
        mongo_controller.__instance = self
        self.__m_mongo_request_generator = mongo_request_generator()
        self.__link_connection()

    def __link_connection(self):
        self.__m_connection = pymongo.MongoClient(MONGO_CONNECTIONS.S_DATABASE_IP, MONGO_CONNECTIONS.S_DATABASE_PORT)[MONGO_CONNECTIONS.S_DATABASE_NAME]

    def __create_unique(self, p_data):
        try:
            self.__m_connection[p_data[MONGODB_KEYS.S_DOCUMENT]].with_options(write_concern=WriteConcern(w=0)).insert(p_data[MONGODB_KEYS.S_VALUE])

            return True, MANAGE_MONGO_MESSAGES.S_INSERT_SUCCESS
        except Exception as ex:
            log.g().e(MANAGE_MONGO_MESSAGES.S_INSERT_FAILURE + " : " + str(ex))
            return False, str(ex)

    def __create(self, p_data):
        try:
            self.__m_connection[p_data[MONGODB_KEYS.S_DOCUMENT]].insert(p_data[MONGODB_KEYS.S_VALUE])
            return True, MANAGE_MONGO_MESSAGES.S_INSERT_SUCCESS
        except Exception as ex:
            log.g().e(MANAGE_MONGO_MESSAGES.S_INSERT_FAILURE + " : " + str(ex))
            return False, str(ex)

    def __read(self, p_data, p_limit):
        try:
            if p_limit is not None:
                documents = self.__m_connection[p_data[MONGODB_KEYS.S_DOCUMENT]].find(p_data[MONGODB_KEYS.S_FILTER]).limit(p_limit)
            else:
                documents = self.__m_connection[p_data[MONGODB_KEYS.S_DOCUMENT]].find(p_data[MONGODB_KEYS.S_FILTER])
            return documents
        except Exception as ex:
            log.g().e(MANAGE_MONGO_MESSAGES.S_READ_FAILURE + " : " + str(ex))
            return str(ex)

    def __update(self, p_data, upsert):
        try:
            self.__m_connection[p_data[MONGODB_KEYS.S_DOCUMENT]].update_many(p_data[MONGODB_KEYS.S_FILTER],p_data[MONGODB_KEYS.S_VALUE], upsert=upsert)
            return True, MANAGE_MONGO_MESSAGES.S_UPDATE_SUCCESS

        except Exception as ex:
            log.g().e(MANAGE_MONGO_MESSAGES.S_UPDATE_FAILURE + " : " + str(ex))
            return False, str(ex)

    def __delete(self, p_data):
        try:
            self.__m_connection[p_data[MONGODB_KEYS.S_DOCUMENT]].remove(p_data[MONGODB_KEYS.S_FILTER])
            return True, MANAGE_MONGO_MESSAGES.S_DELETE_SUCCESS
        except Exception as ex:
            log.g().e(MANAGE_MONGO_MESSAGES.S_DELETE_FAILURE + " : " + str(ex))
            return False, str(ex)

    def invoke_trigger(self, p_commands, p_data=None):

        m_request = p_data[0]
        m_data = p_data[1]
        m_param = p_data[2]

        m_request = self.__m_mongo_request_generator.invoke_trigger(m_request, m_data)

        if p_commands == MONGO_CRUD.S_CREATE:
            return self.__create(m_request)
        elif p_commands == MONGO_CRUD.S_READ:
            return self.__read(m_request, m_param[0])
        elif p_commands == MONGO_CRUD.S_UPDATE:
            return self.__update(m_request, m_param[0])
        elif p_commands == MONGO_CRUD.S_DELETE:
            return self.__delete(m_request)
        elif p_commands == MONGO_CRUD.S_CREATE_UNIQUE:
            return self.__create_unique(m_request)
