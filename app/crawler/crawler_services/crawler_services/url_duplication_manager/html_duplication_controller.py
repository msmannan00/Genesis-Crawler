# Local Imports
import logging
from time import sleep

from html_similarity import structural_similarity
from html_similarity.style_similarity import style_similarity
from jaccard_index.jaccard import jaccard_index
logger_1 = logging.getLogger('style_similarity')
logger_2 = logging.getLogger('structural_similarity')
logger = logging.getLogger('my-logger')
logger.propagate = False
logger_1.propagate = False
logger_2.propagate = False
logger = logging.getLogger()
logger.disabled = True


class html_duplication_controller:

    __k_score = 0.3

    # Initializations

    def __init__(self):
        self.__m_duplication_content_handler = {""}

    def verify_content_duplication(self, m_content):
        m_max_k_score = 0

        try:
            for val in self.__m_duplication_content_handler:
                m_score = jaccard_index(val, m_content, 3)
                if m_score > m_max_k_score:
                    m_max_k_score = m_score
                if m_max_k_score > 0.7:
                    break

        except Exception as ex:
            print(ex, flush=True)

        return m_max_k_score

    def verify_structural_duplication(self, m_doc_1, m_doc_2):
        m_score = self.__k_score * structural_similarity(m_doc_1, m_doc_2) + (1 - self.__k_score*0.2) * style_similarity(m_doc_1, m_doc_2)
        return m_score

    def on_insert_content(self, m_content):
        self.__m_duplication_content_handler.add(m_content)
