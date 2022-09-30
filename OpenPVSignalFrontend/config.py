import os


class Config(object):
    DEBUG = False
    TESTING = False
    # DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = <BYTE_LITERAL_SECRET_KEY>

class ProductionConfig(Config):
    # DATABASE_URI = 'mysql://user@localhost/foo'
    pass

class DevelopmentConfig(Config):
    BACKEND_SERVER = <BACKEND_SERVER_IP>
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
