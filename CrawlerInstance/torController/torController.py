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
from CrawlerInstance.constants import constants
from CrawlerInstance.constants.status import *
from CrawlerInstance.logManager.LogManager import log
from GenesisCrawlerServices.constants import strings, keys
from GenesisCrawlerServices.constants.enums import TorCommands, TorStatus, TorCommandsCMD
from stem.control import Controller
from CrawlerInstance.constants import status
# ./configure --with-openssl-dir=/usr/local/openssl --enable-static-openssl

# Tor Handler - Handle and manage tor request
class TorController(object):
    __instance = None
    m_tor_shell = None
    m_tor_thread = None

    # Initializations
    @staticmethod
    def getInstance():
        if TorController.__instance is None:
            TorController()
        return TorController.__instance

    def __init__(self):
        TorController.__instance = self
        self.controller = None
        self.controller = None

    def createSession(self):
        m_request_handler = requests.Session()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        retries = Retry(total=1, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        m_request_handler.mount(strings.http_protocol_slashed, HTTPAdapter(max_retries=retries))

        proxies = {
            keys.k_http: strings.sock_http_proxy + str(status.tor_connection_port), keys.k_https: strings.sock_https_proxy + str(status.tor_control_port)
        }
        headers = {
            keys.k_user_agent: constants.m_user_agent,
        }
        return m_request_handler, proxies, headers

    def start_tor_subprocess(self, p_command):
        status.tor_status = TorStatus.starting
        self.m_tor_shell = subprocess.Popen(p_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd="/")
        print(p_command)
        self.connectTor()
        while True:
            nextline = self.m_tor_shell.stdout.readline()
            m_log = nextline.decode("utf-8")

            if nextline == strings.empty:
                break

            if status.tor_status == TorStatus.starting:
                sys.stdout.write(m_log)
                sys.stdout.flush()
                self.invokeLogResponse(m_log)

            if strings.bootstrapped in m_log:
                self.invokeLogResponse(m_log)
                break

    def connectTor(self):
        self.controller = Controller.from_port(port=int(status.tor_control_port))
        self.controller.authenticate()

    def newCircuit(self):
        try:
            self.controller.signal(Signal.NEWNYM)
            log.g().i("[1] : " + strings.new_circuit_success)
        except Exception as err:
            log.g().i("[0] : " + strings.new_circuit_fail)


    def releasePorts(self):
        os.system('for /f "tokens=5" %a in (\'netstat -aon ^| find "' + str(status.tor_connection_port) + '"\') do taskkill /f /pid %a')

    def startTor(self):
        self.m_tor_thread = threading.Thread(target=self.start_tor_subprocess, args=[TorCommandsCMD.start_command.value + " " + str(status.tor_connection_port) + " " + str(status.tor_control_port)])
        self.m_tor_thread.start()

    def stopTor(self):
        self.controller.signal(Signal.SHUTDOWN)

    def restartTor(self):
        self.controller.signal(Signal.RELOAD)

    def invokeLogResponse(self, p_log):
        if strings.bootstrapped in p_log:
            status.tor_status = TorStatus.running
        if strings.interrupt in p_log:
            status.tor_status = TorStatus.ready

    def invokeTor(self, m_TorCommand):
        if m_TorCommand == TorStatus.stop:
            self.stopTor()
        elif m_TorCommand is TorCommands.start_command and status.tor_status == TorStatus.ready:
            self.startTor()
        elif m_TorCommand is TorCommands.generate_circuit_command and status.tor_status == TorStatus.running:
            self.newCircuit()
        elif m_TorCommand is TorCommands.restart_command and status.tor_status is TorStatus.running:
            self.restartTor()
        else:
            pass



