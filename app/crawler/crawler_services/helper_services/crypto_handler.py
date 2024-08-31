import base64
import os
import time
from dotenv import load_dotenv
from fernet import Fernet

from crawler.constants.strings import MANAGE_CRAWLER_MESSAGES

class crypto_handler:
    __instance = None

    dotenv_path = os.path.join(os.getcwd(), '.env')
    load_dotenv(dotenv_path)

    @staticmethod
    def get_instance():
        if crypto_handler.__instance is None:
            crypto_handler()
        return crypto_handler.__instance

    def __init__(self):
        if crypto_handler.__instance is not None:
            raise Exception(MANAGE_CRAWLER_MESSAGES.S_SINGLETON_EXCEPTION)
        else:
            crypto_handler.__instance = self

        self.fernet_key = os.getenv('S_FERNET_KEY')
        self.app_block_key = os.getenv('S_APP_BLOCK_KEY')

    def generate_secret_token(self):
        fernet = Fernet(base64.urlsafe_b64encode(self.fernet_key.encode()))
        secret_data = f"{self.app_block_key}----{int(time.time())}"
        return fernet.encrypt(secret_data.encode()).decode()
