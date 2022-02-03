import inspect
import sys
import threading
import logging
import os
import datetime
import arrow

from pathlib import Path
from pathlib import Path
from termcolor import colored

from crawler.crawler_instance.constants.constant import RAW_PATH_CONSTANTS

if sys.platform == "win32":
    os.system('color')
else:
    pass

class log:
    __instance = None

    def __clear_old_logs(self):
        filesPath = r""+RAW_PATH_CONSTANTS.S_LOGS_DIRECTORY
        criticalTime = arrow.now().shift(days=-7)
        for item in Path(filesPath).glob('*'):
            if item.is_file():
                itemTime = arrow.get(item.stat().st_mtime)
                if itemTime < criticalTime:
                    os.remove(item.__fspath__())
                    pass

    def __configure_logs(self):
        if os.path.exists(RAW_PATH_CONSTANTS.S_LOGS_DIRECTORY) is False:
            os.mkdir(RAW_PATH_CONSTANTS.S_LOGS_DIRECTORY)

        logging.basicConfig(filename=RAW_PATH_CONSTANTS.S_LOGS_DIRECTORY + str(datetime.date.today()), filemode='a', format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.WARNING)

    # Initializations
    @staticmethod
    def g():
        if log.__instance is None:
            log()
        return log.__instance

    def __init__(self):
        log.__instance = self
        self.__clear_old_logs()
        self.__configure_logs()

    def get_caller_class(self):
        m_prev_frame = inspect.currentframe().f_back.f_back
        return str(m_prev_frame.f_locals["self"].__class__.__name__)

    # Info Logs
    def i(self, p_log):
        logging.info("INFO:" + p_log)
        print(colored(str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " : " + self.get_caller_class() + " : " + str(threading.get_native_id())) + " : " + p_log, 'cyan'))

    # Success Logs
    def s(self, p_log):
        logging.info(p_log)
        print(colored(str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " : " + self.get_caller_class() + " : " + str(threading.get_native_id())) + " : " + p_log, 'green'))

    # Warning Logs
    def w(self, p_log):
        logging.info("WARNING:" + p_log)
        logging.info(p_log)
        print(colored(str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " : " + self.get_caller_class() + " : " + str(threading.get_native_id())) + " : " + p_log, 'yellow'))

    # Error Logs
    def e(self, p_log):
        logging.info("ERROR:" + p_log)
        logging.info(p_log)
        print(colored(str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " : " + self.get_caller_class() + " : " + str(threading.get_native_id())) + " : " + p_log, 'blue'))

    # Error Logs
    def c(self, p_log):
        logging.info("CRITICAL:" + p_log)
        logging.info(p_log)
        print(colored(str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " : " + self.get_caller_class() + " : " + str(threading.get_native_id())) + " : " + p_log, 'red'))
