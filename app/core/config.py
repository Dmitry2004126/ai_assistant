from pathlib import Path
from typing import Self

from pydantic import BaseModel, PostgresDsn, ValidationInfo, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.enums import LogLevel

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class AppConfig(BaseModel):
    APP_TITLE: str = 'Ai Assistant'
    APP_VERSION: str = '1.0.0'
    API_VERSION_STR: str = '1.0.0'
    LOG_LEVEL: LogLevel = LogLevel.INFO


class DB(BaseModel):
    host: str = 'localhost'
    port: int = 5432
    username: str = 'username'
    password: str = 'password'
    name: str = 'name'
    url: str = ''

    ECHO: bool = False
    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 20
    POOL_TIMEOUT: int = 30
    POOL_RECYCLE: int = 1800
    POOL_PRE_PING: bool = True

    @model_validator(mode='after')
    def assemble_dsn(self, validation_info: ValidationInfo) -> Self:
        self.url = str(
            PostgresDsn.build(
                scheme='postgresql+asyncpg',
                username=self.username,
                password=self.password,
                host=self.host,
                port=int(self.port),
                path=self.name,
            )
        )
        return self


class JWT(BaseModel):
    SECRET: str
    ACCESS_TOKEN_LIFETIME_SECONDS: int = 600 * 60  # 1 hour
    REFRESH_TOKEN_LIFETIME_SECONDS: int = 60 * 60 * 24 * 7  # 7 days


class OpenRouter(BaseModel):
    key: str = None
    base_url: str = ''


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            BASE_DIR / '.env.template',
            BASE_DIR / '.env',
        ),
        case_sensitive=False,
        env_nested_delimiter='__',
        extra='allow',
    )

    app: AppConfig = AppConfig()
    db: DB = DB()
    jwt: JWT
    openrouter: OpenRouter = OpenRouter()


settings = Settings()
