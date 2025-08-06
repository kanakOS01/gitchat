from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    MONGODB_URI: str = 'mongodb://localhost:27017'
    DB_NAME: str = 'gitchat'
    OPENAI_API_KEY: str



settings = Settings()