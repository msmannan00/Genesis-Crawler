import warnings
import logging
from time import sleep

from celery import Celery, Task
from multiprocessing import Process

from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.crawler_instance.genbot_service.genbot_controller import genbot_instance


class celery_manager:
    __instance = None

    @staticmethod
    def get_instance():
        if celery_manager.__instance is None:
            celery_manager()
        return celery_manager.__instance

    def __init__(self):
        if celery_manager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            celery_manager.__instance = self
            warnings.filterwarnings("ignore")
            logging.getLogger('celery').setLevel(logging.CRITICAL)

            self.app = Celery('crawler', broker='redis://localhost:6379/0')
            self.app.autodiscover_tasks()
            self.app.conf.worker_task_log_format = None
            self.app.conf.update(
                worker_log_color=False,
                worker_redirect_stdouts_level='ERROR',
                worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
            )
            self.process_url_task = self.app.task(self.process_url)
            worker_process = Process(target=self.start_worker)
            worker_process.start()

    def start_worker(self):
        self.app.worker_main([
            'worker',
            '--loglevel=ERROR',
            '--logfile=/dev/null',
            '--without-gossip',
            '--without-mingle',
            '--without-heartbeat',
            f'--concurrency={CRAWL_SETTINGS_CONSTANTS.S_MAX_THREAD_COUNT}'
        ])

    @staticmethod
    def process_url(url, virtual_id):
        print(f"Processing URL {url} with virtual_id {virtual_id}")

    def process_url_async(self, url, virtual_id):
        genbot_instance(url, virtual_id)
