# Local Imports
from pydantic import BaseModel
from crawler.crawler_instance.local_shared_model.url_model import url_model


class index_model(BaseModel):
    m_base_model: url_model
    m_title: str
    m_meta_description: str
    m_title_hidden: str
    m_important_content: str
    m_important_content_hidden: str
    m_meta_keywords: str
    m_content: str
    m_content_type: str
    m_extended_content: str
    m_sub_url: list
    m_images: list = []
    m_document: list
    m_video: list
    m_validity_score: int
    m_user_crawled: bool = False


def index_model_init(p_base_model, p_title, p_meta_description, p_title_hidden, p_important_content, p_important_content_hidden, p_meta_keywords, p_content, p_content_type, p_sub_url, p_document, p_video, p_validity_score, p_extended_content):
    return index_model(**{'m_base_model': p_base_model, "m_title": p_title, "m_meta_description": p_meta_description, "m_title_hidden": p_title_hidden, "m_important_content": p_important_content, "m_important_content_hidden": p_important_content_hidden, "m_meta_keywords": p_meta_keywords, "m_content": p_content, "m_content_type": p_content_type, "m_sub_url": p_sub_url, "m_document": p_document, "m_video": p_video, "m_validity_score": p_validity_score, "m_extended_content": p_extended_content})


def index_image_model_init(p_base_model, p_title, p_meta_description, p_title_hidden, p_important_content, p_important_content_hidden, p_meta_keywords, p_content, p_content_type, p_sub_url, p_images, p_document, p_video, p_validity_score, p_extended_content):
    m_json = {'m_images': p_images, 'm_base_model': p_base_model, "m_title": p_title, "m_meta_description": p_meta_description, "m_title_hidden": p_title_hidden, "m_important_content": p_important_content, "m_important_content_hidden": p_important_content_hidden, "m_meta_keywords": p_meta_keywords, "m_content": p_content, "m_content_type": p_content_type, "m_sub_url": p_sub_url, "m_document": p_document, "m_video": p_video, "m_validity_score": p_validity_score, "m_extended_content": p_extended_content}
    m_json.update(p_images.dict())

    return index_model(**m_json)
