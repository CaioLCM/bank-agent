from langchain.tools import tool

from langgraph.prebuilt import ToolRuntime

from langgraph.types import Command

from langchain.messages import ToolMessage

from src.storage.csv_handlers import get_user

from src.core.auth import create_token

MAX_AUTH_ATTEMPTS = 3

@tool
def verify_user(CPF: str, birth: str, runtime: ToolRuntime):
    """Autentica o cliente pelo CPF e data de nascimento na base de clientes."""
    if not get_user(CPF, birth).empty:
        return Command(
            update={
                "messages": [ToolMessage("Cliente autenticado", tool_call_id=runtime.tool_call_id)],
                "cpf": CPF,
                "auth": True,
                "auth_attempts": 0
            }
        )

    # runtime.state chega como dict dentro do create_agent e como BankState em
    # grafos montados à mão, então aceitamos as duas formas.
    state = runtime.state
    anteriores = state.get("auth_attempts", 0) if isinstance(state, dict) else state.auth_attempts

    attempts = anteriores + 1
    restantes = MAX_AUTH_ATTEMPTS - attempts

    if restantes > 0:
        conteudo = (
            f"Autenticação falhou: CPF ou data de nascimento não conferem. "
            f"Tentativa {attempts} de {MAX_AUTH_ATTEMPTS}. "
            f"Peça os dados novamente ao cliente ({restantes} tentativa(s) restante(s))."
        )
    else:
        conteudo = (
            f"Autenticação falhou pela {MAX_AUTH_ATTEMPTS}ª vez consecutiva. "
            "Informe ao cliente de maneira agradável que não foi possível autenticá-lo "
            "e encerre o atendimento com a ferramenta end_conversation."
        )

    return Command(
        update={
            "messages": [ToolMessage(conteudo, tool_call_id=runtime.tool_call_id)],
            "auth": False,
            "auth_attempts": attempts
        }
    )