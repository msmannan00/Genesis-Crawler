from urllib.parse import urlparse
from gensim.parsing.preprocessing import STOPWORDS


class HelperMethod:

    @staticmethod
    def get_host_url(p_url):
        parsed_uri = urlparse(p_url)
        host_url = f"{parsed_uri.scheme}://{parsed_uri.netloc}"
        return host_url

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
    def is_stop_word(p_word):
        return p_word in STOPWORDS
