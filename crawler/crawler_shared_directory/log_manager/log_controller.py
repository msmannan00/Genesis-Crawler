import inspect
import sys
import threading

from termcolor import colored

import os
import datetime

if sys.platform == "win32":
    os.system('color')
else:
    pass

class log:

    __instance = None

    # Initializations
    @staticmethod
    def g():
        if log.__instance is None:
            log()
        return log.__instance

    def __init__(self):
        log.__instance = self

    def get_caller_class(self):
        m_prev_frame = inspect.currentframe().f_back.f_back
        return str(m_prev_frame.f_locals["self"].__class__.__name__)

    # Info Logs
    def i(self, p_log):
        print(colored(str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " : " + self.get_caller_class() + " : " + str(threading.get_native_id())) + " : " + p_log, 'cyan'))

    # Success Logs
    def s(self, p_log):
        print(colored(str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " : " + self.get_caller_class() + " : " + str(threading.get_native_id())) + " : " + p_log, 'green'))

    # Warning Logs
    def w(self, p_log):
        print(colored(str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " : " + self.get_caller_class() + " : " + str(threading.get_native_id())) + " : " + p_log, 'yellow'))

    # Error Logs
    def e(self, p_log):
        print(colored(str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " : " + self.get_caller_class() + " : " + str(threading.get_native_id())) + " : " + p_log, 'blue'))

    # Error Logs
    def c(self, p_log):
        print(colored(str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " : " + self.get_caller_class() + " : " + str(threading.get_native_id())) + " : " + p_log, 'red'))
