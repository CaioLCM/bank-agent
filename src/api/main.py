from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api import chat

from src.core.logger import get_logger

from src.storage.csv_handlers import CLIENTS_PATH, REQUESTS_PATH, SCORE_LIMIT_PATH

logger = get_logger(__name__)

REQUIRED_CSVS = (CLIENTS_PATH, SCORE_LIMIT_PATH, REQUESTS_PATH)

def check_csvs() -> None:
    """Falha se um CSV obrigatório estiver ausente ou vazio."""
    missing = [
        path.name
        for path in REQUIRED_CSVS
        if not path.exists() or path.stat().st_size == 0
    ]
    if missing:
        raise RuntimeError(
            f"CSVs obrigatórios ausentes ou vazios em {CLIENTS_PATH.parent}: {', '.join(missing)}"
        )

    for path in REQUIRED_CSVS:
        logger.info("csv ok | %s", path.name)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("iniciando a API")
    check_csvs()
    logger.info("API pronta")

    yield

    logger.info("encerrando a API")

app = FastAPI(
    title="arq-agnt",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(chat.router)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
