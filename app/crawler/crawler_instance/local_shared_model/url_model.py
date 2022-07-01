# Non Parsed URL Model
from pydantic import BaseModel
from typing import List


class url_model(BaseModel):
    m_url: str
    m_depth: int


class url_model_list(BaseModel):
    sub_url_pending: List[url_model]


def url_model_init(m_url, m_depth):
    return url_model(**{'m_url': m_url, "m_depth": m_depth})
