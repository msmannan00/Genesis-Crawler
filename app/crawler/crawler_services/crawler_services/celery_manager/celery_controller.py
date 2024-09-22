import logging
import warnings
from celery import Celery
import subprocess
import sys
import os
import redis
from logging.config import dictConfig

from crawler.crawler_instance.genbot_service.genbot_unique_controller import genbot_unique_instance
from crawler.crawler_services.crawler_services.celery_manager.celery_enums import CELERY_CONNECTIONS, ELASTIC_LOGGING, \
  CELERY_COMMANDS
from crawler.crawler_services.helper_services.env_handler import env_handler

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from crawler.crawler_instance.genbot_service.genbot_controller import genbot_instance
from crawler.constants.app_status import APP_STATUS

# Apply the custom logging configuration
dictConfig(ELASTIC_LOGGING.logging_config)
logger = logging.getLogger(__name__)

# Celery setup
celery = Celery('crawler', broker=CELERY_CONNECTIONS.conn)

celery.conf.worker_task_log_format = None
celery.conf.task_acks_late = True
celery.conf.worker_prefetch_multiplier = 1
celery.conf.update(
  worker_log_color=True,
  worker_redirect_stdouts=True,  # Ensure stdout is redirected to logs
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
      logger.info("Initializing Celery controller...")
      self.__clear_redis_database()
      self.__clear_queue()
      if not APP_STATUS.DOCKERIZED_RUN:
        self.__start_worker()

  def __clear_redis_database(self):
    try:
      r = redis.Redis(host='redis_server', port=6379, password=env_handler.get_instance().env("REDIS_PASSWORD"))
      r.flushall()
      logger.info("Redis database cleared.")
    except redis.RedisError as e:
      logger.error(f"Error clearing Redis database: {e}")

  def __clear_queue(self):
    try:
      queue_purged = celery.control.purge()
      logger.info(f"Queue cleared. {queue_purged} tasks removed.")
    except Exception as e:
      logger.error(f"Error clearing queue: {e}")

  def __start_worker(self, concurrency=1):
    subprocess.Popen([
      'celery', '-A', 'crawler.crawler_services.crawler_services.celery_manager', 'worker',
      '--loglevel=DEBUG',
      f'--concurrency={concurrency}',
      '--without-gossip',
      '--without-mingle',
      '--without-heartbeat',
      '--pool=gevent'
    ])
    logger.info("Started Celery worker with custom settings.")

  def __run_crawler(self, url, virtual_id):
    start_crawler.delay(url, virtual_id)

  def __run_unique_task(self, url):
    invoke_unique_crawler.delay(url)

  def invoke_trigger(self, p_commands, p_data=None):
    if p_commands == CELERY_COMMANDS.S_START_CRAWLER:
      self.__run_crawler(p_data[0], p_data[1])
    if p_commands == CELERY_COMMANDS.S_INVOKE_UNIQUE_CRAWLER:
      self.__run_unique_task(p_data)


# Define Celery tasks

@celery.task(name='celery_controller.start_crawler')
def start_crawler(url, virtual_id):
  genbot_instance(url, virtual_id)

@celery.task(name='celery_controller.invoke_unique_crawler', bind=True)
def invoke_unique_crawler(self, url):
  redis_client = redis.Redis(host='redis_server', port=6379, password=env_handler.get_instance().env("REDIS_PASSWORD"))

  lock_key = "celery_controller:invoke_unique_crawler_lock"

  lock = redis_client.lock(lock_key, timeout=600, blocking_timeout=5)
  lock_acquired = False

  try:
    if lock.acquire(blocking=False):
      lock_acquired = True
      genbot_unique_instance(url)
    else:
      raise self.retry(exc=Exception("Task already running, rejecting the call"), countdown=60, max_retries=3)

  except Exception as e:
    raise e

  finally:
    if lock_acquired and lock.locked():
      lock.release()


if __name__ == "__main__":
  manager = celery_controller.get_instance()
