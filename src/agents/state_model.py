from typing import Annotated

from langchain_core.messages import BaseMessage

from langgraph.graph.message import add_messages

from pydantic import BaseModel

from src.core.auth import verify_token

class BankState(BaseModel):
    current_agent: str = "triage_agent"
    conversation_ended: bool = False
    messages: Annotated[list[BaseMessage], add_messages] = []
    auth_token: str | None = None
    auth_attempts: int = 0

def state_as_dict(runtime) -> dict:
    """O estado chega como dict dentro do create_agent e como BankState em grafos
    montados à mão. Normaliza para dict."""
    state = runtime.state
    return state if isinstance(state, dict) else state.model_dump()

def get_authenticated_cpf(runtime) -> str | None:
    """CPF do cliente extraído do token de sessão, ou None se não houver token
    válido. É a única forma de saber de quem é o atendimento: o CPF vem assinado
    dentro do token, não de um campo solto no estado."""
    return verify_token(state_as_dict(runtime).get("auth_token"))
