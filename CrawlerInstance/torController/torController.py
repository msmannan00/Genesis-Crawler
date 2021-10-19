# Local Imports
import os
import subprocess
import sys
import threading
import requests
import urllib3

from requests.adapters import HTTPAdapter
from stem import Signal
from urllib3 import Retry

from CrawlerInstance.sharedModel.requestHandler import requestHandler
from GenesisCrawlerServices.constants import strings
from GenesisCrawlerServices.constants.enums import TOR_COMMANDS, TOR_STATUS, TOR_CMD_COMMANDS
from stem.control import Controller
from CrawlerInstance.constants import application_status
# ./configure --with-openssl-dir=/usr/local/openssl --enable-static-openssl

# Tor Handler - Handle and manage tor request
class torController(requestHandler):

    __instance = None
    __m_tor_shell = None
    __m_tor_thread = None

    # Initializations
    @staticmethod
    def get_instance():
        if torController.__instance is None:
            torController()
        return torController.__instance

    def __init__(self):
        torController.__instance = self
        self.controller = None
        self.controller = None

    def on_create_session(self):
        m_request_handler = requests.Session()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        retries = Retry(total=1, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        m_request_handler.mount(strings.S_HTTP_PROTOCOL_SLASHED, HTTPAdapter(max_retries=retries))

        proxies = {
            # keys.k_http: strings.sock_http_proxy + str(application_status.S_TOR_CONNECTION_PORT), keys.k_https: strings.sock_https_proxy + str(application_status.S_TOR_CONTROL_PORT)
        }
        headers = {
            # keys.k_user_agent: constants.m_user_agent,
        }
        return m_request_handler, proxies, headers

    def __on_start_subprocess(self, p_command):
        application_status.S_TOR_STATUS = TOR_STATUS.S_START
        self.__m_tor_shell = subprocess.Popen(p_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd="/")
        self.__on_connect_tor()
        while True:
            nextline = self.__m_tor_shell.stdout.readline()
            m_log = nextline.decode("utf-8")

            if nextline == strings.S_EMPTY:
                break

            if application_status.S_TOR_STATUS == TOR_STATUS.S_START:
                sys.stdout.write(m_log)
                sys.stdout.flush()


    def __on_connect_tor(self):
        self.controller = Controller.from_port(port=int(application_status.S_TOR_CONTROL_PORT))
        self.controller.authenticate()

    def __on_new_circuit(self):
        try:
            self.controller.signal(Signal.NEWNYM)
        except Exception:
            pass


    def __on__release_ports(self):
        os.system('for /f "tokens=5" %a in (\'netstat -aon ^| find "' + str(application_status.S_TOR_CONNECTION_PORT) + '"\') do taskkill /f /pid %a')

    def __on_start_tor(self):
        self.__m_tor_thread = threading.Thread(target=self.__on_start_subprocess, args=[TOR_CMD_COMMANDS.S_START.value + " " + str(application_status.S_TOR_CONNECTION_PORT) + " " + str(application_status.S_TOR_CONTROL_PORT)])
        self.__m_tor_thread.start()

    def __on_stop_tor(self):
        self.controller.signal(Signal.SHUTDOWN)

    def __on_restart_tor(self):
        self.controller.signal(Signal.RELOAD)


    def invoke_trigger(self, p_command, p_data=None):
        if p_command == TOR_STATUS.S_STOP:
            self.__on_stop_tor()
        elif p_command is TOR_COMMANDS.S_START and application_status.S_TOR_STATUS == TOR_STATUS.S_READY:
            self.__on_start_tor()
        elif p_command is TOR_COMMANDS.S_GENERATED_CIRCUIT and application_status.S_TOR_STATUS == TOR_STATUS.S_RUNNING:
            self.__on_new_circuit()
        elif p_command is TOR_COMMANDS.S_RESTART and application_status.S_TOR_STATUS is TOR_STATUS.S_RUNNING:
            self.__on_restart_tor()
        elif p_command is TOR_COMMANDS.S_RELEASE_SESSION:
            self.__on__release_ports()
        elif p_command is TOR_COMMANDS.S_CREATE_SESSION:
            return self.on_create_session()
        else:
            pass



