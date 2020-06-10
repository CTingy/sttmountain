from .users import bp as user_bp
from .base import bp as home_bp
from .base import err_handler
from .proposals import bp as proposal_bp
from .auth import bp as auth_bp
from .members import bp as member_bp
from .events import bp as event_bp


def register_bps(app):

    app.register_blueprint(user_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(proposal_bp, url_prefix="/proposal")
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(member_bp, url_prefix='/member')
    app.register_blueprint(event_bp, url_prefix='/event')
    app.register_blueprint(err_handler)
