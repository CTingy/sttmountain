import os

from flask import Flask

from sttapp.config import app_config
from sttapp.db import init_db


def create_app(config_name='development'):

    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    db = init_db(app)

    return app


app = create_app(config_name=os.getenv("FLASK_ENV"))


@app.route('/')
def index():
    return 'hello world'


@app.route('/users/')
def users():
    from sttapp.users.models import User
    return "Hello " + str(User.objects.first().id)
