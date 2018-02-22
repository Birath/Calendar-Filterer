import os
from celery.schedules import crontab
basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app/app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = 'redis://localhost:6379/0'


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    TEMPLATES_AUTO_RELOAD = True


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True

