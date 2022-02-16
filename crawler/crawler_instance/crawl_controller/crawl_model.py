# Local Libraries
import json

from crawler.crawler_instance.constants import app_status
from crawler.crawler_instance.constants.app_status import CRAWL_STATUS
from crawler.crawler_instance.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.crawler_instance.constants.keys import CRAWL_MODEL_KEYS
from crawler.crawler_instance.constants.strings import STRINGS, MANAGE_CRAWLER_MESSAGES, ERROR_MESSAGES
from crawler.crawler_instance.crawl_controller.crawl_enums import CRAWL_MODEL_COMMANDS
from crawler.crawler_services.crawler_services.elastic_manager.elastic_controller import elastic_controller
from crawler.crawler_services.crawler_services.elastic_manager.elastic_enums import ELASTIC_CRUD_COMMANDS, ELASTIC_REQUEST_COMMANDS
from crawler.crawler_services.crawler_services.url_duplication_manager.url_duplication_controller import url_duplication_controller
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler
from crawler.crawler_instance.local_shared_model.backup_model import backup_model
from crawler.crawler_instance.local_shared_model.url_model import url_model
from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGODB_COMMANDS, MONGO_CRUD
from crawler.crawler_services.helper_services.helper_method import helper_method
from crawler.crawler_services.crawler_services.mongo_manager.mongo_controller import mongo_controller


