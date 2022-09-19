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
        "http": "socks5h://10.0.0.6:" + "9052",
        "https": "socks5h://10.0.0.6:" + "9052"
    },
    {
        "http": "socks5h://10.0.0.7:" + "9054",
        "https": "socks5h://10.0.0.7:" + "9054"
    },
    {
        "http": "socks5h://10.0.0.8:" + "9056",
        "https": "socks5h://10.0.0.8:" + "9056"
    },
    {
        "http": "socks5h://10.0.0.9:" + "9058",
        "https": "socks5h://10.0.0.9:" + "9058"
    },
    {
        "http": "socks5h://10.0.0.10:" + "9060",
        "https": "socks5h://10.0.0.10:" + "9060"
    },
    {
        "http": "socks5h://10.0.0.11:" + "9062",
        "https": "socks5h://10.0.0.11:" + "9062"
    },
    {
        "http": "socks5h://10.0.0.12:" + "9064",
        "https": "socks5h://10.0.0.12:" + "9064"
    },
    {
        "http": "socks5h://10.0.0.13:" + "9066",
        "https": "socks5h://10.0.0.13:" + "9066"
    },
    {
        "http": "socks5h://10.0.0.14:" + "9068",
        "https": "socks5h://10.0.0.14:" + "9068"
    },
    {
        "http": "socks5h://10.0.0.15:" + "9070",
        "https": "socks5h://10.0.0.15:" + "9070"
    },
    {
        "http": "socks5h://10.0.0.16:" + "9072",
        "https": "socks5h://10.0.0.16:" + "9072"
    },
    {
        "http": "socks5h://10.0.0.17:" + "9074",
        "https": "socks5h://10.0.0.17:" + "9074"
    }
]