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

from crawler.crawler_instance.local_shared_model.index_model import index_model, index_model_init
from crawler.crawler_instance.local_shared_model.url_model import url_model
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.crawler_instance.helper_services.helper_method import helper_method
from gensim.summarization import summarize

class html_parse_manager(HTMLParser, ABC):

    def extract_important_content(self) -> str:
        important_tags = self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'em', 'b', 'blockquote'])
        important_content = ' '.join(tag.get_text(strip=True) for tag in important_tags)
        cleaned_content = ' '.join(important_content.split())

        if len(cleaned_content.split()) > 50:
            try:
                summarized_content = summarize(cleaned_content, ratio=0.2)
                return summarized_content
            except ValueError:
                return cleaned_content
        else:
            return cleaned_content

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

    def extract_text_sections(self) -> List[str]:
        sections = []
        stop_words = set(stopwords.words('english'))
        tags_to_extract = ['p', 'div', 'article', 'section', 'blockquote', 'aside']

        for tag in self.soup.find_all(tags_to_extract):
            section_text = tag.get_text(strip=True)
            cleaned_section_text = re.sub(r'[^\w\s]', '', re.sub(r'\s+', ' ', section_text)).strip()

            tokens = [word for word in word_tokenize(cleaned_section_text) if word.isalpha()]
            filtered_tokens = [word for word in tokens if word.lower() not in stop_words]

            if len(filtered_tokens) > 5:
                sentences = re.split(r'[.!?]', cleaned_section_text)
                long_sentences = [sentence for sentence in sentences if len(sentence.split()) > 6]

                if len(long_sentences) > 0:
                    sections.append(cleaned_section_text)

        return sections

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
            m_base_url = helper_method.get_base_url(self.base_url),
            m_url = self.base_url,
            m_title=self.extract_title(),
            m_meta_description=self.extract_meta_description(),
            m_content=self.extract_content(),
            m_important_content=self.extract_important_content(),
            m_images=images,
            m_document=documents,
            m_video=self.extract_media('video'),
            m_validity_score=self.calculate_validity_score(),
        )

    def extract_media(self, tag_name: str) -> List[str]:
        """Extract media elements such as videos."""
        media_tags = self.soup.find_all(tag_name)
        return [urljoin(self.base_url, tag['src']) for tag in media_tags if 'src' in tag.attrs]

