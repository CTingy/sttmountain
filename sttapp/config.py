import os


class Config:

    # JWT_EXPIRATION_DELTA = timedelta(seconds=300)
    # JWT_AUTH_URL_RULE = '/auth/login'
    # JWT_AUTH_HEADER_PREFIX = os.environ.get('JWT_AUTH_HEADER_PREFIX', 'FLASK')
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

    # APPLICATION_ROOT = os.path.dirname(os.path.abspath(__file__))
    # SERVER_NAME = '127.0.0.1:5000'


class TestingConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER ='smtp.mailtrap.io'
    MAIL_PORT = 2525
    MAIL_USERNAME = '92e17ad0041d38'
    MAIL_PASSWORD = '1032dff33158b0'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False


class ProductionConfig(Config):
    DEBUG = False


app_config = {
    'testing': TestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
