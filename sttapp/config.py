import os
import datetime


class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY')

    # mongodb config
    MONGODB_SETTINGS = {
        'db': os.getenv("DB_NAME"),
        'host': os.getenv("DB_HOST"),
        'port': int(os.getenv("DB_PORT")),
        'username': os.getenv("DB_USERNAME"),
        'password': os.getenv("DB_PASSWORD"),
        'connect': False,
    }

    # celery config
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", None)
    BROKER_URL = os.environ.get("CELERY_BROKER_URL", None)  # CELERY_BROKER_URL

    MAIL_DEFAULT_SENDER = os.environ.get("GOOGLE_CLIENT_ID", None)
    SESSION_PROTECTION = 'strong'

    # crediential form Google
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
    GOOGLE_DISCOVERY_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )

    STATIC_DIR = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))) + '/static'


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
    STATIC_DIR = ""


app_config = {
    'testing': TestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
