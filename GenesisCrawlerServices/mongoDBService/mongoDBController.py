# Local Imports
import json
import pymongo

from CrawlerInstance.classModels.IndexModel import UrlObjectEncoder
from CrawlerInstance.constants import constants
from CrawlerInstance.logManager.LogManager import log
from GenesisCrawlerServices.constants import strings
from GenesisCrawlerServices.constants.enums import MongoDBCommands
from GenesisCrawlerServices.helperService.HelperMethod import HelperMethod


class mongoDBController:
    __instance = None
    m_connection = None

    # Initializations
    @staticmethod
    def getInstance():
        if mongoDBController.__instance is None:
            mongoDBController()
        return mongoDBController.__instance

    def __init__(self):
        mongoDBController.__instance = self
        self.linkConnection()

    def linkConnection(self):
        self.m_connection = pymongo.MongoClient(constants.m_mongoDB_ip, constants.m_mongoDB_port)[constants.m_mongoDB_database]

    def clearDataInvoke(self):
        m_collection_index = self.m_connection[strings.MongoDB_index_model]
        m_collection_backup = self.m_connection[strings.MongoDB_backup_model]
        m_collection_tfidf = self.m_connection[strings.MongoDB_tfidf_model]
        m_collection_index.delete_many({})
        m_collection_backup.delete_many({})
        m_collection_tfidf.delete_many({})

    def getParsedURL(self):
        m_collection = self.m_connection[strings.MongoDB_index_model]
        m_collection_result = m_collection.find().limit(constants.m_mongoDB_index_url_fetch_limit)
        # m_collection_result.collection.remove()

        return m_collection_result.collection

    def getUniqueTitle(self):
        m_collection = self.m_connection[strings.MongoDB_index_model]
        m_url_list = []
        for m_document in m_collection.distinct("m_base_url_model.m_redirected_host"):
            m_url_list.append(m_document)

        return m_url_list

    def getUniqueCatagories(self):
        m_collection = self.m_connection[strings.MongoDB_backup_model]
        m_url_list = []
        for m_document in m_collection.distinct("m_catagory"):
            m_url_list.append(m_document)

        return m_url_list

    def setBackupURL(self, p_data):
        try:
            m_collection = self.m_connection[strings.MongoDB_backup_model]
            myquery = {'m_host': {'$eq': p_data.m_host},
                       'm_catagory': {'$eq': p_data.m_thread_catagory},
                       'm_url_data': {'$not': {'$elemMatch': {'m_sub_host': p_data.m_url_data[0].m_sub_host}}}}
            newvalues = {"$addToSet": {'m_url_data': json.loads(UrlObjectEncoder().encode(p_data.m_url_data[0]))}}
            m_collection.update_one(myquery, newvalues, upsert=True)
            log.g().i(strings.backup_parsed + " : " + p_data.m_host + p_data.m_url_data[0].m_sub_host)
        except Exception as e:
            print("fuck")

    def setParseURL(self, p_data):
        m_collection = self.m_connection[strings.MongoDB_index_model]
        myquery = {'m_url': {'$eq': p_data.m_url}}
        newvalues = {"$set": {'m_title': p_data.m_title,
                              'm_description': p_data.m_description,
                              'm_content_type': p_data.m_content_type[0],
                              'm_vid_url': p_data.m_vid_url,
                              'm_image_url': p_data.m_image_url,
                              'm_doc_url': p_data.m_doc_url,
                              'm_score' : json.loads(UrlObjectEncoder().encode(p_data.getTFIDFModel())),
                              'm_date': HelperMethod.getMongoDBDate()}}
        m_collection.update_one(myquery, newvalues, upsert=True)

        log.g().i(strings.url_parsed + " : " + str(p_data.m_thread_id) + " : " + p_data.m_base_url_model.m_redirected_host + p_data.m_base_url_model.m_redirected_subhost)

    def getBackupURL(self, p_data):
        m_collection = self.m_connection[strings.MongoDB_backup_model]
        m_document_list = []
        m_document_list_id = []
        if p_data.m_thread_catagory == "default":
            m_collection_result = m_collection.find().limit(constants.m_mongoDB_backup_url_fetch_limit)
        else:
            m_collection_result = m_collection.find({'m_catagory': {'$eq': p_data.m_thread_catagory}}).limit(constants.m_mongoDB_backup_url_fetch_limit)

        for m_document in m_collection_result:
            m_document_list.append(m_document)
            m_document_list_id.append(m_document["_id"])

        m_collection.delete_many({"_id": {"$in": m_document_list_id}})
        return len(m_document_list) > 0, m_document_list

    def onRequest(self, p_commands, p_data):
        if p_commands == MongoDBCommands.mongoDB_clear_data_invoke:
            return self.clearDataInvoke()
        elif p_commands == MongoDBCommands.mongoDB_save_backup_url:
            return self.setBackupURL(p_data)
        elif p_commands == MongoDBCommands.mongoDB_save_parse_url:
            return self.setParseURL(p_data)
        elif p_commands == MongoDBCommands.mongoDB_get_backup_url:
            return self.getBackupURL(p_data)
        elif p_commands == MongoDBCommands.mongoDB_get_unique_title:
            return self.getUniqueTitle()
        elif p_commands == MongoDBCommands.mongoDB_get_unique_category:
            return self.getUniqueCatagories()
        elif p_commands == MongoDBCommands.mongoDB_get_parsed_url:
            return self.getParsedURL()
