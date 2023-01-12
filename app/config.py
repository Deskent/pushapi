import logging.config
import sys
from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    HOST_DFL: str
    PORT_DFL: int
    NAME_DFL: str
    TOKEN_DFL: str
    OWNCLOUD_HOST: str
    DEBUG: bool = False
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8989


BASE_DIR = Path(__file__).parent
env_file = BASE_DIR.parent / '.env'
settings = Settings(_env_file=env_file, _env_file_encoding='utf-8')

logs_dir_name = 'logs'
logs_dir_full_path = BASE_DIR / logs_dir_name
if not logs_dir_full_path.exists():
    logs_dir_full_path.mkdir(parents=True)
log_level = "DEBUG" if settings.DEBUG else "WARNING"

logger_conf = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "base": {
            "format": '[%(asctime)s] %(levelname)s [%(filename)s:%(name)s.%(funcName)s:%(lineno)d]: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "base",
            "stream": sys.stdout
        },
        'all': {
            "class": "logging.handlers.RotatingFileHandler",
            "backupCount": 2,
            "maxBytes": 5 * 1024 * 1024,
            "encoding": "utf-8",
            "delay": False,
            "level": log_level,
            "formatter": "base",
            "filename": str(logs_dir_full_path / 'all.log'),
            "mode": "a",
        },
        "errors": {
            "class": 'logging.FileHandler',
            "level": 'ERROR',
            "formatter": "base",
            "filename": f"{logs_dir_full_path}/errors.log",
            "mode": "a"
        }
    },
    "loggers": {
        "pushapi": {
            "level": log_level,
            "handlers": ['console', 'errors', 'all'],
            "filters": [],
            "propagate": 1,
        }
    }
}

logging.config.dictConfig(logger_conf)
logger = logging.getLogger('pushapi')
