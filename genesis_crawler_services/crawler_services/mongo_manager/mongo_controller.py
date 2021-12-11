# Local Imports
import json
import threading

import pymongo

from pymongo import WriteConcern

from crawler_instance.i_crawl_crawler.i_crawl_enums import CRAWL_STATUS_TYPE
from crawler_instance.log_manager.log_controller import log
from crawler_instance.shared_class_model.index_model import UrlObjectEncoder
from genesis_crawler_services.constants.constant import mongo_constants
from genesis_crawler_services.constants.strings import tor_strings
from genesis_crawler_services.crawler_services.mongo_manager.mongo_enums import MONGODB_COMMANDS, MONGODB_COLLECTIONS
from genesis_crawler_services.helper_services.helper_method import helper_method
from genesis_crawler_services.shared_model.request_handler import request_handler


class mongo_controller(request_handler):
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
        self.__m_connection = pymongo.MongoClient(mongo_constants.S_DATABASE_IP, mongo_constants.S_DATABASE_PORT)[mongo_constants.S_DATABASE_NAME]

    def __reset_data(self):
        m_collection = self.__m_connection[MONGODB_COLLECTIONS.S_BACKUP_MODEL]
        m_collection.update_many({},{"$set":{"m_parsing":False}})

    def __clear_data(self):
        m_collection_index = self.__m_connection[MONGODB_COLLECTIONS.S_INDEX_MODEL]
        m_collection_backup = self.__m_connection[MONGODB_COLLECTIONS.S_BACKUP_MODEL]
        m_collection_tfidf = self.__m_connection[MONGODB_COLLECTIONS.S_TFIDF_MODEL]
        m_collection_m_unique_host = self.__m_connection[MONGODB_COLLECTIONS.S_UNIQUE_HOST_MODEL]
        m_collection_index.delete_many({})
        m_collection_backup.delete_many({})
        m_collection_tfidf.delete_many({})
        m_collection_m_unique_host.delete_many({})
        m_collection = self.__m_connection[MONGODB_COLLECTIONS.S_BACKUP_MODEL]
        m_collection.update_many({},{"$set":{"m_parsing":False}})

    def __clear_cache(self):
        m_collection_backup = self.__m_connection[MONGODB_COLLECTIONS.S_BACKUP_MODEL]
        m_collection_m_unique_host = self.__m_connection[MONGODB_COLLECTIONS.S_UNIQUE_HOST_MODEL]
        m_collection_backup.delete_many({})
        m_collection_m_unique_host.delete_many({})

    def __clear_crawl_info(self):
        m_collection_crawlable_url = self.__m_connection[MONGODB_COLLECTIONS.S_CRAWLABLE_URL_MODEL]
        m_collection_crawlable_url.delete_many({})

    def __get_parsed_url(self):
        m_collection = self.__m_connection[MONGODB_COLLECTIONS.S_INDEX_MODEL]
        m_collection_result = m_collection.find()

        return m_collection_result

    def __set_parse_url(self, p_data):
        m_collection = self.__m_connection[MONGODB_COLLECTIONS.S_INDEX_MODEL]
        myquery = {'m_url': {'$eq': p_data.m_base_url_model.m_url}}
        newvalues = {"$set": {'m_title': p_data.m_title,
                              'm_description': p_data.m_description,
                              'm_content_type': p_data.m_content_type,
                              'm_vid_url': p_data.m_videos,
                              'm_images': json.loads(UrlObjectEncoder().encode(p_data.m_images)),
                              'm_doc_url': p_data.m_documents,
                              'm_sub_url': p_data.m_sub_url,
                              'm_validity_score': p_data.m_validity_score,
                              'm_uniary_tfidf_score' : json.loads(UrlObjectEncoder().encode(p_data.m_uniary_tfidf_score)),
                              'm_binary_tfidf_score' : json.loads(UrlObjectEncoder().encode(p_data.m_binary_tfidf_score)),
                              'm_date': helper_method.get_mongodb_date()
                              }}
        m_collection.update_one(myquery, newvalues, upsert=True)

        log.g().i("Successfully Parsed URL : " + p_data.m_base_url_model.m_url + " : " + str(threading.get_native_id()))
        # log.g().i(tor_strings.S_URL_PARSED + " : " + p_data.m_base_url_model.m_url)

    def __get_backup_url(self, p_data):
        m_collection = self.__m_connection[MONGODB_COLLECTIONS.S_BACKUP_MODEL]
        m_document_list = []
        m_document_list_id = []
        if p_data[0].m_category == "default":
            m_collection_result = m_collection.find({'m_parsing': {'$eq': False}}).limit(p_data[1])
        else:
            m_collection_result = m_collection.find({'m_parsing': {'$eq': False}}).limit(p_data[1])

        for m_document in m_collection_result:
            m_document_list.append(m_document)
            m_document_list_id.append(m_document["_id"])

        m_collection.update_many({"_id": {"$in": m_document_list_id}},{"$set":{"m_parsing":True}})
        return len(m_document_list) > 0, m_document_list

    def __set_backup_url(self, p_data):
        try:
            m_collection = self.__m_connection[MONGODB_COLLECTIONS.S_BACKUP_MODEL]
            myquery = {'m_host': {'$eq': p_data.m_host},
                       'm_catagory': {'$eq': p_data.m_category},
                       'm_url_data': {'$not': {'$elemMatch': {'m_sub_host': p_data.m_url_data[0].m_sub_host}}}}
            newvalues = {"$set": {'m_parsing': False},
                         "$addToSet": {'m_url_data': json.loads(UrlObjectEncoder().encode(p_data.m_url_data[0]))}}
            m_collection.update_one(myquery, newvalues, upsert=True)
            log.g().i(tor_strings.S_BACKUP_PARSED + " : " + p_data.m_host + p_data.m_url_data[0].m_sub_host)
        except Exception:
            pass

    def __add_unique_host(self, p_data):
        try:
            m_collection = self.__m_connection[MONGODB_COLLECTIONS.S_UNIQUE_HOST_MODEL]
            m_collection.with_options(write_concern=WriteConcern(w=0)).insert({'m_host': p_data})

            m_collection = self.__m_connection[MONGODB_COLLECTIONS.S_BACKUP_MODEL]
            m_collection.delete_one({'m_host': p_data})
        except Exception:
            pass

    def __install_crawlable_url(self, p_url):
        try:
            m_collection = self.__m_connection[MONGODB_COLLECTIONS.S_CRAWLABLE_URL_MODEL]

            myquery = {'m_url': {'$eq':p_url}}
            newvalues = {'$setOnInsert': { 'm_failed_hits': 0,'m_duplicate_hits': 0,'m_low_yield_hits': 0},
                         '$set': { 'm_live': True}}

            m_collection.update(myquery, newvalues, upsert=True)
            log.g().i(tor_strings.S_INSTALLED_URL + " : " + p_url)

        except Exception as ex:
            pass

    def __reset_crawlable_url(self):
        try:
            m_collection = self.__m_connection[MONGODB_COLLECTIONS.S_CRAWLABLE_URL_MODEL]
            myquery = {}

            newvalues = {'$set': { 'm_live':False}}
            m_collection.update_many(myquery, newvalues)

            log.g().i(tor_strings.S_RESET_CRAWLABLE_URL)

        except Exception as ex:
            pass

    def __update_crawlable_url(self, p_data):
        try:
            m_collection = self.__m_connection[MONGODB_COLLECTIONS.S_CRAWLABLE_URL_MODEL]
            myquery = {'m_url': {'$eq': p_data[0]}}
            m_duplicate = 0
            m_failed = 0
            m_low_yield = 0
            if p_data[1] == CRAWL_STATUS_TYPE.S_DUPLICATE:
                m_duplicate +=1
            if p_data[1] == CRAWL_STATUS_TYPE.S_LOW_YIELD:
                m_low_yield +=1
            if p_data[1] == CRAWL_STATUS_TYPE.S_FETCH_ERROR:
                m_failed +=1

            newvalues = {'$inc': { 'm_failed_hits': m_failed, 'm_low_yield_hits': m_low_yield, 'm_duplicate_hits': m_duplicate}}
            m_collection.update(myquery, newvalues, upsert=True)

            log.g().i(tor_strings.S_UPDATE_URL_STATUS_URL + " : " + p_data[0])

        except Exception as ex:
            pass

    def __fetch_crawlable_url(self):
        m_collection = self.__m_connection[MONGODB_COLLECTIONS.S_CRAWLABLE_URL_MODEL]
        m_url_list = []

        m_collection_result = m_collection.find({'m_live': True})

        for m_document in m_collection_result:
            m_url_list.append(m_document)

        return m_url_list

    def __fetch_unique_host(self):
        m_collection = self.__m_connection[MONGODB_COLLECTIONS.S_UNIQUE_HOST_MODEL]
        m_collection_result = m_collection.find()
        return m_collection_result

    def invoke_trigger(self, p_commands, p_data=None):
        if p_commands == MONGODB_COMMANDS.S_CLEAR_DATA:
            return self.__clear_data()
        if p_commands == MONGODB_COMMANDS.S_RESET:
            return self.__reset_data()
        elif p_commands == MONGODB_COMMANDS.S_SAVE_BACKUP:
            return self.__set_backup_url(p_data)
        elif p_commands == MONGODB_COMMANDS.S_SAVE_PARSE_URL:
            return self.__set_parse_url(p_data)
        elif p_commands == MONGODB_COMMANDS.S_BACKUP_URL:
            return self.__get_backup_url(p_data)
        elif p_commands == MONGODB_COMMANDS.S_GET_PARSE_URL:
            return self.__get_parsed_url()
        elif p_commands == MONGODB_COMMANDS.S_ADD_UNIQUE_HOST:
            return self.__add_unique_host(p_data)
        elif p_commands == MONGODB_COMMANDS.S_FETCH_UNIQUE_HOST:
            return self.__fetch_unique_host()
        elif p_commands == MONGODB_COMMANDS.S_INSTALL_CRAWLABLE_URL:
            return self.__install_crawlable_url(p_data)
        elif p_commands == MONGODB_COMMANDS.S_CLEAR_CRAWLABLE_URL_DATA:
            return self.__clear_crawl_info()
        elif p_commands == MONGODB_COMMANDS.S_GET_CRAWLABLE_URL_DATA:
            return self.__fetch_crawlable_url()
        elif p_commands == MONGODB_COMMANDS.S_UPDATE_CRAWLABLE_URL_DATA:
            return self.__update_crawlable_url(p_data)
        elif p_commands == MONGODB_COMMANDS.S_CLEAR_CACHE:
            return self.__clear_cache()
        elif p_commands == MONGODB_COMMANDS.S_RESET_CRAWLABLE_URL:
            return self.__reset_crawlable_url()

