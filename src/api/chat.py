from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


class ChatResponse(BaseModel):
    message: str
    thread_id: str


@router.post("/invoke", response_model=ChatResponse)
async def invoke(request: ChatRequest) -> ChatResponse:
    """Execução síncrona: recebe a mensagem e devolve a resposta completa."""
    raise NotImplementedError


@router.post("/chat")
async def chat(request: ChatRequest):
    """Execução em streaming: devolve a resposta em chunks."""
    raise NotImplementedError
