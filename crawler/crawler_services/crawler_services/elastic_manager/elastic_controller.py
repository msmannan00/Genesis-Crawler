# Local Imports
import json

from raven.transport import requests

from crawler.crawler_instance.constants.strings import MANAGE_CRAWLER_MESSAGES
from crawler.crawler_services.constants.strings import MANAGE_ELASTIC_MESSAGES
from crawler.crawler_services.crawler_services.elastic_manager.elastic_enums import ELASTIC_CONNECTIONS
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler


class elastic_controller(request_handler):
    __instance = None

    # Initializations
    @staticmethod
    def get_instance():
        if elastic_controller.__instance is None:
            elastic_controller()
        return elastic_controller.__instance

    def __init__(self):
        elastic_controller.__instance = self

    def __post_data(self,p_commands, p_data):
        try:
            m_json_data = json.dumps(p_data)
            m_post_object = {'pRequestCommand': p_commands, "pRequestData": m_json_data}
            m_response = requests.post(ELASTIC_CONNECTIONS.S_DATABASE_IP, data=m_post_object)
            m_data = json.loads(m_response.text)
            m_status =  m_data[0]
            m_data = m_data[1]
            if  m_status is False:
                log.g().e(MANAGE_ELASTIC_MESSAGES.S_REQUEST_FAILURE + " : " + str(m_data))
            elif m_data is not None:
                m_data = m_data['hits']['hits']
            return m_status, m_data
        except Exception as ex:
            log.g().e(MANAGE_CRAWLER_MESSAGES.S_ELASTIC_ERROR + " : " + str(ex))
            return False, None

    def invoke_trigger(self, p_commands, p_data=None):
        return self.__post_data(p_commands, p_data)
