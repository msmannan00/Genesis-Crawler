import enum


class CELERY_CONNECTIONS:
  conn = 'redis://:killprg1@redis_server:6379/0'


class CELERY_COMMANDS(enum.Enum):
  S_START_TASK = 1


class ELASTIC_LOGGING:
  logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
      'default': {
        'format': '[%(asctime)s: %(levelname)s/%(name)s] %(message)s',
      },
    },
    'handlers': {
      'console': {
        'class': 'logging.StreamHandler',
        'formatter': 'default',
      },
    },
    'loggers': {
      '': {  # root logger
        'level': 'DEBUG',
        'handlers': ['console'],
      },
      'celery': {
        'level': 'WARNING',  # Suppress Celery's internal INFO and DEBUG logs
        'handlers': ['console'],
        'propagate': False,
      },
      'celery.worker.strategy': {
        'level': 'WARNING',  # Suppress Celery worker strategy logs
        'handlers': ['console'],
        'propagate': False,
      },
      'kombu': {
        'level': 'WARNING',  # Suppress Kombu logs (Celery's messaging library)
        'handlers': ['console'],
        'propagate': False,
      },
      'pymongo': {
        'level': 'WARNING',  # Suppress pymongo logs
        'handlers': ['console'],
        'propagate': False,
      },
      'urllib3': {
        'level': 'WARNING',  # Suppress urllib3 logs
        'handlers': ['console'],
        'propagate': False,
      }
    },
  }
