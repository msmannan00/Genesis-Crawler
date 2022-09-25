import xxhash

from crawler.crawler_services.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS

redis_controller.get_instance().invoke_trigger(REDIS_COMMANDS.S_SET_STRING, ["assaxx", "dsaasd", 60 * 60 * 24 * 5])
xx = m_hashed_duplication_status = redis_controller.get_instance().invoke_trigger(REDIS_COMMANDS.S_GET_STRING, ["assaxxs", None, 60 * 60 * 24 * 5])
print(type(xx))
