from sttapp.app import create_app
from sttapp.app import celery


app = create_app()
app.app_context().push()
