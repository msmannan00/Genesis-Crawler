# Non Parsed URL Model
from crawler_instance.constants.strings import GENERIC_STRINGS


class image_model:
    m_url = GENERIC_STRINGS.S_EMPTY
    m_type = GENERIC_STRINGS.S_EMPTY

    def __init__(self, p_url, p_type):
        self.m_url = p_url
        self.m_type = p_type
