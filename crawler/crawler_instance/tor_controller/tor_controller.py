# Local Imports
import os
import shutil
import subprocess
import threading
import time
import requests
import urllib3

from requests.adapters import HTTPAdapter
from stem import Signal
from urllib3 import Retry
from crawler.crawler_instance.constants import app_status
from crawler.crawler_instance.constants.constant import CRAWL_SETTINGS_CONSTANTS, TOR_CONSTANTS
from crawler.crawler_instance.constants.strings import STRINGS, TOR_STRINGS
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS, TOR_CMD_COMMANDS, TOR_STATUS
from stem.control import Controller
from crawler.crawler_services.constants.keys import tor_keys

# Tor Handler - Handle and manage tor request

class tor_controller(request_handler):

    __instance = None
    __m_tor_shell = None
    __m_tor_thread = None
    __m_new_circuit_thread = None
    __m_controller = None

    # Initializations
    @staticmethod
    def get_instance():
        if tor_controller.__instance is None:
            tor_controller()
        return tor_controller.__instance

    def __init__(self):
        tor_controller.__instance = self

    # Tor Helper Methods
    def __on_create_session(self):
        m_request_handler = requests.Session()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        retries = Retry(total=1, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        m_request_handler.mount("http://", HTTPAdapter(max_retries=retries))

        proxies = {
            tor_keys.S_HTTP: TOR_STRINGS.S_SOCKS_HTTPS_PROXY + str(app_status.TOR_STATUS.S_TOR_CONNECTION_PORT),
            tor_keys.S_HTTPS: TOR_STRINGS.S_SOCKS_HTTPS_PROXY + str(app_status.TOR_STATUS.S_TOR_CONNECTION_PORT)
        }
        headers = {
            tor_keys.S_USER_AGENT: CRAWL_SETTINGS_CONSTANTS.S_USER_AGENT,
        }
        return m_request_handler, proxies, headers

    def __on_remove_carriage_return(self):
        with open(TOR_CONSTANTS.S_SHELL_CONFIG_PATH, 'r') as file:
            content = file.read()

        with open(TOR_CONSTANTS.S_SHELL_CONFIG_PATH, 'w', newline='\n') as file:
            file.write(content)

    def __on_clear_cache(self):
        if os.path.exists(TOR_CONSTANTS.S_TOR_PROXY_PATH):
            shutil.rmtree(TOR_CONSTANTS.S_TOR_PROXY_PATH)

    def __on_start_subprocess(self, p_command):
        self.__on_remove_carriage_return()

        app_status.S_TOR_STATUS = TOR_STATUS.S_START
        self.__m_tor_shell = subprocess.Popen(p_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd="/")
        self.__m_controller = Controller.from_port(port=int(app_status.TOR_STATUS.S_TOR_CONTROL_PORT))
        self.__m_controller.authenticate()
        self.__m_new_circuit_threadS = threading.Thread(target=self.__on_new_circuit_repeat)
        self.__m_new_circuit_threadS.start()

        while True:
            nextline = self.__m_tor_shell.stdout.readline()
            m_log = nextline.decode(STRINGS.S_UTF8_ENCODING)
            if len(m_log)>5 and app_status.TOR_STATUS.S_TOR_STATUS != TOR_STATUS.S_RUNNING:
                print(m_log, flush=True)

            if nextline == STRINGS.S_EMPTY:
                break

            if m_log.__contains__("Bootstrapped 100% (done)"):
                app_status.TOR_STATUS.S_TOR_STATUS = TOR_STATUS.S_RUNNING

    def __on_new_circuit_repeat(self):
        while True:
            time.sleep(CRAWL_SETTINGS_CONSTANTS.S_TOR_NEW_CIRCUIT_INVOKE_DELAY)
            self.__on_new_circuit()

    # Tor Commands
    def __on_new_circuit(self):
        self.__m_controller.signal(Signal.NEWNYM)

    def __on__release_ports(self):
        os.system(TOR_STRINGS.S_RELEASE_PORT)

    def __on_start_tor(self):
        self.__on_clear_cache()
        self.__m_tor_thread = threading.Thread(target=self.__on_start_subprocess, args=[TOR_CMD_COMMANDS.S_START.value + STRINGS.S_EMPTY_SPACE + str(
            app_status.TOR_STATUS.S_TOR_CONNECTION_PORT) + STRINGS.S_EMPTY_SPACE + str(
            app_status.TOR_STATUS.S_TOR_CONTROL_PORT)])
        self.__m_tor_thread.start()

    def __on_stop_tor(self):
        self.__m_controller.signal(Signal.SHUTDOWN)

    def __on_restart_tor(self):
        self.__m_controller.signal(Signal.RELOAD)

    # Request Triggers
    def invoke_trigger(self, p_command, p_data=None):
        if p_command == TOR_STATUS.S_STOP:
            self.__on_stop_tor()
        elif p_command is TOR_COMMANDS.S_START and app_status.TOR_STATUS.S_TOR_STATUS == TOR_STATUS.S_READY:
            self.__on__release_ports()
            self.__on_start_tor()
        elif p_command is TOR_COMMANDS.S_GENERATED_CIRCUIT and app_status.TOR_STATUS.S_TOR_STATUS == TOR_STATUS.S_RUNNING:
            self.__on_new_circuit()
        elif p_command is TOR_COMMANDS.S_RESTART and app_status.TOR_STATUS.S_TOR_STATUS is TOR_STATUS.S_RUNNING:
            self.__on_restart_tor()
        elif p_command is TOR_COMMANDS.S_RELEASE_SESSION:
            self.__on__release_ports()
        elif p_command is TOR_COMMANDS.S_CREATE_SESSION:
            return self.__on_create_session()



