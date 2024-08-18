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
    __instance = None

    def __configure_logs(self):
        key = LOG_CONSTANTS.S_LOGS_KEY
        self.__server_instance = logging.getLogger('genesis_logs')
        self.__server_instance.setLevel(logging.INFO)  # Set the logging level to INFO
        options = {'hostname': 'genesis_logs', 'ip': '10.0.1.1', 'mac': 'C0:FF:EE:C0:FF:EE', 'index_meta': True}
        handler = LogDNAHandler(key, options)
        self.__server_instance.addHandler(handler)

        self.__server_instance.warning("Warning message", {'app': 'bloop'})
        self.__server_instance.info("Info message")

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

    # Info Logs
    def i(self, p_log):
        filter_log = str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " : " + self.get_caller_class() + " : " + str(p_log[0:120]))
        self.__server_instance.info(filter_log)
        print(colored(filter_log, 'cyan'))

    def s(self, p_log):
        filter_log = str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " : " + self.get_caller_class() + " : " + str(p_log[0:120]))
        self.__server_instance.info(filter_log)
        print(colored(filter_log, 'green'))

    # Warning Logs
    def w(self, p_log):
        filter_log = str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " : " + self.get_caller_class() + " : " + str(p_log[0:120]))
        self.__server_instance.warning(filter_log)
        print(colored(filter_log, 'yellow'))

    # Error Logs
    def e(self, p_log):
        filter_log = str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " : " + self.get_caller_class() + " : " + str(p_log[0:120]))
        self.__server_instance.error(filter_log)
        print(colored(filter_log, 'blue'))

    # Critical Logs
    def c(self, p_log):
        filter_log = str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " : " + self.get_caller_class() + " : " + str(p_log[0:120]))
        self.__server_instance.critical(filter_log)
        print(colored(filter_log, 'red'))
