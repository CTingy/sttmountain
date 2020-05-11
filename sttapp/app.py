import os

from flask import Flask

from .config import app_config
from .db import init_db
from .bp import register_bps


def create_app(config_name='development'):

    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    db = init_db(app)

    register_bps(app)

    return app


# app = create_app(config_name=os.getenv("FLASK_ENV"))
