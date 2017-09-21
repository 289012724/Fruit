import os

base_dir = os.path.abspath(os.path.dirname(__name__))


# config base
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    FLASKY_ADMIN = os.environ.get('FLASKY_AMIND')
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    PORT = 9012
    DATABASE = "fruits"
    SQLALCHEMY_DATABASE_URI = "mysql://root:123456@127.0.0.1:3306/fruit?charset=utf8"


class TestConfig(Config):
    TESTING = True
    PORT = 9012
    DATABASE = "fruits"
    SQLALCHEMY_DATABASE_URI = "mysql://root:123456@127.0.0.1:/fruit?charset=utf8"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    PORT = 9012
    DATABASE = "fruits"
    SQLALCHEMY_DATABASE_URI = "mysql://root:123456@127.0.0.1:3306/fruit?charset=utf8"


config = {
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
