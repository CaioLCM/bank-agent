from langchain.tools import tool

from langgraph.prebuilt import ToolRuntime

from langgraph.types import Command

from langchain.messages import ToolMessage

from src.storage.csv_handlers import get_user

from src.core.auth import create_token

from src.core.logger import get_logger, mask_cpf

from ..state_model import state_as_dict

logger = get_logger(__name__)

MAX_AUTH_ATTEMPTS = 3

@tool
def verify_user(CPF: str, birth: str, runtime: ToolRuntime):
    """Autentica o cliente pelo CPF e data de nascimento na base de clientes."""
    if not get_user(CPF, birth).empty:
        logger.info("autenticacao bem-sucedida | cpf=%s", mask_cpf(CPF))
        return Command(
            update={
                "messages": [ToolMessage("Cliente autenticado", tool_call_id=runtime.tool_call_id)],
                "auth_token": create_token(CPF),
                "auth_attempts": 0
            }
        )

    attempts = state_as_dict(runtime).get("auth_attempts", 0) + 1
    remaining = MAX_AUTH_ATTEMPTS - attempts
    logger.warning(
        "autenticacao falhou | cpf=%s tentativa=%d/%d", mask_cpf(CPF), attempts, MAX_AUTH_ATTEMPTS
    )

    if remaining > 0:
        content = (
            f"Autenticação falhou: CPF ou data de nascimento não conferem. "
            f"Tentativa {attempts} de {MAX_AUTH_ATTEMPTS}. "
            f"Peça os dados novamente ao cliente ({remaining} tentativa(s) restante(s))."
        )
    else:
        content = (
            f"Autenticação falhou pela {MAX_AUTH_ATTEMPTS}ª vez consecutiva. "
            "Informe ao cliente de maneira agradável que não foi possível autenticá-lo "
            "e encerre o atendimento com a ferramenta end_conversation."
        )

    return Command(
        update={
            "messages": [ToolMessage(content, tool_call_id=runtime.tool_call_id)],
            "auth_token": None,
            "auth_attempts": attempts
        }
    )