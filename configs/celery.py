import os

from celery import Celery
from configs.settings import (
    CELERY_APP_NAME, RABBITMQ_DEFAULT_USER, RABBITMQ_DEFAULT_PASS)

RABBITMQ = os.environ.get('RABBITMQ')
# Initialize an app for celery task queue
# Where app is up-level package and tasks is the sub-package for store and calling task
app_celery = Celery(f'{CELERY_APP_NAME}',
                    broker=f'amqp://{RABBITMQ_DEFAULT_USER}:{RABBITMQ_DEFAULT_PASS}@{RABBITMQ}:5672',
                    include=['app.tasks.celery'])
# Optional configuration
app_celery.config_from_object('configs.celeryconfig')
