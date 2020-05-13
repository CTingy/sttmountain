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

    APPLICATION_ROOT = os.path.dirname(os.path.abspath(__file__))
    # SERVER_NAME = '127.0.0.1:5000'


class TestingConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


app_config = {
    'testing': TestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
