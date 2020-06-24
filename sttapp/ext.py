from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_mail import Mail


# database
db = MongoEngine()


# login manager
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "請先登入才可進行操作"
login_manager.login_message_category = "info"


# flask mail
mail = Mail()
