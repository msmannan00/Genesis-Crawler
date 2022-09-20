from html_similarity import structural_similarity

from crawler.crawler_services.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, REDIS_KEYS

XX = redis_controller.get_instance().invoke_trigger(REDIS_COMMANDS.S_GET_LIST, ["pp1", "xxx", 60])
print(XX)