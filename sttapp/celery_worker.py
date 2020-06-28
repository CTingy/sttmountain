from sttapp.app import create_app
from sttapp.app import celery
from .config import app_config


app = create_app()
app.app_context().push()
