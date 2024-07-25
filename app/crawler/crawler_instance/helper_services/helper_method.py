import os
import re
from urllib.parse import urlparse
from gensim.parsing.preprocessing import STOPWORDS


class helper_method:

    @staticmethod
    def get_host_url(p_url):
        parsed_uri = urlparse(p_url)
        host_url = f"{parsed_uri.scheme}://{parsed_uri.netloc}"
        return host_url

    @staticmethod
    def strip_special_character(p_text):
        return re.sub(r"^\W+", "", p_text)

    @staticmethod
    def split_host_url(p_url):
        parsed_uri = urlparse(p_url)
        host_url = f"{parsed_uri.scheme}://{parsed_uri.netloc}"
        subhost = p_url[len(host_url):] or "na"
        return host_url, subhost

    @staticmethod
    def on_clean_url(p_url):
        p_url = p_url.lstrip("www.")
        return p_url.rstrip("/ ")

    @staticmethod
    def normalize_slashes(p_url):
        p_url = '/'.join(filter(None, str(p_url).split('/')))
        p_url = p_url.replace("http:/", "http://").replace("https:/", "https://").replace("ftp:/", "ftp://")
        return p_url

    @staticmethod
    def is_url_base_64(p_url):
        return p_url.startswith("duplicationHandlerService:")

    @staticmethod
    def is_uri_validator(p_url):
        try:
            result = urlparse(p_url)
            return all([result.scheme, result.netloc])
        except:
            return False

    @staticmethod
    def is_stop_word(p_word):
        return p_word in STOPWORDS

    @staticmethod
    def clear_folder(p_path):
        for f in os.listdir(p_path):
            os.remove(os.path.join(p_path, f))

    @staticmethod
    def write_content_to_path(p_path, p_content):
        with open(p_path, "wb") as file:
            file.write(p_content)
