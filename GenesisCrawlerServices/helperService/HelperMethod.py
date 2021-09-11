# Local Imports
import json
import pickle
import re
from datetime import datetime
from urllib.parse import urlparse


# Helper Method Classes
from GenesisCrawlerServices.constants import strings


class HelperMethod:

    # Base URL Verify - In case if url is non parsable image
    @staticmethod
    def isURLBase64(p_url):
        if str(p_url).startswith("duplicationHandlerService:"):
            return True
        else:
            return False

    # Extract URL Host
    @staticmethod
    def getHostURL(p_url):
        m_parsed_uri = urlparse(p_url)
        m_host_url = '{uri.scheme}://{uri.netloc}/'.format(uri=m_parsed_uri)
        if m_host_url.endswith("/"):
            m_host_url = m_host_url[:-1]
        return m_host_url

    @staticmethod
    def splitHostURL(p_url):
        m_parsed_uri = urlparse(p_url)
        m_host_url = '{uri.scheme}://{uri.netloc}/'.format(uri=m_parsed_uri)
        if m_host_url.endswith("/"):
            m_host_url = m_host_url[:-1]
        return m_host_url, p_url[len(m_host_url):]

    # Append URL Protocol
    @staticmethod
    def appendProtocol(p_url):
        if not re.match('(?:http|ftp|https)://', p_url):
            return 'http://{}'.format(p_url)
        return p_url

    # URL Cleaner
    @staticmethod
    def cleanURL(p_url):
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

    # Save objects in case of application restart
    @staticmethod
    def saveObject(p_path, p_object):
        picklefile = open(p_path, 'wb')
        pickle.dump(p_object, picklefile)
        picklefile.close()

    # Load objects in case of application restart
    @staticmethod
    def loadObject(p_path):
        dbfile = open(p_path, 'rb')
        m_object = pickle.load(dbfile)
        return m_object

    @staticmethod
    def getMongoDBDate():
        return datetime.strptime("2017-10-13T10:53:53.000Z", "%Y-%m-%dT%H:%M:%S.000Z")


    @staticmethod
    def createJson(p_keys, p_values):
        m_json = {}
        for (key, value) in zip(p_keys, p_values):
            m_json[key] = value
        return json.dumps(m_json)

