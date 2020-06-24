import os

from flask import Flask

from .config import app_config
from .db import init_db
from .mail import init_mail
from .login import init_login
from flask_wtf.csrf import CSRFProtect


from flask import Flask
from werkzeug.utils import import_string


blueprints = [
    ('sttapp.users:bp', '/user'),
    ('sttapp.base:bp', ''),
    ('sttapp.base:err_handler', ''),
    ('sttapp.proposals:bp', '/proposal'),
    ('sttapp.auth:bp', '/auth'),
    ('sttapp.members:bp', '/member'),
    ('sttapp.events:bp', '/event'),
]


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
    
    # register_bps
    for bp_name, prefix in blueprints:
        bp = import_string(bp_name, silent=False)
        if prefix:
            app.register_blueprint(bp, url_prefix=prefix)
        else:
            app.register_blueprint(bp, url_prefix=prefix)

    return app

app = create_app()
