import os
from celery import Celery
from config import app_config


app = Celery()
app.config_from_object(app_config[os.getenv('FLASK_ENV')])
app.autodiscover_tasks(["tasks"])

if __name__ == "__main__":
    app.start()
