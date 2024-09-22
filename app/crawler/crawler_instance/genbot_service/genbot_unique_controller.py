# Local Imports
import filecmp
import json

from crawler.constants.constant import RAW_PATH_CONSTANTS
from crawler.crawler_services.crawler_services.elastic_manager.elastic_controller import elastic_controller
from crawler.crawler_services.crawler_services.elastic_manager.elastic_enums import ELASTIC_CRUD_COMMANDS, ELASTIC_REQUEST_COMMANDS, ELASTIC_CONNECTIONS
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler
from crawler.crawler_instance.genbot_service.genbot_enums import ICRAWL_CONTROLLER_COMMANDS
from crawler.crawler_instance.tor_controller.tor_controller import tor_controller
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS
from crawler.crawler_services.web_request_handler import webRequestManager
from crawler.crawler_services.helper_services.duplication_handler import duplication_handler
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_services.helper_services.helper_method import helper_method
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
    self.__m_parsed_list = []

    self.__m_tor_id = - 1
    self.__m_proxy = {}

  def init(self):
    self.__m_proxy, self.__m_tor_id = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_PROXY, [])

  def __trigger_url_request(self, p_url):
    try:
      m_redirected_url, m_response, m_raw_html = self.__m_web_request_handler.load_url(p_url, self.__m_proxy)

      if m_response is True:
        soup = BeautifulSoup(m_raw_html, 'html.parser')
        extracted_text = soup.get_text()
        substring_text = extracted_text[0:500]
        unique_hash = hashlib.sha256(substring_text.encode('utf-8')).hexdigest()
        if self.m_url_duplication_handler.validate_duplicate(unique_hash):
          return False, True
        else:
          self.m_url_duplication_handler.insert(p_url)
          return True, True
      else:
        return False, False

    except Exception as ex:
      log.g().e(str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " + str(ex))
      return False, True

  def __index_url(self, m_url):
    file_path = os.path.join(RAW_PATH_CONSTANTS.UNIQUE_CRAWL_DIRECTORY, 'hosts_new.txt')
    try:
      with open(file_path, 'a') as file:
        file.write(m_url + '\n')
      log.g().i(f"Written to file: {m_url}")
    except Exception as e:
      log.g().e(f"Failed to write to file: {e}")

  def __update_global_index(self):
    file_path_new = os.path.join(RAW_PATH_CONSTANTS.UNIQUE_CRAWL_DIRECTORY, 'hosts_new.txt')
    file_path_old = os.path.join(RAW_PATH_CONSTANTS.UNIQUE_CRAWL_DIRECTORY, 'hosts.txt')

    try:
      if os.path.exists(file_path_old) and filecmp.cmp(file_path_new, file_path_old, shallow=False):
        with open(file_path_new, 'w'):
          pass
      else:
        os.replace(file_path_new, file_path_old)
        elastic_controller.get_instance().invoke_trigger(ELASTIC_CRUD_COMMANDS.S_INDEX, [ELASTIC_REQUEST_COMMANDS.S_UNIQUE_INDEX, json.dumps(self.__m_parsed_list), ELASTIC_CONNECTIONS.S_CRAWL_UNIQUE_INDEX])
        with open(file_path_new, 'w'):
          pass

    except Exception:
      pass

  def start_crawler_instance(self, p_request_url_list):
      self.init()
      for m_url in p_request_url_list:
        try:
          m_url = helper_method.on_clean_url(m_url)
          m_status = False
          m_failure_count = 0
          while m_failure_count<3:
            m_status, m_web_status = self.__trigger_url_request(m_url)
            if m_web_status is False:
              m_failure_count += 1
              continue
            else:
              break
          if m_status:
            self.__m_parsed_list.append(m_url)
            self.__index_url(m_url)
        except Exception as ex:
          log.g().e(str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " + str(ex))
      self.__update_global_index()

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

def prepare_and_fetch_data(url):
  os.makedirs(RAW_PATH_CONSTANTS.UNIQUE_CRAWL_DIRECTORY, exist_ok=True)
  helper_method.clear_hosts_file(os.path.join(RAW_PATH_CONSTANTS.UNIQUE_CRAWL_DIRECTORY, 'hosts.txt'))
  helper_method.clear_hosts_file(os.path.join(RAW_PATH_CONSTANTS.UNIQUE_CRAWL_DIRECTORY, 'hosts_new.txt'))

  web_request_manager = webRequestManager()
  file_content, status_or_error = web_request_manager.request_server_get(url)

  if status_or_error == 200:
    return file_content.decode('utf-8').splitlines()
  else:
    log.g().e(f"Failed to fetch data from {url}, status: {status_or_error}")
    return None
