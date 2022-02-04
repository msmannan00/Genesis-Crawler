from crawler.crawler_instance.application_controller.application_controller import application_controller
from crawler.crawler_instance.application_controller.application_enums import APPICATION_COMMANDS
from crawler.crawler_services.crawler_services.mongo_manager.mongo_controller import mongo_controller
from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGO_CRUD, MONGODB_COMMANDS

# mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_DELETE,[MONGODB_COMMANDS.S_CLEAR_BACKUP,[None],[None]])
# mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_DELETE,[MONGODB_COMMANDS.S_CLEAR_CRAWLED_URL,[None],[None]])

application_controller.get_instance().invoke_triggers(APPICATION_COMMANDS.S_START_APPLICATION)
