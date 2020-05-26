import os
import datetime


class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY', 'flask123')

    # mongodb config
    MONGODB_SETTINGS =  {
        'db': os.getenv("DB_NAME"),
        'host': '127.0.0.1',
        'port': 27017,
        'username': os.getenv("DB_USERNAME"),
        'password': os.getenv("DB_PASSWORD")
    }

    MAIL_DEFAULT_SENDER = 'sttmountain@mail.ncku.edu.tw'
    SESSION_PROTECTION = 'strong'

    # APPLICATION_ROOT = os.path.dirname(os.path.abspath(__file__))
    # SERVER_NAME = '127.0.0.1:5000'

    # crediential form Google
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
    GOOGLE_DISCOVERY_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )


class TestingConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.mailtrap.io'
    MAIL_PORT = 2525
    MAIL_USERNAME = os.environ.get('DEV_MAIL_USERNAME', None)
    MAIL_PASSWORD = os.environ.get('DEV_MAIL_PASSWORD', None)
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False


class ProductionConfig(Config):
    DEBUG = False


app_config = {
    'testing': TestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
