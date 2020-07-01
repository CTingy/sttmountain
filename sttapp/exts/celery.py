from celery import Celery


celery = Celery()


def init_celery(app):

    celery.config_from_object(app.config)
    # celery.autodiscover_tasks(["sttapp.tasks"])
    return celery
