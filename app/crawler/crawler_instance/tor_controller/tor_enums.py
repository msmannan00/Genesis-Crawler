from crawler.constants.constant import RAW_PATH_CONSTANTS, TOR_CONSTANTS


class TOR_COMMANDS:
    S_START = 1
    S_RESTART = 2
    S_GENERATED_CIRCUIT = 3
    S_RELEASE_SESSION = 4
    S_CREATE_SESSION = 5
    S_PROXY = 6


class TOR_CMD_COMMANDS:
    S_START_DIRECT = RAW_PATH_CONSTANTS.S_SIGWIN_PATH + " " + TOR_CONSTANTS.S_SHELL_CONFIG_PATH + " " + TOR_CONSTANTS.S_TOR_PATH + " " + "build-start-tor"
    S_START_DOCKERISED = "." + TOR_CONSTANTS.S_SHELL_CONFIG_PATH + " " + TOR_CONSTANTS.S_TOR_PATH + " " + "build-start-tor"


class TOR_STATUS:
    S_RUNNING = 1
    S_PAUSE = 2
    S_STOP = 3
    S_READY = 4
    S_START = 5
    S_CLOSE = 6


TOR_PROXIES = [
    {
        "http": "socks5h://172.0.0.10:" + "9152",
        "https": "socks5h://172.0.0.10:" + "9152"
    },
    {
        "http": "socks5h://172.0.0.11:" + "9154",
        "https": "socks5h://172.0.0.11:" + "9154"
    },
    {
        "http": "socks5h://172.0.0.12:" + "9156",
        "https": "socks5h://172.0.0.12:" + "9156"
    },
    {
        "http": "socks5h://172.0.0.13:" + "9158",
        "https": "socks5h://172.0.0.13:" + "9158"
    },
    {
        "http": "socks5h://172.0.0.14:" + "9160",
        "https": "socks5h://172.0.0.14:" + "9160"
    },
    {
        "http": "socks5h://172.0.0.15:" + "9162",
        "https": "socks5h://172.0.0.15:" + "9162"
    },
    {
        "http": "socks5h://172.0.0.16:" + "9164",
        "https": "socks5h://172.0.0.16:" + "9164"
    },
    {
        "http": "socks5h://172.0.0.17:" + "9166",
        "https": "socks5h://172.0.0.17:" + "9166"
    },
    {
        "http": "socks5h://172.0.0.18:" + "9168",
        "https": "socks5h://172.0.0.18:" + "9168"
    },
    {
        "http": "socks5h://172.0.0.19:" + "9170",
        "https": "socks5h://172.0.0.19:" + "9170"
    },
    {
        "http": "socks5h://172.0.0.20:" + "9172",
        "https": "socks5h://172.0.0.20:" + "9172"
    },
    {
        "http": "socks5h://172.0.0.21:" + "9174",
        "https": "socks5h://172.0.0.21:" + "9174"
    },
    {
        "http": "socks5h://172.0.0.22:" + "9176",
        "https": "socks5h://172.0.0.22:" + "9176"
    },
    {
        "http": "socks5h://172.0.0.23:" + "9178",
        "https": "socks5h://172.0.0.23:" + "9178"
    },
    {
        "http": "socks5h://172.0.0.24:" + "9180",
        "https": "socks5h://172.0.0.24:" + "9180"
    }
]
TOR_CONTROL_PROXIES = [
    {
        "proxy": "172.0.0.10",
        "port": 9153
    },
    {
        "proxy": "172.0.0.11",
        "port": 9155
    },
    {
        "proxy": "172.0.0.12",
        "port": 9157
    },
    {
        "proxy": "172.0.0.13",
        "port": 9159
    },
    {
        "proxy": "172.0.0.14",
        "port": 9161
    },
    {
        "proxy": "172.0.0.15",
        "port": 9163
    },
    {
        "proxy": "172.0.0.16",
        "port": 9165
    },
    {
        "proxy": "172.0.0.17",
        "port": 9167
    },
    {
        "proxy": "172.0.0.18",
        "port": 9169
    },
    {
        "proxy": "172.0.0.19",
        "port": 9171
    },
    {
        "proxy": "172.0.0.20",
        "port": 9173
    },
    {
        "proxy": "172.0.0.21",
        "port": 9175
    },
    {
        "proxy": "172.0.0.22",
        "port": 9177
    },
    {
        "proxy": "172.0.0.23",
        "port": 9179
    },
    {
        "proxy": "172.0.0.24",
        "port": 9181
    }
]