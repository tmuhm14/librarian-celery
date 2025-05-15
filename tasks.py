import os
from celery import Celery
from celery.utils.log import get_task_logger

app = Celery('tasks', broker=os.getenv("CELERY_BROKER_URL"))
logger = get_task_logger(__name__)


@app.task
def add(x, y):
    logger.info(f'Adding {x} + {y}')
    return x + y


@app.task
def sync_to_phoneburner(pd_ref):
    logger.info(f'Syncing to Phoneburner {pd_ref}')
    sync_to_phoneburner(pd_ref)
    return "Synced to Phoneburner"
