from pydantic import BaseModel
from typing import List
from crawler.crawler_instance.local_shared_model.url_model import url_model

class index_model(BaseModel):
    m_base_url: str
    m_url: str
    m_title: str
    m_meta_description: str
    m_content: str
    m_important_content: str
    m_images: List[str]
    m_document: List[str]
    m_video: List[str]
    m_validity_score: int

def index_model_init(
    m_base_url: str,
    m_url: str,
    m_title: str,
    m_meta_description: str,
    m_content: str,
    m_important_content: str,
    m_images: List[str],
    m_document: List[str],
    m_video: List[str],
    m_validity_score: int,
) -> index_model:
    return index_model(
        m_base_url=m_base_url,
        m_url=m_url,
        m_title=m_title,
        m_meta_description=m_meta_description,
        m_content=m_content,
        m_important_content=m_important_content,
        m_images=m_images,
        m_document=m_document,
        m_video=m_video,
        m_validity_score=m_validity_score,
    )
