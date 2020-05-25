from flask_login import LoginManager
from .base.enums import FlashCategory


login_manager = LoginManager()


def init_login(app):
    
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "請先登入才可使用邀請註冊功能"
    login_manager.login_message_category = FlashCategory.info
    return login_manager
