from crawler.crawler_services.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, REDIS_CONNECTIONS

REDIS_CONNECTIONS.S_DATABASE_IP = "localhost"
ss = redis_controller.get_instance().invoke_trigger(REDIS_COMMANDS.S_GET_BOOL, ["VDests", False])
print(ss)
