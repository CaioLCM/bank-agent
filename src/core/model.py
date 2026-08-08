from langchain_openai import ChatOpenAI

from src.core.settings import settings


def get_model() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.model,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    )
