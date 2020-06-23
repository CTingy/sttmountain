import os
from celery import Celery
from config import app_config


app = Celery(broker="redis://127.0.0.1:6379/1", backend="mongodb://127.0.0.1:27017/")


app.config_from_object(
    app_config[os.getenv('FLASK_ENV')]
)


if __name__ == "__main__":
    app.start()
