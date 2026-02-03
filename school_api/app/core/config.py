from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    access_token: int = 15
    refresh_token: int = 7

    class Config:
        env_file = ".env"

settings = Settings()