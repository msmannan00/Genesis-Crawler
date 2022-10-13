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
        "http": "socks5h://0.0.0.0:" + "9054",
        "https": "socks5h://0.0.0.0:" + "9054"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9056",
        "https": "socks5h://0.0.0.0:" + "9056"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9058",
        "https": "socks5h://0.0.0.0:" + "9058"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9060",
        "https": "socks5h://0.0.0.0:" + "9060"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9062",
        "https": "socks5h://0.0.0.0:" + "9062"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9064",
        "https": "socks5h://0.0.0.0:" + "9064"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9066",
        "https": "socks5h://0.0.0.0:" + "9066"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9068",
        "https": "socks5h://0.0.0.0:" + "9068"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9070",
        "https": "socks5h://0.0.0.0:" + "9070"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9072",
        "https": "socks5h://0.0.0.0:" + "9072"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9074",
        "https": "socks5h://0.0.0.0:" + "9074"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9076",
        "https": "socks5h://0.0.0.0:" + "9076"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9078",
        "https": "socks5h://0.0.0.0:" + "9078"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9080",
        "https": "socks5h://0.0.0.0:" + "9080"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9082",
        "https": "socks5h://0.0.0.0:" + "9082"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9084",
        "https": "socks5h://0.0.0.0:" + "9084"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9086",
        "https": "socks5h://0.0.0.0:" + "9086"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9088",
        "https": "socks5h://0.0.0.0:" + "9088"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9090",
        "https": "socks5h://0.0.0.0:" + "9090"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9092",
        "https": "socks5h://0.0.0.0:" + "9092"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9094",
        "https": "socks5h://0.0.0.0:" + "9094"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9096",
        "https": "socks5h://0.0.0.0:" + "9096"
    },
    {
        "http": "socks5h://0.0.0.0:" + "9098",
        "https": "socks5h://0.0.0.0:" + "9098"
    },
    {
        "http": "socks5h://0.0.0.0:" + "10000",
        "https": "socks5h://0.0.0.0:" + "10000"
    },
    {
        "http": "socks5h://0.0.0.0:" + "10002",
        "https": "socks5h://0.0.0.0:" + "10002"
    },
    {
        "http": "socks5h://0.0.0.0:" + "10004",
        "https": "socks5h://0.0.0.0:" + "10004"
    },
    {
        "http": "socks5h://0.0.0.0:" + "10006",
        "https": "socks5h://0.0.0.0:" + "10006"
    },
    {
        "http": "socks5h://0.0.0.0:" + "10008",
        "https": "socks5h://0.0.0.0:" + "10008"
    },
    {
        "http": "socks5h://0.0.0.0:" + "10010",
        "https": "socks5h://0.0.0.0:" + "10010"
    }
]