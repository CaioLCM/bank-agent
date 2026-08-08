from fastapi import FastAPI

from src.api import chat

app = FastAPI(
    title="arq-agnt",
    version="0.1.0",
)

app.include_router(chat.router)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
