import base64
import time
from fernet import Fernet

from app.crawler.constants.strings import MANAGE_MESSAGES
from app.crawler.crawler_services.helper_services.env_handler import env_handler


class crypto_handler:
    __instance = None

    @staticmethod
    def get_instance():
        if crypto_handler.__instance is None:
            crypto_handler()
        return crypto_handler.__instance

    def __init__(self):
        if crypto_handler.__instance is not None:
            raise Exception(MANAGE_MESSAGES.S_SINGLETON_EXCEPTION)
        else:
            crypto_handler.__instance = self

        self.fernet_key = env_handler.get_instance().env('S_FERNET_KEY')
        self.app_block_key = env_handler.get_instance().env('S_APP_BLOCK_KEY')

    def generate_secret_token(self):
        fernet = Fernet(base64.urlsafe_b64encode(self.fernet_key.encode()))
        secret_data = f"{self.app_block_key}----{int(time.time())}"
        return fernet.encrypt(secret_data.encode()).decode()
