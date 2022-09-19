# Local Imports
from crawler.celery_manager import celery_genbot
from crawler.crawler_instance.genbot_service.genbot_enums import ICRAWL_CONTROLLER_COMMANDS
from crawler.crawler_instance.genbot_service.web_request_handler import webRequestManager
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler


class web_controller(request_handler):

    def __init__(self):
        self.__m_web_request_handler = webRequestManager()

    # Wait For Crawl Manager To Provide URL From Queue
    def start_crawler_instance(self, p_request_url, p_proxy):
        return self.__m_web_request_handler.load_url(p_request_url, p_proxy)

    def invoke_trigger(self, p_command, p_data=None):
        if p_command == ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE:
            return self.start_crawler_instance(p_data[0], p_data[1])


@celery_genbot.task(name='celery_web_instance.task', bind=False, queue='web_queue')
def celery_web_instance(p_url, p_proxy):
    m_crawler = web_controller()
    return m_crawler.invoke_trigger(ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE, [p_url, p_proxy])
