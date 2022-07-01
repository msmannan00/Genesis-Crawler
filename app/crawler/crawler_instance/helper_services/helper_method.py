# Local Imports
import os
import re
from urllib.parse import urlparse
from gensim.parsing.preprocessing import STOPWORDS


class helper_method:

    @staticmethod
    def get_host_url(p_url):
        m_parsed_uri = urlparse(p_url)
        m_host_url = '{uri.scheme}://{uri.netloc}/'.format(uri=m_parsed_uri)
        if m_host_url.endswith("/"):
            m_host_url = m_host_url[:-1]
        return m_host_url

    @staticmethod
    def strip_special_character(p_text):
        m_text = re.sub(r"^\W+", "", p_text)
        return m_text

    @staticmethod
    def split_host_url(p_url):
        m_parsed_uri = urlparse(p_url)
        m_host_url = '{uri.scheme}://{uri.netloc}/'.format(uri=m_parsed_uri)
        if m_host_url.endswith("/"):
            m_host_url = m_host_url[:-1]

        m_subhost = p_url[len(m_host_url):]
        if len(m_subhost) == 1:
            m_subhost = "na"
        return m_host_url, m_subhost

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
        normalized_url = normalized_url.replace("http:/", "http://")
        normalized_url = normalized_url.replace("https:/", "https://")
        normalized_url = normalized_url.replace("ftp:/", "ftp://")
        return normalized_url

    @staticmethod
    def is_url_base_64(p_url):
        if str(p_url).startswith("duplicationHandlerService:"):
            return True
        else:
            return False

    @staticmethod
    def is_uri_validator(p_url):
        try:
            result = urlparse(p_url)
            return all([result.scheme, result.netloc])
        except:
            return False
    @staticmethod
    def is_stop_word(p_word):
        if p_word in STOPWORDS:
            return True
        else:
            return False

    @staticmethod
    def clear_folder(p_path):
        os.chdir(p_path)
        all_files = os.listdir()

        for f in all_files:
            os.remove(f)

    @staticmethod
    def write_content_to_path(p_path, p_content):
        m_url_path = p_path
        file = open(m_url_path, "wb")
        file.write(p_content)
        file.close()
