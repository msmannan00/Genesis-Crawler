import warnings
from celery import Celery
import subprocess
import sys
import os
import signal

from crawler.crawler_instance.genbot_service.genbot_unique_controller import genbot_unique_instance
from crawler.crawler_services.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.crawler_services.celery_manager.celery_enums import CELERY_CONNECTIONS, CELERY_COMMANDS
from crawler.crawler_instance.genbot_service.genbot_controller import genbot_instance
from crawler.constants.app_status import APP_STATUS
from crawler.crawler_services.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, REDIS_KEYS
from crawler.crawler_shared_directory.log_manager.log_controller import log

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

celery = Celery('crawler', broker=CELERY_CONNECTIONS.conn)

# Configure Celery task routing
celery.conf.task_routes = {
  'celery_controller.invoke_unique_crawler': {'queue': 'unique_crawler_queue'}
}

celery.conf.worker_task_log_format = None
celery.conf.task_acks_late = True
celery.conf.worker_prefetch_multiplier = 1
celery.conf.update(
  worker_log_color=True,
  worker_redirect_stdouts=True,
  worker_redirect_stdouts_level='DEBUG',
  worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
)

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
    self.__redis_controller = redis_controller.get_instance()
    self.__clear_redis_database()
    # if APP_STATUS.DOCKERIZED_RUN:
    #   self.__start_worker()
    #   self.__start_unique_crawler_worker()

  def __clear_redis_database(self):
    try:
      self.__redis_controller.invoke_trigger('S_FLUSH_ALL')
    except Exception:
      pass

  # def __start_worker(self):
  #   self.__stop_all_workers()
  #   subprocess.Popen([
  #     'celery', '-A', 'crawler.crawler_services.crawler_services.celery_manager', 'worker',
  #     '--loglevel=DEBUG',
  #     '--without-gossip',
  #     '--without-mingle',
  #     '--without-heartbeat',
  #     '--pool=gevent'
  #   ])
  #
  # def __start_unique_crawler_worker(self):
  #   self.__stop_all_workers()
  #   subprocess.Popen([
  #     'celery', '-A', 'crawler.crawler_services.crawler_services.celery_manager', 'worker',
  #     '--loglevel=DEBUG',
  #     '--without-gossip',
  #     '--without-mingle',
  #     '--without-heartbeat',
  #     '--pool=gevent',
  #     '-Q', 'unique_crawler_queue',
  #     '--concurrency=1'
  #   ])

  def __stop_all_workers(self):
    try:
      output = subprocess.check_output(['pgrep', '-f', 'celery'])
      pids = output.decode().strip().split("\n")
      for pid in pids:
        os.kill(int(pid), signal.SIGTERM)
    except subprocess.CalledProcessError:
      pass
    except Exception:
      pass

  def __run_crawler(self, url, virtual_id):
    start_crawler.delay(url, virtual_id)

  def __run_unique_task(self, url):
    # Queue the task
    invoke_unique_crawler.delay(url)

  def invoke_trigger(self, p_commands, p_data=None):
    if p_commands == CELERY_COMMANDS.S_START_CRAWLER:
      self.__run_crawler(p_data[0], p_data[1])
    if p_commands == CELERY_COMMANDS.S_INVOKE_UNIQUE_CRAWLER:
      self.__run_unique_task(p_data)


# Celery tasks
@celery.task(name='celery_controller.start_crawler')
def start_crawler(url, virtual_id):
  genbot_instance(url, virtual_id)

@celery.task(name='celery_controller.invoke_unique_crawler', bind=True)
def invoke_unique_crawler(_, url):
  genbot_unique_instance(url)

if __name__ == "__main__":
  manager = celery_controller.get_instance()