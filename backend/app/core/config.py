from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

env_file = os.getenv("ENV_FILE", ".env")
load_dotenv(env_file)


class Settings(BaseSettings):
    PROJECT_NAME: str = "Подари мне"
    VERSION: str = "1.0.0"

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    TELEGRAM_BOT_TOKEN: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    ENDPOINT_URL: str
    BUCKET_NAME: str
    URL_DATA_SAVE: str

    @property
    def DATABASE_URL_asyncpg(self):
        base_url = f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@"
        host_port = f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return base_url + host_port

    class Config:
        case_sensitive = True
        extra = "ignore"
        # env_file = ".env"


settings = Settings()
