from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URI: str = 'mongodb://localhost:27017'
    GEMINI_API_KEY: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()