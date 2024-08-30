import inspect
import sys
import logging
import os
import datetime
from logdna import LogDNAHandler
from termcolor import colored

from crawler.constants.constant import LOG_CONSTANTS

if sys.platform == "win32":
  os.system('color')


class log:
  __server_instance = None

  def __configure_logs(self):
    key = LOG_CONSTANTS.S_LOGS_KEY
    self.__server_instance = logging.getLogger('genesis_logs')
    self.__server_instance.setLevel(logging.DEBUG)

    # Configure LogDNA handler
    options = {
      'hostname': 'genesis_logs',
      'ip': '10.0.1.1',
      'mac': 'C0:FF:EE:C0:FF:EE',
      'index_meta': True
    }
    handler = LogDNAHandler(key, options)
    self.__server_instance.addHandler(handler)

    self.log_directory = os.path.join(os.getcwd(), 'logs')
    os.makedirs(self.log_directory, exist_ok=True)

  @staticmethod
  def g():
    if log.__server_instance is None:
      log()
    return log.__server_instance

  def __init__(self):
    log.__server_instance = self
    self.__configure_logs()

  def get_caller_class(self):
    m_prev_frame = inspect.currentframe().f_back.f_back
    return str(m_prev_frame.f_locals["self"].__class__.__name__)

  def __write_to_file(self, log_message):
    log_filename = datetime.datetime.now().strftime("%Y-%m-%d") + ".log"
    log_filepath = os.path.join(self.log_directory, log_filename)
    with open(log_filepath, 'a') as log_file:
      log_file.write(log_message + "\n")

  def __format_log_message(self, log_type, p_log):
    current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    caller_class = self.get_caller_class()
    formatted_log = f"{log_type} - {current_time} : {caller_class} : {p_log[:120]}"
    return formatted_log

  # Info Logs
  def i(self, p_log):
    filter_log = self.__format_log_message("INFO", p_log)
    self.__server_instance.info(filter_log)
    self.__write_to_file(filter_log)
    print(colored(filter_log, 'cyan'))

  # Success Logs
  def s(self, p_log):
    try:
      filter_log = self.__format_log_message("SUCCESS", p_log)
      self.__server_instance.info(filter_log)
      self.__write_to_file(filter_log)
      print(colored(filter_log, 'green'))
    except Exception:
      pass

  # Warning Logs
  def w(self, p_log):
    try:
      filter_log = self.__format_log_message("WARNING", p_log)
      self.__server_instance.warning(filter_log)
      self.__write_to_file(filter_log)
      print(colored(filter_log, 'yellow'))
    except Exception:
      pass

  # Error Logs
  def e(self, p_log):
    try:
      filter_log = self.__format_log_message("ERROR", p_log)
      self.__server_instance.error(filter_log)
      self.__write_to_file(filter_log)
      print(colored(filter_log, 'blue'))
    except Exception:
      pass

  # Critical Logs
  def c(self, p_log):
    try:
      filter_log = self.__format_log_message("CRITICAL", p_log)
      self.__server_instance.critical(filter_log)
      self.__write_to_file(filter_log)
      print(colored(filter_log, 'red'))
    except Exception:
      pass
