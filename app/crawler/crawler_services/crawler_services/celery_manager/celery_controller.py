import logging
import warnings
from celery import Celery
import subprocess
import sys
import os
import redis
from logging.config import dictConfig
from crawler.crawler_services.crawler_services.celery_manager.celery_enums import CELERY_CONNECTIONS, ELASTIC_LOGGING, \
  CELERY_COMMANDS

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
      r = redis.Redis(host='redis_server', port=6379, password='killprg1')
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

  def __run_task(self, url, virtual_id):
    simple_task.delay(url, virtual_id)

  def invoke_trigger(self, p_commands, p_data=None):
    if p_commands == CELERY_COMMANDS.S_START_TASK:
      self.__run_task(p_data[0], p_data[1])


# Define Celery tasks
@celery.task(name='celery_controller.simple_task')
def simple_task(url, virtual_id):
  genbot_instance(url, virtual_id)


if __name__ == "__main__":
  manager = celery_controller.get_instance()
