from .users import bp as user_bp
from .base import bp as home_bp


def register_bps(app):

    app.register_blueprint(user_bp)
    app.register_blueprint(home_bp)
