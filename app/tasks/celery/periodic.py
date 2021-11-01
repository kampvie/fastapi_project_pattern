from configs.celery import app_celery
from app.utils.logger import get_stream_logger

logger = get_stream_logger(__name__)

@app_celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        30,
        example.s(),
        name='Hello every 30 seconds'
    )

@app_celery.task
def example():
    logger.info("Example periodic task -- Hello")