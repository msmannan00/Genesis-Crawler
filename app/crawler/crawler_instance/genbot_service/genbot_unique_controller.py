# Local Imports
from asyncio import sleep
from crawler.crawler_instance.local_shared_model.url_model import url_model
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler
from crawler.crawler_instance.genbot_service.genbot_enums import ICRAWL_CONTROLLER_COMMANDS
from crawler.crawler_instance.tor_controller.tor_controller import tor_controller
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS
from crawler.crawler_instance.helper_services.web_request_handler import webRequestManager
from crawler.crawler_services.helper_services.duplication_handler import duplication_handler
from crawler.constants.strings import MANAGE_CRAWLER_MESSAGES
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_instance.helper_services.helper_method import helper_method
import hashlib
from bs4 import BeautifulSoup
import os
import sys


class genbot_unique_controller(request_handler):

  hashseed = os.getenv('PYTHONHASHSEED')
  if not hashseed:
    os.environ['PYTHONHASHSEED'] = '0'
    os.execv(sys.executable, [sys.executable] + sys.argv)

  def __init__(self):
    self.__task_id = None
    self.m_url_duplication_handler = duplication_handler()
    self.__m_web_request_handler = webRequestManager()

    self.__m_tor_id = - 1
    self.__m_proxy = {}

  def init(self):
    self.__m_proxy, self.__m_tor_id = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_PROXY, [])

  def __trigger_url_request(self, p_request_model: url_model):
    try:
      log.g().i(str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " + MANAGE_CRAWLER_MESSAGES.S_PARSING_STARTING + " : " + p_request_model.m_url)

      m_redirected_url, m_response, m_raw_html = self.__m_web_request_handler.load_url(p_request_model.m_url, self.__m_proxy)

      if m_response is True:
        soup = BeautifulSoup(m_raw_html, 'html.parser')
        extracted_text = soup.get_text()
        substring_text = extracted_text[0:500]
        unique_hash = hashlib.sha256(substring_text.encode('utf-8')).hexdigest()
        if self.m_url_duplication_handler.validate_duplicate(unique_hash):
          return False
        else:
          self.m_url_duplication_handler.insert(url_model.m_url)
          return True
      else:
        return False

    except Exception as ex:
      log.g().e(str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " + str(ex))
      return False

  def __index_url(self, m_url):
    pass

  def start_crawler_instance(self, p_request_url_list):
    self.init()
    m_failure_count = 0

    for m_url in p_request_url_list:
      m_url = helper_method.on_clean_url(m_url)
      while True:
        m_status = self.__trigger_url_request(m_url)
        if m_status is False:
          if m_failure_count > 3:
            break
          else:
            m_failure_count += 1
            sleep(5)
          continue
        else:
          self.__index_url(m_url)

  def invoke_trigger(self, p_command, p_data=None):
    if p_command == ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE:
      self.start_crawler_instance(p_data[0])


def genbot_unique_instance(p_url_list):
  m_crawler = genbot_unique_controller()
  try:
    m_crawler.invoke_trigger(ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE, [p_url_list])
  except Exception as ex:
    print("error : " + str(ex.with_traceback(ex.__traceback__)), flush=True)
  finally:
    del m_crawler

