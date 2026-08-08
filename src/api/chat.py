from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from pydantic import BaseModel

from langchain.messages import HumanMessage

import json
import uuid

from src.agents.triage_agent.agent import triage_agent

router = APIRouter(tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


class ChatResponse(BaseModel):
    message: str
    thread_id: str


@router.post("/invoke", response_model=ChatResponse)
async def invoke(request: ChatRequest):
    """Execução síncrona: recebe a mensagem e devolve a resposta completa."""
    thread_id = request.thread_id or uuid.uuid4().hex
    resp = await triage_agent.ainvoke(
        {"messages": [HumanMessage(content=request.message)]},
        {"configurable": {"thread_id": thread_id}},
    )
    return ChatResponse(message=resp["messages"][-1].content, thread_id=thread_id)

@router.post("/chat")
async def chat(request: ChatRequest):
    """Execução em streaming: devolve a resposta em chunks."""
    thread_id = request.thread_id or uuid.uuid4().hex

    def event(payload: dict) -> str:
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    async def gen():
        yield event({"type": "start", "thread_id": thread_id})
        async for chunk, _metadata in triage_agent.astream(
            {"messages": [HumanMessage(content=request.message)]},
            {"configurable": {"thread_id": thread_id}},
            stream_mode="messages",
        ):
            if chunk.content:
                yield event({"type": "token", "content": chunk.content})
        yield event({"type": "end"})

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no"},
    )