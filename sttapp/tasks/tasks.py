from .celery import capp


@capp.task()
def add(a, b):
    return a + b
