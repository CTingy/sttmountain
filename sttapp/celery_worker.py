from sttapp.app import create_app
from sttapp.exts.celery import celery


app = create_app()
app.app_context().push()
