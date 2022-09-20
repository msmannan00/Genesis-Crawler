from crawler.constants.keys import REDIS_KEYS
from crawler.constants.strings import MANAGE_CRAWLER_MESSAGES
from crawler.crawler_services.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS


class celery_shared_data:
    __instance = None
    __m_running = False

    # Initializations
    @staticmethod
    def get_instance():
        if celery_shared_data.__instance is None:
            celery_shared_data()
        return celery_shared_data.__instance

    def __init__(self):
        if celery_shared_data.__instance is not None:
            raise Exception(MANAGE_CRAWLER_MESSAGES.S_SINGLETON_EXCEPTION)
        else:
            celery_shared_data.__instance = self

    def get_network_status(self):
        return redis_controller.get_instance().invoke_trigger(REDIS_COMMANDS.S_GET_BOOL, [REDIS_KEYS.S_NETWORK_MONITOR_STATUS, False, None])

    def set_network_status(self, p_status):
        redis_controller.get_instance().invoke_trigger(REDIS_COMMANDS.S_SET_BOOL, [REDIS_KEYS.S_NETWORK_MONITOR_STATUS, p_status, None])
