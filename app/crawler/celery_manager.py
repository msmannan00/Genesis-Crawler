from celery import Celery
from celery.signals import after_setup_task_logger
import celery.signals

CELERY_BROKER_URL = "redis://{}:{}@{}:{}".format('', 'killprg1', 'redis_server', 6379)
CELERY_RESULT_BACKEND = "redis://{}:{}@{}:{}".format('', 'killprg1', 'redis_server', 6379)

celery_genbot = Celery(
    "celery_genbot",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND)


@celery.signals.setup_logging.connect
def on_celery_setup_logging(**kwargs):
    pass
