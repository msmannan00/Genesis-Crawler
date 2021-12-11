# Local Imports
import datetime
from urllib.parse import urlparse

import requests
import urllib3
from gensim.parsing.preprocessing import STOPWORDS


class helper_method:

    # Base URL Verify - In case if url is non parsable image
    @staticmethod
    def is_url_base_64(p_url):
        if str(p_url).startswith("duplicationHandlerService:"):
            return True
        else:
            return False

    # Extract URL Host
    @staticmethod
    def get_host_url(p_url):
        m_parsed_uri = urlparse(p_url)
        m_host_url = '{uri.scheme}://{uri.netloc}/'.format(uri=m_parsed_uri)
        if m_host_url.endswith("/"):
            m_host_url = m_host_url[:-1]
        return m_host_url

    @staticmethod
    def split_host_url(p_url):
        m_parsed_uri = urlparse(p_url)
        m_host_url = '{uri.scheme}://{uri.netloc}/'.format(uri=m_parsed_uri)
        if m_host_url.endswith("/"):
            m_host_url = m_host_url[:-1]
        return m_host_url, p_url[len(m_host_url):]

    # URL Cleaner
    @staticmethod
    def on_clean_url(p_url):
        if p_url.startswith("http://www.") or p_url.startswith("https://www.") or p_url.startswith("www."):
            p_url = p_url.replace("www.", "", 1)

        while p_url.endswith("/") or p_url.endswith(" "):
            p_url = p_url[:-1]

        return p_url

    # Remove Extra Slashes
    @staticmethod
    def normalize_slashes(p_url):
        p_url = str(p_url)
        segments = p_url.split('/')
        correct_segments = []
        for segment in segments:
            if segment != '':
                correct_segments.append(segment)
        normalized_url = '/'.join(correct_segments)
        normalized_url = normalized_url.replace("http:/","http://")
        normalized_url = normalized_url.replace("https:/","https://")
        normalized_url = normalized_url.replace("ftp:/","ftp://")
        return normalized_url

    @staticmethod
    def on_create_session():
        m_request_handler = requests.Session()
        m_request_handler.max_redirects = 5
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        return m_request_handler

    @staticmethod
    def get_mongodb_date():
        return datetime.datetime.utcnow()

    @staticmethod
    def is_stop_word(p_word):
        if p_word in STOPWORDS:
            return True
        else:
            return False
