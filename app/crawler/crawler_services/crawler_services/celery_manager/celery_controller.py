import warnings
import logging
from celery import Celery
import subprocess
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from crawler.crawler_instance.genbot_service.genbot_controller import genbot_instance

app = Celery('crawler', broker='redis://localhost:6379/0')


class celery_controller:
    __instance = None

    @staticmethod
    def get_instance():
        if celery_controller.__instance is None:
            celery_controller()
        return celery_controller.__instance

    def __init__(self):
        if celery_controller.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            celery_controller.__instance = self
            warnings.filterwarnings("ignore")
            logging.getLogger('celery').setLevel(logging.DEBUG)
            self.clear_redis_database()
            app.conf.worker_task_log_format = None
            app.conf.task_acks_late = True
            app.conf.worker_prefetch_multiplier = 1
            app.conf.update(
                worker_log_color=True,
                worker_redirect_stdouts_level='DEBUG',
                worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
            )

            self.clear_queue()
            self.start_worker()

    def clear_redis_database(self):
        try:
            subprocess.run(['redis-cli', 'FLUSHALL'], check=True)
            print("Redis database cleared.")
        except subprocess.CalledProcessError as e:
            print(f"Error clearing Redis database: {e}")

    def clear_queue(self):
        try:
            queue_purged = app.control.purge()
            print(f"Queue cleared. {queue_purged} tasks removed.")
        except Exception as e:
            print(f"Error clearing queue: {e}")

    def start_worker(self, concurrency=14):
        subprocess.Popen([
            'celery', '-A', 'celery_controller', 'worker',
            '--loglevel=DEBUG',
            f'--concurrency={concurrency}',
            '--without-gossip',
            '--without-mingle',
            '--without-heartbeat',
            '--pool=gevent'
        ])

    def run_task(self, url, virtual_id):
        print(f"Dispatching simple_task with url: {url} and virtual_id: {virtual_id}")
        simple_task.delay(url, virtual_id)


@app.task(name='celery_controller.simple_task')
def simple_task(url, virtual_id):
    genbot_instance(url, virtual_id)


if __name__ == "__main__":
    manager = celery_controller.get_instance()
    print("Celery worker with queue cleared and multiple processes started.")
