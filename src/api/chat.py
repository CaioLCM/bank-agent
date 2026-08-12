from fastapi import APIRouter

from pydantic import BaseModel

from langchain.messages import HumanMessage

import uuid

from src.agents.orchestrator import orchestrator

router = APIRouter(tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


class ChatResponse(BaseModel):
    message: str
    thread_id: str
    conversation_ended: bool = False


@router.post("/invoke", response_model=ChatResponse)
async def invoke(request: ChatRequest):
    """Execução síncrona: recebe a mensagem e devolve a resposta completa."""
    thread_id = request.thread_id or uuid.uuid4().hex
    resp = await orchestrator.ainvoke(
        {"messages": [HumanMessage(content=request.message)]},
        {"configurable": {"thread_id": thread_id}},
    )
    return ChatResponse(
        message=resp["messages"][-1].content,
        thread_id=thread_id,
        conversation_ended=bool(resp.get("conversation_ended")),
    )
