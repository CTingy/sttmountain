import os
from celery import Celery
from sttapp.config import app_config


celery = Celery()
celery.config_from_object(app_config[os.getenv('FLASK_ENV')])
celery.autodiscover_tasks(["sttapp.tasks"])


if __name__ == "__main__":
    celery.start()
