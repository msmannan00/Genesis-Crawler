# Local Imports
import json
import pymongo

from CrawlerInstance.classModels.indexModel import UrlObjectEncoder
from CrawlerInstance.constants import constants
from CrawlerInstance.logManager.logManager import log
from GenesisCrawlerServices.constants import strings
from GenesisCrawlerServices.constants.enums import MONGODB_COMMANDS, MONGODB_COLLECTIONS
from GenesisCrawlerServices.sharedModel.requestHandler import RequestHandler


class mongo_controller(RequestHandler):
    __instance = None
    __m_connection = None

    # Initializations
    @staticmethod
    def get_instance():
        if mongo_controller.__instance is None:
            mongo_controller()
        return mongo_controller.__instance

    def __init__(self):
        mongo_controller.__instance = self
        self.__link_connection()

    def __link_connection(self):
        self.__m_connection = pymongo.MongoClient(constants.S_DATABASE_IP, constants.S_DATABASE_PORT)[constants.S_DATABASE_NAME]

    def __clear_data(self):
        m_collection_index = self.__m_connection[MONGODB_COLLECTIONS.S_INDEX_MODEL.value]
        m_collection_backup = self.__m_connection[MONGODB_COLLECTIONS.S_BACKUP_MODEL.value]
        m_collection_tfidf = self.__m_connection[MONGODB_COLLECTIONS.S_TFIDF_MODEL.value]
        m_collection_m_unique_host = self.__m_connection[MONGODB_COLLECTIONS.S_UNIQUE_HOST_MODEL.value]
        m_collection_index.delete_many({})
        m_collection_backup.delete_many({})
        m_collection_tfidf.delete_many({})
        m_collection_m_unique_host.delete_many({})

    def __get_parsed_url(self):
        m_collection = self.__m_connection[MONGODB_COLLECTIONS.S_INDEX_MODEL.value]
        m_collection_result = m_collection.find()

        return m_collection_result

    def __set_backup_url(self, p_data):
        try:
            m_collection = self.__m_connection[MONGODB_COLLECTIONS.S_BACKUP_MODEL.value]
            myquery = {'m_host': {'$eq': p_data.m_host},
                       'm_catagory': {'$eq': p_data.m_thread_catagory},
                       'm_url_data': {'$not': {'$elemMatch': {'m_sub_host': p_data.m_url_data[0].m_sub_host}}}}
            newvalues = {"$set": {'m_parsing': False},
                         "$addToSet": {'m_url_data': json.loads(UrlObjectEncoder().encode(p_data.m_url_data[0]))}}
            m_collection.update_one(myquery, newvalues, upsert=True)
            log.g().i(strings.S_BACKUP_PARSED + " : " + p_data.m_host + p_data.m_url_data[0].m_sub_host)
        except Exception:
            pass

    def __set_parse_url(self, p_data):
        m_collection = self.__m_connection[MONGODB_COLLECTIONS.S_INDEX_MODEL.value]
        myquery = {'m_url': {'$eq': p_data.m_url}}
        newvalues = {"$set": {'m_title': p_data.m_title,
                              'm_description': p_data.m_description,
                              'm_keyword': p_data.m_correct_keyword,
                              'm_content_type': p_data.m_content_type,
                              # 'm_vid_url': p_data.m_vid_url,
                              # 'm_image_url': json.loads(UrlObjectEncoder().encode(p_data.m_image_url)),
                              # 'm_doc_url': p_data.m_doc_url,
                              'm_score' : json.loads(UrlObjectEncoder().encode(p_data.m_scores)),
                              # 'm_binary_score' : json.loads(UrlObjectEncoder().encode(p_data.m_binary_scores)),
                              # 'm_date': HelperMethod.getMongoDBDate()
                              }}
        m_collection.update_one(myquery, newvalues, upsert=True)

        log.g().i(strings.S_URL_PARSED + str(p_data.m_thread_id) + " : " + p_data.m_base_url_model.m_redirected_host + p_data.m_base_url_model.m_redirected_subhost)

    def __get_backup_url(self, p_data):
        m_collection = self.__m_connection[MONGODB_COLLECTIONS.S_BACKUP_MODEL.value]
        m_document_list = []
        m_document_list_id = []
        if p_data.m_thread_catagory == "default":
            m_collection_result = m_collection.find({'m_parsing': {'$eq': False}}).limit(constants.S_BACKUP_FETCH_LIMIT)
        else:
            m_collection_result = m_collection.find({'m_parsing': {'$eq': False}}).limit(constants.S_BACKUP_FETCH_LIMIT)

        for m_document in m_collection_result:
            m_document_list.append(m_document)
            m_document_list_id.append(m_document["_id"])

        m_collection.update_many({"_id": {"$in": m_document_list_id}},{"$set":{"m_parsing":True}})
        return len(m_document_list) > 0, m_document_list

    def __reset_backup_url(self):
        m_collection = self.__m_connection[MONGODB_COLLECTIONS.S_BACKUP_MODEL.value]
        m_collection.update_many({},{"$set":{"m_parsing":False}})

    def __add_unique_host(self, p_data):
        m_collection = self.__m_connection[MONGODB_COLLECTIONS.S_UNIQUE_HOST_MODEL.value]
        m_collection.insert({'m_host': p_data})

    def __fetch_unique_host(self):
        m_collection = self.__m_connection[MONGODB_COLLECTIONS.S_UNIQUE_HOST_MODEL.value]
        m_collection_result = m_collection.find()
        return m_collection_result

    def invoke_trigger(self, p_commands, p_data=None):
        if p_commands == MONGODB_COMMANDS.S_CLEAR_DATA:
            return self.__clear_data()
        elif p_commands == MONGODB_COMMANDS.S_SAVE_BACKUP:
            return self.__set_backup_url(p_data)
        elif p_commands == MONGODB_COMMANDS.S_SAVE_PARSE_URL:
            return self.__set_parse_url(p_data)
        elif p_commands == MONGODB_COMMANDS.S_BACKUP_URL:
            return self.__get_backup_url(p_data)
        elif p_commands == MONGODB_COMMANDS.S_GET_PARSE_URL:
            return self.__get_parsed_url()
        elif p_commands == MONGODB_COMMANDS.S_RESET_BACKUP_URL:
            return self.__reset_backup_url()
        elif p_commands == MONGODB_COMMANDS.S_HOST_EXISTING:
            return self.__add_unique_host(p_data)
        elif p_commands == MONGODB_COMMANDS.S_FETCH_UNIQUE_HOST:
            return self.__fetch_unique_host()
