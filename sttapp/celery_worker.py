import os
from sttapp.app import create_app
from sttapp.exts.celery import celery


app = create_app(os.environ.get("FLASK_ENV"))
app.app_context().push()
