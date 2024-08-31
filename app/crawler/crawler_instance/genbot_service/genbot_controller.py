# Local Imports
import copy
from asyncio import sleep
from crawler.crawler_instance.genbot_service.parse_controller import parse_controller
from crawler.crawler_instance.local_shared_model.url_model import url_model, url_model_init
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler
from crawler.crawler_instance.genbot_service.genbot_enums import ICRAWL_CONTROLLER_COMMANDS
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.crawler_services.crawler_services.mongo_manager.mongo_controller import mongo_controller
from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGO_CRUD
from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGODB_COMMANDS
from crawler.crawler_instance.tor_controller.tor_controller import tor_controller
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS
from crawler.crawler_instance.helper_services.web_request_handler import webRequestManager
from crawler.crawler_services.helper_services.duplication_handler import duplication_handler
from crawler.constants.strings import MANAGE_CRAWLER_MESSAGES
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_instance.helper_services.helper_method import helper_method


class genbot_controller(request_handler):
  import os
  import sys

  hashseed = os.getenv('PYTHONHASHSEED')
  if not hashseed:
    os.environ['PYTHONHASHSEED'] = '0'
    os.execv(sys.executable, [sys.executable] + sys.argv)

  def __init__(self):
    self.__task_id = None
    self.m_url_duplication_handler = duplication_handler()
    self.__m_web_request_handler = webRequestManager()
    self.__m_html_parser = parse_controller()

    self.__m_tor_id = - 1
    self.__m_depth = 0
    self.m_unparsed_url = []
    self.m_parsed_url = []
    self.__m_proxy = {}

  def init(self):
    self.__m_proxy, self.__m_tor_id = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_PROXY, [])

  def __trigger_url_request(self, p_request_model: url_model):
    try:
      log.g().i(str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " + MANAGE_CRAWLER_MESSAGES.S_PARSING_STARTING + " : " + p_request_model.m_url)
      m_redirected_url, m_response, m_raw_html = self.__m_web_request_handler.load_url(p_request_model.m_url, self.__m_proxy)

      if m_response is True:

        m_parsed_model = self.__m_html_parser.on_parse_html(m_raw_html, p_request_model)
        m_leak_data_model, m_sub_url = self.__m_html_parser.on_parse_leaks(m_raw_html, m_redirected_url)

        if m_leak_data_model is not None and helper_method.get_host_name(m_redirected_url).__eq__(helper_method.get_host_name(p_request_model.m_url)) and self.m_url_duplication_handler.validate_duplicate(m_redirected_url) is False:
          self.m_url_duplication_handler.insert(m_redirected_url)
          m_paresed_request_data = {"m_parsed_model":m_parsed_model.model_dump(),  "m_leak_data_model":m_leak_data_model.dict()}
          m_paresed_request_data = copy.deepcopy(m_paresed_request_data)
          # elastic_controller.get_instance().invoke_trigger(ELASTIC_CRUD_COMMANDS.S_INDEX, [ELASTIC_REQUEST_COMMANDS.S_INDEX, [json.dumps(m_paresed_request_data)], [True]])

          log.g().s(str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " + MANAGE_CRAWLER_MESSAGES.S_LOCAL_URL_PARSED + " : " + m_redirected_url)
          self.m_parsed_url.append(m_redirected_url)

          return m_parsed_model, m_sub_url
        else:
          return None, None
      else:
        log.g().e(str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " + MANAGE_CRAWLER_MESSAGES.S_LOCAL_URL_PARSED_FAILED + " : " + p_request_model.m_url + " : " + str(m_raw_html))
        return None, None
    except Exception as ex:
      print(ex, flush=True)
      return None, None

  def start_crawler_instance(self, p_request_url, p_task_id):
    p_request_url = helper_method.on_clean_url(p_request_url)
    self.__task_id = "dirlink_" + str(p_task_id)
    self.init()
    m_host_crawled = False
    m_failure_count = 0

    self.m_unparsed_url.append(url_model_init(p_request_url, CRAWL_SETTINGS_CONSTANTS.S_DEFAULT_DEPTH))
    while len(self.m_unparsed_url) > 0:
      item = self.m_unparsed_url.__getitem__(0)
      m_parsed_model, m_sub_url = self.__trigger_url_request(item)

      if m_parsed_model is None:
        if not m_host_crawled:
          if m_failure_count > 3:
            self.m_unparsed_url.pop(0)
          else:
            m_failure_count += 1
            sleep(5)
          continue

      for sub_url in m_sub_url:
        self.m_unparsed_url.append(url_model_init(sub_url, item.m_depth + 1))

      m_host_crawled = True
      self.m_unparsed_url.pop(0)

  def invoke_trigger(self, p_command, p_data=None):
    if p_command == ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE:
      self.start_crawler_instance(p_data[0], p_data[1])


def genbot_instance(p_url, p_vid):
  m_crawler = genbot_controller()
  try:
    m_crawler.invoke_trigger(ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE, [p_url, p_vid])
    p_request_url = helper_method.on_clean_url(p_url)
    mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_UPDATE, [MONGODB_COMMANDS.S_CLOSE_INDEX_ON_COMPLETE, [p_request_url], [True]])
  except Exception as ex:
    print("error : " + str(ex), flush=True)
  finally:
    del m_crawler
