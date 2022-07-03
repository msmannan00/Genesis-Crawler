import redis
from crawler.constants.strings import MANAGE_CRAWLER_MESSAGES
from crawler.crawler_services.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, REDIS_CONNECTIONS


class redis_controller:
    __instance = None
    __redis = None

    # Initializations
    @staticmethod
    def get_instance():
        if redis_controller.__instance is None:
            redis_controller()
        return redis_controller.__instance

    def __init__(self):
        if redis_controller.__instance is not None:
            raise Exception(MANAGE_CRAWLER_MESSAGES.S_SINGLETON_EXCEPTION)
        else:
            redis_controller.__instance = self
        self.__redis = redis.StrictRedis(REDIS_CONNECTIONS.S_DATABASE_IP, decode_responses=True, password=REDIS_CONNECTIONS.S_DATABASE_PASSWORD)

    def __set_bool(self, p_key, p_val):
        self.__redis.set(p_key, int(p_val))

    def __get_bool(self, p_key, p_val):
        if not self.__redis.exists(p_key):
            self.__set_bool(p_key, p_val)
        return bool(int(self.__redis.get(p_key)))

    def __set_int(self, p_key, p_val):
        self.__redis.set(p_key, p_val)

    def __get_int(self, p_key, p_val):
        if not self.__redis.exists(p_key):
            self.__set_int(p_key, p_val)
        return self.__redis.get(p_key)

    def __set_string(self, p_key, p_val):
        self.__redis.set(p_key, p_val)

    def __get_string(self, p_key, p_val):
        if not self.__redis.exists(p_key):
            self.__set_string(p_key, p_val)
        return self.__redis.get(p_key)

    def invoke_trigger(self, p_commands, p_data=None):

        if p_commands == REDIS_COMMANDS.S_GET_INT:
            return self.__get_int(p_data[0], p_data[1])
        if p_commands == REDIS_COMMANDS.S_SET_INT:
            return self.__set_int(p_data[0], p_data[1])


        elif p_commands == REDIS_COMMANDS.S_GET_BOOL:
            return self.__get_bool(p_data[0], p_data[1])
        elif p_commands == REDIS_COMMANDS.S_SET_BOOL:
            return self.__set_bool(p_data[0], p_data[1])

        elif p_commands == REDIS_COMMANDS.S_GET_STRING:
            return self.__get_string(p_data[0], p_data[1])
        elif p_commands == REDIS_COMMANDS.S_SET_STRING:
            return self.__set_string(p_data[0], p_data[1])
