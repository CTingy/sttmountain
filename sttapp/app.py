import os

from flask import Flask

from .config import app_config
from .db import init_db
from .bp import register_bps
from .mail import init_mail
from .login import init_login
from flask_wtf.csrf import CSRFProtect


def create_app(config_name='development'):

    config = app_config[config_name]

    app = Flask(__name__,
                static_url_path='',
                static_folder=config.STATIC_DIR,
                template_folder='templates/'
                )
    app.config.from_object(config)
    db = init_db(app)
    mail = init_mail(app)
    login_manager = init_login(app)
    csrf = CSRFProtect(app)
    register_bps(app)

    return app
