# Local Imports
import os
import shutil
import subprocess
import threading
import requests
import stem
import socket

from time import sleep
from requests.adapters import HTTPAdapter
from stem import Signal
from stem.control import Controller
from urllib3 import Retry
from crawler.constants.app_status import APP_STATUS
from crawler.constants.constant import TOR_CONSTANTS, CRAWL_SETTINGS_CONSTANTS, TOR_CONNECTION_CONSTANTS
from crawler.constants.keys import TOR_KEYS
from crawler.constants.strings import TOR_STRINGS, STRINGS
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS, TOR_CMD_COMMANDS, TOR_STATUS
from crawler.crawler_services.helper_services.scheduler import RepeatedTimer
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler


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
    def __on_create_session(self, p_tor_based):
        m_request_handler = requests.Session()
        retries = Retry(total=1, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        m_request_handler.mount("http://", HTTPAdapter(max_retries=retries))

        if p_tor_based:
            proxies = {
                TOR_KEYS.S_HTTP: TOR_STRINGS.S_SOCKS_HTTPS_PROXY + str(TOR_CONNECTION_CONSTANTS.S_TOR_CONNECTION_PORT),
                TOR_KEYS.S_HTTPS: TOR_STRINGS.S_SOCKS_HTTPS_PROXY + str(TOR_CONNECTION_CONSTANTS.S_TOR_CONNECTION_PORT)
            }
            headers = {
                TOR_KEYS.S_USER_AGENT: CRAWL_SETTINGS_CONSTANTS.S_USER_AGENT,
            }
        else:
            proxies = {}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
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

    def tor_running(self, p_port):
        HOST = "10.0.0.106"

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((HOST, p_port))
        if result == 0:
            sock.close()
            return True
        else:
            sock.close()
            return False


    def __on_start_subprocess(self):
        APP_STATUS.S_TOR_STATUS = TOR_STATUS.S_START

        if not APP_STATUS.DOCKERIZED_RUN:
            self.__on_remove_carriage_return()
            p_command = TOR_CMD_COMMANDS.S_START_DIRECT + STRINGS.S_EMPTY_SPACE + str(TOR_CONNECTION_CONSTANTS.S_TOR_CONNECTION_PORT) + STRINGS.S_EMPTY_SPACE + str(TOR_CONNECTION_CONSTANTS.S_TOR_CONTROL_PORT)
            self.__m_tor_shell = subprocess.Popen(p_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd="/")

            while True:
                nextline = self.__m_tor_shell.stdout.readline()
                m_log = nextline.decode(STRINGS.S_UTF8_ENCODING)
                if len(m_log) > 5 and APP_STATUS.S_TOR_STATUS != TOR_STATUS.S_RUNNING:
                    log.g().i(m_log)

                if nextline == STRINGS.S_EMPTY:
                    break

                if m_log.__contains__("Bootstrapped 100% (done)"):
                    self.__m_controller = Controller(stem.socket.ControlPort("127.0.0.1", 9053))
                    self.__m_controller.authenticate()

                    APP_STATUS.S_TOR_STATUS = TOR_STATUS.S_RUNNING
                    RepeatedTimer(CRAWL_SETTINGS_CONSTANTS.S_TOR_NEW_CIRCUIT_INVOKE_DELAY, self.__on_new_circuit)

        else:
            while not self.tor_running(9052):
                log.g().i("waiting for tor...")
                sleep(1)
                continue

            self.__m_controller = Controller(stem.socket.ControlPort("10.0.0.106", 9053))
            self.__m_controller.authenticate("Imammehdi@00")

            APP_STATUS.S_TOR_STATUS = TOR_STATUS.S_RUNNING
            RepeatedTimer(CRAWL_SETTINGS_CONSTANTS.S_TOR_NEW_CIRCUIT_INVOKE_DELAY, self.__on_new_circuit)

    # Tor Commands
    def __on_new_circuit(self):
        self.__m_controller.signal(Signal.NEWNYM)

    def __on__release_ports(self):
        os.system(TOR_STRINGS.S_RELEASE_PORT)

    def __on_start_tor(self):
        self.__on_clear_cache()
        self.__m_tor_thread = threading.Thread(target=self.__on_start_subprocess)
        self.__m_tor_thread.start()

    def __on_stop_tor(self):
        self.__m_controller.signal(Signal.SHUTDOWN)

    def __on_restart_tor(self):
        self.__m_controller.signal(Signal.RELOAD)

    # Request Triggers
    def invoke_trigger(self, p_command, p_data=None):
        if p_command == TOR_STATUS.S_STOP:
            self.__on_stop_tor()
        elif p_command is TOR_COMMANDS.S_START and APP_STATUS.S_TOR_STATUS == TOR_STATUS.S_READY:
            self.__on__release_ports()
            self.__on_start_tor()
        elif p_command is TOR_COMMANDS.S_GENERATED_CIRCUIT and APP_STATUS.S_TOR_STATUS == TOR_STATUS.S_RUNNING:
            self.__on_new_circuit()
        elif p_command is TOR_COMMANDS.S_RESTART and APP_STATUS.S_TOR_STATUS is TOR_STATUS.S_RUNNING:
            self.__on_restart_tor()
        elif p_command is TOR_COMMANDS.S_RELEASE_SESSION:
            self.__on__release_ports()
        elif p_command is TOR_COMMANDS.S_CREATE_SESSION:
            return self.__on_create_session(p_data[0])
