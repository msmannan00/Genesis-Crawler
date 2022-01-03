from crawler_instance.application_controller.application_controller import application_controller
from crawler_instance.application_controller.application_enums import APPICATION_COMMANDS
from crawler_services.crawler_services.mongo_manager.mongo_controller import mongo_controller
from crawler_services.crawler_services.mongo_manager.mongo_enums import MONGO_CRUD, MONGODB_COMMANDS

# mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_DELETE,[MONGODB_COMMANDS.S_CLEAR_INDEX,[None],[None]])
# mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_DELETE,[MONGODB_COMMANDS.S_CLEAR_TFIDF,[None],[None]])
# mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_DELETE,[MONGODB_COMMANDS.S_CLEAR_BACKUP,[None],[None]])
mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_DELETE,[MONGODB_COMMANDS.S_CLEAR_UNIQUE_HOST,[None],[None]])

application_controller.get_instance().invoke_trigger(APPICATION_COMMANDS.S_START_APPLICATION)
