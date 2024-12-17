from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Awesome API"
    admin_email: str
    password_hash_secret_word: str

    model_config = SettingsConfigDict(env_file=".env")