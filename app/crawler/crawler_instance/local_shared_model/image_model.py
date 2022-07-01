# Non Parsed URL Model
from typing import List

from pydantic import BaseModel


class image_model(BaseModel):
    m_url: str
    m_type: str


class image_model_list(BaseModel):
    m_images: List[image_model]


def image_model_init(p_url, p_type):
    return image_model(**{'m_url': p_url, "m_type": p_type})
