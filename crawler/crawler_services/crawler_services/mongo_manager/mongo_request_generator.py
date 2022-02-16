import json

from crawler.crawler_instance.i_crawl_crawler.i_crawl_enums import CRAWL_STATUS_TYPE
from crawler.crawler_instance.local_shared_model.index_model import UrlObjectEncoder
from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGODB_KEYS, MONGODB_COLLECTIONS, MONGODB_COMMANDS
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler


class mongo_request_generator(request_handler):

    def __init__(self):
        pass

    def __on_set_backup_url(self, p_data):
        return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_BACKUP_MODEL, MONGODB_KEYS.S_VALUE:{"m_host": p_data.m_host, "m_parsing": False, "m_catagory": p_data.m_catagory}}

    def __on_set_backup_parsable(self, p_document_list_id):
        return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_BACKUP_MODEL, MONGODB_KEYS.S_FILTER:{"_id": {"$in": p_document_list_id}}, MONGODB_KEYS.S_VALUE:{"$set":{"m_parsing":True}}}

    def __on_clear_backup(self):
        return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_BACKUP_MODEL, MONGODB_KEYS.S_FILTER:{}}

    def __on_clear_crawl_info(self):
        return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_CRAWLABLE_URL_MODEL, MONGODB_KEYS.S_FILTER:{}}

    def __on_reset_crawl_info(self):
        return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_CRAWLABLE_URL_MODEL, MONGODB_KEYS.S_FILTER:{}, MONGODB_KEYS.S_VALUE:{'$set': { 'm_live':False}}}

    def __on_get_unparsed_url(self):
        return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_BACKUP_MODEL, MONGODB_KEYS.S_FILTER: {"m_parsing": {"$eq": False}}}

    def __on_reset_backup_url(self):
        return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_BACKUP_MODEL, MONGODB_KEYS.S_FILTER:{}, MONGODB_KEYS.S_VALUE:{"$set":{"m_parsing":False}}}

    def __on_set_backup_url(self, p_data):
        return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_BACKUP_MODEL, MONGODB_KEYS.S_FILTER:{'m_host': {'$eq': p_data.m_host}, 'm_catagory': {'$eq': p_data.m_category}, 'm_url_data': {'$not': {'$elemMatch': {'m_sub_host': p_data.m_url_data[0].m_sub_host}}}}, MONGODB_KEYS.S_VALUE:{"$set": {'m_parsing': False}, "$addToSet": {'m_url_data': json.loads(UrlObjectEncoder().encode(p_data.m_url_data[0]))}}}

    def __on_install_crawlable_url(self, p_url):
        return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_CRAWLABLE_URL_MODEL, MONGODB_KEYS.S_FILTER:{'m_url': {'$eq':p_url}}, MONGODB_KEYS.S_VALUE:{'$setOnInsert': {'m_failed_hits': 0, 'm_duplicate_hits': 0, 'm_low_yield_hits': 0}, '$set': {'m_live': True}}}

    def __on_fetch_crawlable_url(self):
        return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_CRAWLABLE_URL_MODEL, MONGODB_KEYS.S_FILTER:{'m_live': True}}

    def __on_update_crawlable_url(self, p_url, p_crawl_status_type):
        m_duplicate = 0
        m_failed = 0
        m_low_yield = 0
        if p_crawl_status_type == CRAWL_STATUS_TYPE.S_DUPLICATE:
            m_duplicate += 1
        if p_crawl_status_type == CRAWL_STATUS_TYPE.S_LOW_YIELD:
            m_low_yield += 1
        if p_crawl_status_type == CRAWL_STATUS_TYPE.S_FETCH_ERROR:
            m_failed += 1

        return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_CRAWLABLE_URL_MODEL, MONGODB_KEYS.S_FILTER: {'m_url': {'$eq': p_url}}, MONGODB_KEYS.S_VALUE: { '$inc': {'m_failed_hits': m_failed, 'm_low_yield_hits': m_low_yield, 'm_duplicate_hits': m_duplicate}}}

    def __on_remove_backup(self, p_url):
        return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_BACKUP_MODEL,MONGODB_KEYS.S_FILTER: {"m_host": {"$eq": p_url[0]}}}

    def __on_get_crawl_count(self):
        return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_BACKUP_MODEL, MONGODB_KEYS.S_FILTER:{}}

    def __on_remove_dead_crawlable_url(self):
        return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_CRAWLABLE_URL_MODEL, MONGODB_KEYS.S_FILTER: {"m_live": {"$eq": False}}}

    def __on_insert_crawled_url(self, p_url):
        return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_CRAWLED_URL_MODEL, MONGODB_KEYS.S_VALUE: {"m_url": p_url[0]}}

    def __on_fetch_crawled_url(self):
        return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_CRAWLED_URL_MODEL, MONGODB_KEYS.S_FILTER: {}}

    def __on_clear_crawled_url(self):
        return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_CRAWLED_URL_MODEL, MONGODB_KEYS.S_FILTER: {}}

    def invoke_trigger(self, p_commands, p_data=None):
        if p_commands == MONGODB_COMMANDS.S_CLEAR_BACKUP:
            return self.__on_clear_backup()
        if p_commands == MONGODB_COMMANDS.S_RESET:
            return self.__on_reset_backup_url()
        elif p_commands == MONGODB_COMMANDS.S_SAVE_BACKUP:
            return self.__on_set_backup_url(p_data[0])
        elif p_commands == MONGODB_COMMANDS.S_CLEAR_CRAWLABLE_URL_DATA:
            return self.__on_clear_crawl_info()
        elif p_commands == MONGODB_COMMANDS.S_RESET_CRAWLABLE_URL:
            return self.__on_reset_crawl_info()
        elif p_commands == MONGODB_COMMANDS.S_INSTALL_CRAWLABLE_URL:
            return self.__on_install_crawlable_url(p_data[0])
        elif p_commands == MONGODB_COMMANDS.S_GET_CRAWLABLE_URL_DATA:
            return self.__on_fetch_crawlable_url()
        elif p_commands == MONGODB_COMMANDS.S_UPDATE_CRAWLABLE_URL_DATA:
            return self.__on_update_crawlable_url(p_data[0], p_data[1])
        elif p_commands == MONGODB_COMMANDS.S_REMOVE_BACKUP:
            return self.__on_remove_backup(p_data)
        elif p_commands == MONGODB_COMMANDS.S_GET_UNPARSED_URL:
            return self.__on_get_unparsed_url()
        elif p_commands == MONGODB_COMMANDS.S_SET_BACKUP_URL:
            return self.__on_set_backup_parsable(p_data[0])
        elif p_commands == MONGODB_COMMANDS.S_COUNT_CRAWLED_URL:
            return self.__on_get_crawl_count()
        elif p_commands == MONGODB_COMMANDS.S_REMOVE_DEAD_CRAWLABLE_URL:
            return self.__on_remove_dead_crawlable_url()
        elif p_commands == MONGODB_COMMANDS.S_INSERT_CRAWLED_URL:
            return self.__on_insert_crawled_url(p_data)
        elif p_commands == MONGODB_COMMANDS.S_FETCH_CRAWLED_URL:
            return self.__on_fetch_crawled_url()
        elif p_commands == MONGODB_COMMANDS.S_CLEAR_CRAWLED_URL:
            return self.__on_clear_crawled_url()


