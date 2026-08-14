from pydantic_settings import SettingsConfigDict, BaseSettings

class Settings(BaseSettings):
    ALGORITHM: str
    DATABASE_URL: str
    SECRET_KEY: str
    SECRET_KEY_2FA: str
    SALT: str

    SMTP_HOST: str
    SMTP_PORT: str
    SMTP_PASSWORD: str
    SMTP_FROM: str

    model_config = SettingsConfigDict(
        env_file=".env"
    )

settings = Settings()