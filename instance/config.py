import os

class Config(object):
    """Parent configuration class."""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = os.getenv('SECRET')
    REMOTE_USERNAME = os.getenv('REMOTE_USERNAME')
    REMOTE_SERVER = os.getenv('REMOTE_SERVER')

class DevelopmentConfig(Config):
    """Configurations for Development."""
    DEBUG = True
    LOCAL_PATH = '/tmp/backups'
    REMOTE_PATH = '/tmp/backups'

class TestingConfig(Config):
    """Configurations for Development."""
    DEBUG = True
    TESTING = True
    LOCAL_PATH = '/tmp/backups'
    REMOTE_PATH = '/tmp/backups'

class ProductionConfig(Config):
    """Configurations for Production."""

    DEBUG = False
    TESTING = False
    LOCAL_PATH = os.getenv('BACKUP_LOCAL_PATH')
    REMOTE_PATH = os.getenv('BACKUP_REMOTE_PATH')

app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}