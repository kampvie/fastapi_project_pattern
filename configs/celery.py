import os
import urllib.parse

from celery import Celery
from configs.settings import CELERY_APP_NAME

RABBITMQ = os.environ.get('RABBITMQ')
# Initialize an app for celery task queue
# Where app is up-level package and tasks is the sub-package for store and calling task
app_celery = Celery(f'{CELERY_APP_NAME}',
                    broker=f'amqp://root:{urllib.parse.quote("rootrabbitmq2021")}@{RABBITMQ}:5672',
                    include=['app.tasks'])
# Optional configuration
app_celery.config_from_object('configs.celeryconfig')
