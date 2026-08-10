
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    model: str
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Autenticação
    jwt_secret: str = "dev-secret-apenas-para-desenvolvimento-trocar-em-producao"
    jwt_algorithm: str = "HS256"
    jwt_ttl_minutes: int = 30


def get_settings() -> Settings:
    return Settings()

settings = get_settings()
