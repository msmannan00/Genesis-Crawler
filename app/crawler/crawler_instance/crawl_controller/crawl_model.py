# Local Imports
import os
import shutil
import zipfile
from time import sleep

from crawler.constants.app_status import APP_STATUS
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.constants.strings import MANAGE_CRAWLER_MESSAGES
from crawler.crawler_instance.crawl_controller.crawl_enums import CRAWL_MODEL_COMMANDS
from crawler.crawler_instance.genbot_service.genbot_controller import genbot_instance
from crawler.crawler_instance.helper_services.helper_method import helper_method
from crawler.crawler_instance.tor_controller.tor_controller import tor_controller
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS
from crawler.crawler_services.crawler_services.celery_manager.celery_enums import CELERY_COMMANDS
from crawler.crawler_services.crawler_services.mongo_manager.mongo_controller import mongo_controller
from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGODB_COMMANDS, MONGO_CRUD
from crawler.crawler_services.helper_services.scheduler import RepeatedTimer
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler
from crawler.crawler_services.crawler_services.celery_manager.celery_controller import celery_controller
from crawler.shared_data import celery_shared_data


class crawl_model(request_handler):

  def __init__(self):
    self.__celery_vid = 100000

  def init_parsers(self):
    zip_url = CRAWL_SETTINGS_CONSTANTS.S_PARSERS_URL
    zip_path = "downloaded_file.zip"
    extract_dir = os.path.join(os.getcwd(), 'raw')

    try:
      m_request_handler, headers = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_CREATE_SESSION, [False])
      m_response = m_request_handler.get(zip_url, headers=headers, timeout=CRAWL_SETTINGS_CONSTANTS.S_URL_TIMEOUT, proxies={}, allow_redirects=True)

      if m_response.status_code == 200:
        with open(zip_path, "wb") as file:
          for chunk in m_response.iter_content(chunk_size=1024):
            if chunk:
              file.write(chunk)

        if os.path.exists(extract_dir):
          shutil.rmtree(extract_dir)
        os.makedirs(extract_dir)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
          zip_ref.extractall(extract_dir)

    except Exception as e:
      log.g().e(e)

    finally:
      if os.path.exists(zip_path):
        os.remove(zip_path)

  def __init_docker_request(self):
    m_live_url_list, m_updated_url_list = self.__install_live_url()
    m_list = list(m_live_url_list)
    m_list.extend(m_updated_url_list)
    self.__start_docker_request(m_list)

  def __init_direct_request(self):
    log.g().i(MANAGE_CRAWLER_MESSAGES.S_REINITIALIZING_CRAWLABLE_URL)

    while True:
      m_live_url_list, p_fetched_url_list = self.__install_live_url()
      m_request_list = list(m_live_url_list) + p_fetched_url_list
      for m_url_node in m_request_list:
        genbot_instance(m_url_node, -1)

  def __reinit_docker_request(self):
    m_live_url_list, m_updated_url_list = self.__install_live_url()
    return m_updated_url_list

  # Start Crawler Manager
  def __install_live_url(self):
    mongo_response = mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_READ, [MONGODB_COMMANDS.S_GET_CRAWLABLE_URL_DATA, [None], [None]])
    m_live_url_list = list([x['m_url'] for x in mongo_response])
    m_request_handler, headers = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_CREATE_SESSION, [False])
    while True:
      try:
        m_response = m_request_handler.get(CRAWL_SETTINGS_CONSTANTS.S_START_URL, headers=headers, timeout=CRAWL_SETTINGS_CONSTANTS.S_URL_TIMEOUT, proxies={}, allow_redirects=True)
        break
      except Exception as ex:
        sleep(1000)
        log.g().e(ex)
    m_response_text = m_response.text

    m_updated_url_list = []
    for m_server_url in m_response_text.splitlines():
      m_url = helper_method.on_clean_url(m_server_url)
      if helper_method.is_uri_validator(m_server_url) and m_url not in m_live_url_list:
        log.g().s(MANAGE_CRAWLER_MESSAGES.S_INSTALLED_URL + " : " + m_url)
        mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_UPDATE, [MONGODB_COMMANDS.S_INSTALL_CRAWLABLE_URL, [m_url], [True]])
        m_updated_url_list.append(m_url)

    mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_DELETE, [MONGODB_COMMANDS.S_REMOVE_DEAD_CRAWLABLE_URL, [list(m_live_url_list)], [None]])
    return m_live_url_list, m_updated_url_list

  def __start_docker_request(self, p_fetched_url_list):
    RepeatedTimer(CRAWL_SETTINGS_CONSTANTS.S_UPDATE_STATUS_TIMEOUT, self.reinit_list_periodically, True, p_fetched_url_list)

  def reinit_list_periodically(self, p_fetched_url_list):
    if celery_shared_data.get_instance().get_network_status:
      if not p_fetched_url_list:
        p_fetched_url_list.extend(self.__reinit_docker_request())
      while len(p_fetched_url_list) > 0:
        self.__celery_vid += 1
        celery_controller.get_instance().invoke_trigger(CELERY_COMMANDS.S_START_TASK, [p_fetched_url_list.pop(0), self.__celery_vid])

  def __init_crawler(self):
    self.__celery_vid = 100000
    # self.init_parsers()
    # RepeatedTimer(CRAWL_SETTINGS_CONSTANTS.S_UPDATE_PARSERS_TIMEOUT, self.reinit_list_periodically, False, self.init_parsers)

    if APP_STATUS.DOCKERIZED_RUN:
      self.__init_docker_request()
    else:
      self.__init_direct_request()

  def invoke_trigger(self, p_command, p_data=None):
    if p_command == CRAWL_MODEL_COMMANDS.S_INIT:
      self.__init_crawler()
