import os


class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY')
    SESSION_PROTECTION = 'strong'
    STATIC_DIR = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))) + '/static'

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
    CELERY_RESULT_BACKEND = "redis://{}:{}".format(
        os.environ.get("REDIS_HOST", None), os.environ.get("REDIS_PORT"), None) 
    BROKER_URL = "redis://{}:{}".format(
        os.environ.get("REDIS_HOST", None), os.environ.get("REDIS_PORT"), None)

    # crediential from Google
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
    GOOGLE_DISCOVERY_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )
    # google drive api
    GOOGLE_DRIVE_FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER_ID", None)
    GOOGLE_DRIVE_API_CERD_PATH = os.environ.get("GOOGLE_DRIVE_API_CERD_PATH", None)


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
    MAIL_DEFAULT_SENDER = os.environ.get("ADMIN_EMAIL", None)


class ProductionConfig(Config):
    DEBUG = False
    STATIC_STORAGE_URL = "https://storage.googleapis.com/sttmountainstatic/"
    
    # sendgrid smtp server
    # ref: https://www.twilio.com/blog/using-twilio-sendgrid-to-send-emails-from-python-flask-applications
    MAIL_SERVER = 'smtp.sendgrid.net'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'apikey'
    MAIL_PASSWORD = os.environ.get("SENDGRID_API_KEY", None)
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", None)


app_config = {
    'testing': TestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
