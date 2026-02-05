import os
import logging
from logging.handlers import RotatingFileHandler

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Logging configuration
    LOG_LEVEL = logging.INFO
    LOG_FILE = 'timesheet_api.log'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5

def setup_logging(app):
    if not app.debug:
        file_handler = RotatingFileHandler(
            Config.LOG_FILE, 
            maxBytes=Config.LOG_MAX_BYTES, 
            backupCount=Config.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(Config.LOG_LEVEL)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(Config.LOG_LEVEL)
        app.logger.info('Timesheet API startup')