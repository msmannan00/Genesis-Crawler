from dataclasses import dataclass
from typing import List

@dataclass
class card_extraction_model:
    m_title: str
    m_url: str
    m_content: str
    m_base_url: str
    m_important_content: str
    m_weblink: List[str]
    m_dumplink: List[str]
    m_extra_tags: List[str]
