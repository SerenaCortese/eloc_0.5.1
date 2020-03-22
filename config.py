import os

basedir = os.path.abspath(os.path.dirname(__file__))
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    UPLOADS_DEFAULT_DEST = os.path.join(os.path.abspath(os.path.dirname(__file__)) + 'pictures')

    @staticmethod
    def init_app(app):#todo - fill the func with the proper code
        pass

class DevelopmentConfig(Config):

    DEBUG = True
    USE_RELOADER = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #todo configure the email settings eventually

    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'sqlite_eloc.db')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'sqlite_eloc.db')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
'development': DevelopmentConfig,
'testing': TestingConfig,
'production': ProductionConfig,
'default': DevelopmentConfig
}