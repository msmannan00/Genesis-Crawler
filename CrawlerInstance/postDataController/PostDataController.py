import json
import threading
import requests

from asyncio import sleep
from GenesisCrawlerServices.constants.enums import MongoDBCommands
from GenesisCrawlerServices.mongoDBService.mongoDBController import mongoDBController


class PostDataController:

    # Crawler Instances & Threads
    m_main_thread = None

    # Initializations
    def __init__(self):
        pass

    def run(self):
        self.m_main_thread = threading.Thread(target=self.crawlThreadManager)
        self.m_main_thread.start()

    def postJSON(self, pJson):
        url = "http://genesishiddentechnologies.com/update_cache?dedicated=true"
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        requests.post(url, data=json.dumps(pJson), headers=headers)

    def crawlThreadManager(self):
        while True:
            sleep(1000)
            response = mongoDBController.getInstance().onRequest(MongoDBCommands.mongoDB_get_parsed_url, None)
            self.postJSON(response)

