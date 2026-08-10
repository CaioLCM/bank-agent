from langchain.tools import tool

from langgraph.prebuilt import ToolRuntime

from langgraph.types import Command

from langchain.messages import ToolMessage

from src.storage.csv_handlers import get_user

from src.core.auth import create_token

@tool
def verify_user(CPF: str, birth: str, runtime: ToolRuntime):
    """Autentica o cliente pelo CPF e data de nascimento na base de clientes."""
    if not get_user(CPF, birth).empty:
        return Command(
            update={
                "messages": [ToolMessage("Cliente autenticado", tool_call_id=runtime.tool_call_id)],
                "CPF": CPF,
                "auth": True
            }
        )
