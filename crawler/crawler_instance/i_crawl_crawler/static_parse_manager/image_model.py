# Non Parsed URL Model
from crawler.crawler_instance.constants.strings import STRINGS


class image_model:
    m_url = STRINGS.S_EMPTY
    m_type = STRINGS.S_EMPTY

    def __init__(self, p_url, p_type):
        self.m_url = p_url
        self.m_type = p_type
