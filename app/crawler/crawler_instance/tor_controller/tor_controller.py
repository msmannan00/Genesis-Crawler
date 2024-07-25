# Local Imports
import requests
import stem as stem
from requests.adapters import HTTPAdapter
from stem.control import Controller
from urllib3 import Retry
from crawler.constants.app_status import APP_STATUS
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.constants.status import S_TOR_INSTANCE_COUNT
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler
from crawler.crawler_services.helper_services.scheduler import RepeatedTimer
from stem import Signal


class tor_controller(request_handler):
    __instance = None
    __m_controller = []
    __m_session = None
    __proxy_index = 0
    __control_proxy_index = 0
    __tor_instances_count = S_TOR_INSTANCE_COUNT

    # Dynamically generate proxies
    @staticmethod
    def generate_proxies(start_ip, start_port, count, port_step=2, control_port_offset=1):
        base_ip = [int(x) for x in start_ip.split('.')]
        proxies = []
        control_proxies = []

        for i in range(count):
            ip = f"172.0.0.{base_ip[3] + i}"
            http_port = start_port + (i * port_step)
            https_port = http_port  # Assuming HTTP and HTTPS ports are the same
            control_port = http_port + control_port_offset

            proxies.append({
                "http": f"socks5h://{ip}:{http_port}",
                "https": f"socks5h://{ip}:{https_port}"
            })

            control_proxies.append({
                "proxy": ip,
                "port": control_port
            })

        return proxies, control_proxies

    TOR_PROXIES, TOR_CONTROL_PROXIES = generate_proxies('172.0.0.10', 9152, __tor_instances_count)

    @staticmethod
    def get_instance():
        if tor_controller.__instance is None:
            tor_controller.__instance = tor_controller()
        return tor_controller.__instance

    def __init__(self):
        self.__on_init()

    def __on_init(self):
        self.__session = requests.Session()
        retries = Retry(total=1, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(pool_connections=1000, pool_maxsize=1000, max_retries=retries)
        self.__session.mount('http://', adapter)
        self.__session.mount('https://', adapter)

        if APP_STATUS.DOCKERIZED_RUN:
            for controller_info in self.TOR_CONTROL_PROXIES:
                try:
                    m_temp_controller = Controller(stem.socket.ControlPort(controller_info["proxy"], controller_info["port"]))
                    m_temp_controller.authenticate("Imammehdi@00")
                    self.__m_controller.append(m_temp_controller)
                    RepeatedTimer(CRAWL_SETTINGS_CONSTANTS.S_TOR_NEW_CIRCUIT_INVOKE_DELAY, self.__invoke_new_circuit, False, m_temp_controller)
                    self.__invoke_new_circuit(m_temp_controller)
                except Exception as e:
                    print(e)

    def __invoke_new_circuit(self, m_temp_controller):
        try:
            m_temp_controller.signal(Signal.NEWNYM)
        except Exception as ex:
            print(ex, flush=True)

    def __on_create_session(self, tor_based):
        headers = {
            'User-Agent': CRAWL_SETTINGS_CONSTANTS.S_USER_AGENT if tor_based else 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
            'Cache-Control': 'no-cache'
        }
        return self.__session, headers

    def __on_proxy(self):
        proxy_settings = self.TOR_PROXIES[self.__proxy_index % len(self.TOR_PROXIES)]
        self.__proxy_index = (self.__proxy_index + 1) % len(self.TOR_PROXIES)
        return proxy_settings, self.__proxy_index

    def invoke_trigger(self, command, data=None):
        if command is TOR_COMMANDS.S_CREATE_SESSION:
            return self.__on_create_session(data[0])
        elif command is TOR_COMMANDS.S_PROXY:
            return self.__on_proxy()
