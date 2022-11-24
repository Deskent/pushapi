from pydantic import BaseSettings


class Settings(BaseSettings):
    HOST_DFL: str
    PORT_DFL:  int
    NAME_DFL: str
    TOKEN_DFL: str


settings = Settings(_env_file='../.env', _env_file_encoding='utf-8')