from jaccard_index.jaccard import jaccard_index

from crawler.crawler_instance.genbot_service.html_parse_manager import html_parse_manager
from crawler.crawler_instance.genbot_service.web_request_handler import webRequestManager
from crawler.crawler_services.crawler_services.url_duplication_manager.html_duplication_controller import \
    html_duplication_controller

base1 = "https://bbc.com/news/world-europe-62899474"
base2 = "https://bbc.com"

__m_web_request_handler = webRequestManager()
m_redirected_url1, m_response1, m_doc_1 = __m_web_request_handler.load_url(base1)
m_redirected_url2, m_response2, m_doc_2 = __m_web_request_handler.load_url(base2)

ss = m_doc_1
ss1 = m_doc_2

m_html_parser = html_parse_manager(base1, m_doc_1)
m_html_parser.feed(m_doc_1)
m_title, x1, x2, m_important_content, m_important_content_hidden, m_meta_keywords, m_doc_1, m_content_type, m_sub_url, m_images, m_document, m_video, m_validity_score, ss = m_html_parser.parse_html_files()

m_html_parser = html_parse_manager(base2, m_doc_2)
m_html_parser.feed(m_doc_2)
m_title, x1, x2, m_important_content, m_important_content_hidden, m_meta_keywords, m_doc_2, m_content_type, m_sub_url, m_images, m_document, m_video, m_validity_score, cc = m_html_parser.parse_html_files()

doc1 = " ".join(list(set(m_doc_1.split(" "))))
doc2 = " ".join(list(set(m_doc_2.split(" "))))

__html_duplication_handler = html_duplication_controller()
__html_duplication_handler.on_insert_content(doc2)
m_score = __html_duplication_handler.verify_content_duplication(doc1)
print(m_score)
