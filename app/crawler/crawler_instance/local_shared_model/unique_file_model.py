# Non Parsed URL Model
from pydantic import BaseModel
from typing import List


class unique_file_model:

    m_documents = []
    m_videos = []
    m_images = []
    m_content = []

    def __init__(self, p_documents, p_videos, p_images):
        self.m_images = p_images
        self.m_documents = p_documents
        self.m_videos = p_videos