# URL Queue Manager
class crawl_model(request_handler):

    # Local Queues
    __m_url_queue = {}
    __m_active_queue_keys = []
    __m_inactive_queue_keys = []

    # Helper Methods
    def __init__(self):
        self.__m_url_queue = dict()

    def __init_duplication_handler(self):
        m_response = mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_READ, [MONGODB_COMMANDS.S_FETCH_CRAWLED_URL, [None], [None]])
        for m_document in m_response:
            url_duplication_controller.get_instance().insert(m_document['m_url'])

    def __calculate_depth(self, p_url, p_base_url_model):
        depth = 1
        new_url_host = helper_method.get_host_url(p_url)
        parent_host = helper_method.get_host_url(p_base_url_model.m_url)

        if new_url_host == parent_host or parent_host == "https://drive.google.com":
            if new_url_host == parent_host:
                depth = p_base_url_model.m_depth + 1
            else:
                depth = CRAWL_SETTINGS_CONSTANTS.S_MAX_ALLOWED_DEPTH - 1

        return depth

    # Insert To Database - Insert URL to database after parsing them
    def __insert_url(self, p_url, p_base_url_model, p_init = False):
        m_url = helper_method.on_clean_url(helper_method.normalize_slashes(p_url + "////"))
        m_url_depth = self.__calculate_depth(m_url, p_base_url_model)

        m_url_host = helper_method.get_host_url(p_url)
        if m_url_host not in self.__m_url_queue.keys():
            if p_init is True:
                if len(self.__m_url_queue) < CRAWL_SETTINGS_CONSTANTS.S_MAX_HOST_QUEUE_SIZE:
                    m_fresh_url_model = url_model(p_url, m_url_depth, p_base_url_model.m_type)
                    if url_duplication_controller.get_instance().verify_content_duplication(m_url_host) is False:
                        url_duplication_controller.get_instance().on_insert_content(m_url_host)
                        url_duplication_controller.get_instance().on_set_parsed_content(m_url_host, False)
                        self.__m_url_queue[m_url_host] = [m_fresh_url_model]
                        self.__m_inactive_queue_keys.append(m_url_host)
                else:
                    self.__save_backup_url_to_drive(p_url, m_url_depth)
                    app_status.CRAWL_STATUS.S_QUEUE_BACKUP_STATUS = True
        elif m_url_host == helper_method.get_host_url(p_base_url_model.m_url) and m_url_depth <= CRAWL_SETTINGS_CONSTANTS.S_MAX_ALLOWED_DEPTH and len(self.__m_url_queue[m_url_host]) < CRAWL_SETTINGS_CONSTANTS.S_MAX_SUBHOST_QUEUE_SIZE:
                self.__m_url_queue[m_url_host].insert(0, url_model(p_url, m_url_depth, p_base_url_model.m_type))

    def __save_backup_url_to_drive(self, p_url, p_url_depth, p_category = None):
        if url_duplication_controller.get_instance().verify_content_duplication(p_url) is False:
            app_status.CRAWL_STATUS.S_QUEUE_BACKUP_STATUS = True
            m_host = helper_method.get_host_url(p_url)
            m_subhost = p_url.replace(m_host, STRINGS.S_EMPTY)
            if p_category is not None:
                m_data = backup_model(m_host, m_subhost, p_url_depth, p_category)
            else:
                m_data = backup_model(m_host, m_subhost, p_url_depth, CRAWL_SETTINGS_CONSTANTS.S_THREAD_CATEGORY_GENERAL)
            mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_UPDATE,[MONGODB_COMMANDS.S_SAVE_BACKUP, [m_data], [True]])
            log.g().s(MANAGE_CRAWLER_MESSAGES.S_BACKUP_PARSED + " : " + str(p_url))
        else:
            url_duplication_controller.get_instance().insert(p_url)

    # Extract Fresh Host URL
    def __get_host_url(self):
        if len(self.__m_inactive_queue_keys) <= 0:
            if CRAWL_STATUS.S_QUEUE_BACKUP_STATUS is True:
                self.__load_backup_url()

        if len(self.__m_inactive_queue_keys) > 0:
            m_url_key = self.__m_inactive_queue_keys.pop(0)
            m_url_model = self.__m_url_queue.get(m_url_key).pop(0)
            self.__m_active_queue_keys.append(m_url_key)

            return True, m_url_model
        else:
            return False, None

    # Extract Sub URL - Extract url in relation to host extracted in above ^ function
    def __get_sub_url(self, p_host_url):
        m_url_host = helper_method.get_host_url(p_host_url)
        if m_url_host in self.__m_url_queue and len(self.__m_url_queue[m_url_host]) > 0:
            m_url_model = self.__m_url_queue.get(m_url_host).pop(0)
            return True, m_url_model
        else:
            self.__m_active_queue_keys.remove(m_url_host)
            self.__m_url_queue.pop(m_url_host, None)

            mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_DELETE, [MONGODB_COMMANDS.S_REMOVE_BACKUP, [m_url_host], [None]])
            mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_CREATE_UNIQUE, [MONGODB_COMMANDS.S_INSERT_CRAWLED_URL, [m_url_host], [None]])
            return False, None

    def __load_backup_url(self):
        try:
            m_data = backup_model(STRINGS.S_EMPTY, STRINGS.S_EMPTY, STRINGS.S_EMPTY, CRAWL_SETTINGS_CONSTANTS.S_THREAD_CATEGORY_GENERAL)
            m_backup_model = mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_READ, [MONGODB_COMMANDS.S_GET_UNPARSED_URL, [m_data], [CRAWL_SETTINGS_CONSTANTS.S_BACKUP_FETCH_LIMIT]])

            m_document_list = []
            m_document_list_id = []
            for m_document in m_backup_model:
                m_document_list.append(m_document)
                m_document_list_id.append(m_document["_id"])

            if len(m_document_list) > 0:
                mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_UPDATE, [MONGODB_COMMANDS.S_SET_BACKUP_URL, [m_document_list_id], [True]])
                for data_item in m_document_list:
                    for m_url_model in data_item[CRAWL_MODEL_KEYS.S_URL_DATA]:
                        p_url = data_item[CRAWL_MODEL_KEYS.S_HOST]
                        if m_url_model[CRAWL_MODEL_KEYS.S_SUB_HOST]!='/':
                            p_url += m_url_model[CRAWL_MODEL_KEYS.S_SUB_HOST]
                        p_depth = int(m_url_model[CRAWL_MODEL_KEYS.S_DEPTH])
                        p_type = data_item['m_catagory'].lower()
                        m_url_host = helper_method.get_host_url(p_url)
                        if m_url_host not in self.__m_url_queue.keys():
                            m_fresh_url_model = url_model(p_url, p_depth, p_type)
                            self.__m_url_queue[m_url_host] = [m_fresh_url_model]
                            self.__m_inactive_queue_keys.append(m_url_host)
                        else:
                            self.__m_url_queue[m_url_host].append(url_model(p_url, p_depth, p_type))

                log.g().i(MANAGE_CRAWLER_MESSAGES.S_LOADING_BACKUP_URL)
                if len(m_document_list) < CRAWL_SETTINGS_CONSTANTS.S_BACKUP_FETCH_LIMIT:
                    log.g().w(MANAGE_CRAWLER_MESSAGES.S_BACKUP_QUEUE_EMPTY)
                    app_status.CRAWL_STATUS.S_QUEUE_BACKUP_STATUS = False
            else:
                log.g().w("W1 : " + ERROR_MESSAGES.S_DATABASE_FETCH_ERROR)
                app_status.CRAWL_STATUS.S_QUEUE_BACKUP_STATUS = False
        except Exception as e:
           log.g().e("Crawl Model E1 : " + str(e))

    def on_reset(self):
        self.__m_url_queue = {}
        self.__m_active_queue_keys = []
        self.__m_inactive_queue_keys = []
        url_duplication_controller.get_instance().clear_filter()

    def __on_save_url(self, p_index_model, p_save_to_mongodb):
        if p_save_to_mongodb is True:
            elastic_controller.get_instance().invoke_trigger(ELASTIC_CRUD_COMMANDS.S_INDEX, [ELASTIC_REQUEST_COMMANDS.S_INDEX, [json.loads(p_index_model.to_json())], [True]])
            log.g().s(MANAGE_CRAWLER_MESSAGES.S_URL_PARSED + STRINGS.S_SEPERATOR + p_index_model.m_base_url_model.m_url)

        for m_url in p_index_model.m_sub_url:
            self.__insert_url(m_url, p_index_model.m_base_url_model)

    def invoke_trigger(self, p_command, p_data=None):
        if p_command == CRAWL_MODEL_COMMANDS.S_GET_HOST_URL:
           return self.__get_host_url()
        if p_command == CRAWL_MODEL_COMMANDS.S_CRAWL_FINISHED_STATUS:
           return self.on_reset()
        if p_command == CRAWL_MODEL_COMMANDS.S_INSERT_URL:
           return self.__on_save_url(p_data[0], p_data[1])
        if p_command == CRAWL_MODEL_COMMANDS.S_INSERT_INIT:
           return self.__insert_url(p_data[0], p_data[1], p_init = True)
        if p_command == CRAWL_MODEL_COMMANDS.S_GET_SUB_URL:
           return self.__get_sub_url(p_data[0])

