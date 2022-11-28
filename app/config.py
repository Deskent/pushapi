from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    HOST_DFL: str
    PORT_DFL:  int
    NAME_DFL: str
    TOKEN_DFL: str
    TELEGRAM_ID: str = ''
    TELEBOT_TOKEN: str = ''


BASE_DIR = Path(__file__).parent
env_file = BASE_DIR.parent / '.env'
settings = Settings(_env_file=env_file, _env_file_encoding='utf-8')