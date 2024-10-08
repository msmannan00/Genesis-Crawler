from dataclasses import dataclass, field
from typing import List

@dataclass
class card_extraction_model:
    m_title: str = ""
    m_url: str = ""
    m_content: str = ""
    m_base_url: str = ""
    m_important_content: str = ""
    m_content_type: str = "general"
    m_weblink: List[str] = field(default_factory=list)
    m_dumplink: List[str] = field(default_factory=list)
    m_extra_tags: List[str] = field(default_factory=list)
