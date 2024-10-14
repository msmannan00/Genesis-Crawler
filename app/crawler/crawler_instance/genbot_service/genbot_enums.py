import enum
from threading import Lock


class ICRAWL_CONTROLLER_COMMANDS(enum.Enum):
  S_INIT_CRAWLER_INSTANCE = 1
  S_START_CRAWLER_INSTANCE = 2
  S_GET_CRAWLED_DATA = 3
  S_INVOKE_THREAD = 4


class PARSE_TAGS(enum.Enum):
  S_TITLE = 1
  S_META = 2
  S_KEYWORD = 3
  S_HEADER = 4
  S_PARAGRAPH = 5
  S_SPAN = 6
  S_DIV = 7
  S_BR = 8
  S_NONE = -1


class CRAWL_STATUS_TYPE:
  S_NONE = "running"
  S_LOW_YIELD = "low yield url"
  S_DUPLICATE = "duplicate url"
  S_FETCH_ERROR = "timeout"


CRAWL_HOST_LOCKS = [Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock()]
