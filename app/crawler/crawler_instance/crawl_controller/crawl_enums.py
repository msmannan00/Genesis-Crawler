import enum


class NETWORK_STATUS(enum.Enum):
    S_ONLINE = 1
    S_OUTAGE = 2
    S_REACHABLE = 3


class CRAWL_CONTROLLER_COMMANDS(enum.Enum):
    S_RUN_CRAWLER = 1


class CRAWL_MODEL_COMMANDS(enum.Enum):
    S_INIT = 0
    S_INIT_DIRECT = 1
