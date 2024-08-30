from dataclasses import dataclass
from typing import List

@dataclass
class card_extraction_model:
    title: str
    url: List[str]
    text: List[str]
    weblink: List[str]
    dumplink: List[str]
    extra_tags: List[str]
