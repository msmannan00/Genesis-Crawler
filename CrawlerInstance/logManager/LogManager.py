import sys

from CrawlerInstance.constants import constants, status
from GenesisCrawlerServices.constants.enums import ErrorMessages, CrawlerStatus


class log:

    __instance = None
    info_logs = []
    error_logs = []

    # Initializations
    @staticmethod
    def g():
        if log.__instance is None:
            log()
        return log.__instance

    def __init__(self):
        log.__instance = self

    # Info Logs
    def i(self, p_log):
        print(p_log)

        self.info_logs.insert(0, p_log)
        if len(self.info_logs) > constants.m_max_log_queue_size:
            self.info_logs = self.info_logs[:-1]

    # Error Logs
    def e(self, p_log):
        print(p_log)
        self.error_logs.insert(0, p_log)
        if len(self.info_logs) > constants.m_max_log_queue_size:
            self.info_logs = self.info_logs[:-1]

    def getErrorLogs(self):
        return self.error_logs

    def getInfoLogs(self):
        return self.info_logs
