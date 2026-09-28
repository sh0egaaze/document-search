from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    database_url: str
    elasticsearch_url: str = "http://localhost:9200"

    model_config = {"env_file": ".env"}


settings = Settings()