import os

from flask import Flask
from werkzeug.utils import import_string
from .config import app_config
from flask_wtf.csrf import CSRFProtect


blueprints = [
    ('sttapp.users:bp', '/user'),
    ('sttapp.base:bp', ''),
    ('sttapp.base:err_handler', ''),
    ('sttapp.proposals:bp', '/proposal'),
    ('sttapp.auth:bp', '/auth'),
    ('sttapp.members:bp', '/member'),
    ('sttapp.events:bp', '/event'),
]


extensions = [
    'sttapp.db:init_db',
    'sttapp.mail:init_mail',
    'sttapp.login:init_login',
]


def create_app(config_name='development'):

    config = app_config[config_name]
    app = Flask(
        __name__,
        static_url_path='',
        static_folder=config.STATIC_DIR,
        template_folder='templates/'
    )
    app.config.from_object(config)

    for ext_name in extensions:
        init_ext = import_string(ext_name)
        ext = init_ext(app)

    csrf = CSRFProtect(app)
    
    # register_bps
    for bp_name, prefix in blueprints:
        bp = import_string(bp_name, silent=False)
        app.register_blueprint(bp, url_prefix=prefix)
        
    return app


app = create_app()
