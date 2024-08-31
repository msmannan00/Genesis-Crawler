from abc import ABC
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.probability import FreqDist
from typing import List, Tuple
from urllib.parse import urljoin
import nltk
import re

from app.crawler.crawler_instance.local_shared_model.index_model import index_model, index_model_init
from app.crawler.crawler_instance.local_shared_model.url_model import url_model
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.crawler_instance.helper_services.helper_method import helper_method

nltk.download('punkt')
nltk.download('stopwords')

class html_parse_manager(HTMLParser, ABC):

    def __init__(self, html_content: str, request_model: url_model):
        super().__init__()
        self.base_url = request_model.m_url
        self.html_content = html_content
        self.request_model = request_model
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()

    def extract_title(self) -> str:
        """Extract the title from the HTML."""
        title_tag = self.soup.find('title')
        return title_tag.get_text(strip=True).lower() if title_tag else ''

    def extract_meta_description(self) -> str:
        """Extract the meta description from the HTML."""
        meta_tag = self.soup.find('meta', attrs={'name': 'description'})
        return meta_tag['content'].strip().lower() if meta_tag and 'content' in meta_tag.attrs else ''

    def extract_meta_keywords(self) -> List[str]:
        """Extract the meta keywords from the HTML."""
        meta_tag = self.soup.find('meta', attrs={'name': 'keywords'})
        if meta_tag and 'content' in meta_tag.attrs:
            return [keyword.strip().lower() for keyword in meta_tag['content'].split(',')]
        return []

    def extract_content(self) -> str:
        """Extract the main content from the HTML, excluding unwanted elements."""
        for tag in self.soup(['script', 'style', 'noscript', '[document]', 'header', 'footer', 'aside']):
            tag.decompose()

        content = ' '.join(self.soup.stripped_strings)
        return content.lower()

    def extract_important_content(self) -> str:
        """Extract important content such as headers, strong, and emphasized text."""
        important_tags = self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'em', 'b', 'blockquote'])
        return ' '.join(tag.get_text(strip=True).lower() for tag in important_tags)

    def extract_sub_urls(self) -> Tuple[List[str], List[str]]:
        """Extract unique and cleaned images and documents (excluding videos) from the HTML."""
        seen_urls = set()

        images = []
        for img in self.soup.find_all('img'):
            if 'src' in img.attrs:
                img_url = urljoin(self.base_url, img['src'])
                cleaned_img_url = helper_method.on_clean_url(img_url)
                if cleaned_img_url not in seen_urls:
                    seen_urls.add(cleaned_img_url)
                    images.append(cleaned_img_url)

        documents = []
        for a in self.soup.find_all('a', href=True):
            href = a['href']
            # Check if the href ends with allowed document types
            if any(href.endswith(ext) for ext in CRAWL_SETTINGS_CONSTANTS.S_DOC_TYPES) or 'download' in a.get('rel', []):
                doc_url = urljoin(self.base_url, href)
                cleaned_doc_url = helper_method.on_clean_url(doc_url)
                if cleaned_doc_url not in seen_urls:
                    seen_urls.add(cleaned_doc_url)
                    seen_urls.add(cleaned_doc_url)
                    documents.append(cleaned_doc_url)

        return images, documents

    def extract_content_tokens(self) -> List[str]:
        """Tokenize and stem the main content, removing stopwords."""
        content = self.extract_content()
        tokens = [word for word in word_tokenize(content) if word.isalpha()]
        filtered_tokens = [token for token in tokens if token.lower() not in self.stop_words]
        stemmed_tokens = [self.stemmer.stem(token) for token in filtered_tokens]
        return stemmed_tokens

    def extract_keywords(self) -> List[str]:
        """Extract significant keywords based on frequency and importance."""
        tokens = self.extract_content_tokens()
        fdist = FreqDist(tokens)
        most_common = fdist.most_common(10)
        return [word for word, freq in most_common]

    def calculate_validity_score(self) -> int:
        """Calculate the validity score based on content quality."""
        tokens = self.extract_content_tokens()
        non_stopwords = [word for word in tokens if word.lower() not in self.stop_words]
        token_count = len(tokens)
        unique_non_stopwords = len(set(non_stopwords))

        if token_count == 0:
            return 0

        score = (len(non_stopwords) / token_count) * 70 + (unique_non_stopwords / token_count) * 30
        return int(score)

    def generate_content_summary(self) -> str:
        """Generate a brief summary or snippet of the content."""
        content = self.extract_content()
        sentences = re.split(r'(?<=[.!?]) +', content)
        summary = ' '.join(sentences[:3]) if len(sentences) > 3 else content
        return summary

    def parse_html_files(self) -> index_model:
        """Implement parsing logic for extracting data and creating an index model."""
        images, documents = self.extract_sub_urls()
        return index_model_init(
            self.request_model,
            m_title=self.extract_title(),
            m_meta_description=self.extract_meta_description(),
            m_meta_keywords=self.extract_meta_keywords(),
            m_content=self.extract_content(),
            m_important_content=self.extract_important_content(),
            m_content_tokens=self.extract_content_tokens(),
            m_keywords=self.extract_keywords(),
            m_images=images,
            m_document=documents,
            m_video=self.extract_media('video'),
            m_validity_score=self.calculate_validity_score(),
            m_content_summary=self.generate_content_summary()
        )

    def extract_media(self, tag_name: str) -> List[str]:
        """Extract media elements such as videos."""
        media_tags = self.soup.find_all(tag_name)
        return [urljoin(self.base_url, tag['src']) for tag in media_tags if 'src' in tag.attrs]

