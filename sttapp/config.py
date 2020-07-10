import os


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
    CELERY_RESULT_BACKEND = "redis://{}:6379".format(os.environ.get("REDIS_HOST", None)) 
    BROKER_URL = "redis://{}:6379".format(os.environ.get("REDIS_HOST", None))

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

    # STATIC_STORAGE_URL = "https://storage.googleapis.com/sttmountainstatic/"


class ProductionConfig(Config):
    DEBUG = False
    STATIC_STORAGE_URL = "https://storage.googleapis.com/sttmountainstatic/"


app_config = {
    'testing': TestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
