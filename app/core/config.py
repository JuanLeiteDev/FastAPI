from pydantic_settings import SettingsConfigDict, BaseSettings

class Settings(BaseSettings):
    ALGORITHM: str
    DATABASE_URL: str
    SECRET_KEY: str
    SECRET_KEY_2FA: str
    SALT: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    TEMPORARY_TOKEN_EXPIRE_MINUTES: int

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_PASSWORD: str
    SMTP_FROM: str

    model_config = SettingsConfigDict(
        env_file=".env"
    )

settings = Settings()