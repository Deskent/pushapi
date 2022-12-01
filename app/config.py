from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8989
    HOST_DFL: str
    PORT_DFL:  int
    NAME_DFL: str
    TOKEN_DFL: str
    TELEGRAM_ID: str = ''
    TELEBOT_TOKEN: str = ''
    DEBUG: bool = False


BASE_DIR = Path(__file__).parent
env_file = BASE_DIR.parent / '.env'
settings = Settings(_env_file=env_file, _env_file_encoding='utf-8')