from langchain.tools import tool

from langgraph.prebuilt import ToolRuntime

from src.storage import csv_handlers

from src.core.logger import get_logger, mask_cpf

from ..state_model import get_authenticated_cpf

logger = get_logger(__name__)

INVALID_SESSION = "Sessão inválida ou expirada. É necessário autenticar o cliente novamente."

@tool
def consult_credit_limit(runtime: ToolRuntime):
    """Consulta o limite de crédito disponível do cliente autenticado."""
    cpf = get_authenticated_cpf(runtime)
    if cpf is None:
        logger.warning("consulta de limite sem sessao valida")
        return INVALID_SESSION

    try:
        limit = csv_handlers.consult_credit_limit(cpf)
    except OSError:
        logger.exception("falha ao ler clientes.csv")
        return (
            "Não foi possível ler a base de clientes agora. Informe ao cliente que "
            "a consulta está indisponível e ofereça tentar novamente."
        )

    if limit is None:
        return "Cliente não encontrado na base. Informe que não foi possível localizar o cadastro."

    logger.info("consulta de limite | cpf=%s limite=%.2f", mask_cpf(cpf), limit)
    return f"Limite de crédito disponível: R$ {limit:.2f}."

@tool
def request_credit(amount: float, runtime: ToolRuntime):
    """Registra uma solicitação de aumento de limite e devolve o status do pedido.

    O pedido é gravado em solicitacoes_aumento_limite.csv e avaliado contra o
    score atual do cliente: 'aprovado' se o valor couber no teto do score,
    'rejeitado' caso contrário.
    """
    cpf = get_authenticated_cpf(runtime)
    if cpf is None:
        logger.warning("pedido de aumento sem sessao valida")
        return INVALID_SESSION

    if amount <= 0:
        return "O valor solicitado deve ser maior que zero. Peça o valor novamente ao cliente."

    try:
        credit_request = csv_handlers.request_limit_increase(cpf, amount)
    except ValueError:
        logger.warning("pedido de aumento para cpf inexistente | cpf=%s", mask_cpf(cpf))
        return "Cliente não encontrado na base. Informe que não foi possível localizar o cadastro."
    except OSError:
        logger.exception("falha ao gravar solicitacao de aumento")
        return (
            "Não foi possível registrar a solicitação agora. Informe ao cliente que "
            "o serviço está indisponível e ofereça tentar novamente."
        )

    logger.info(
        "pedido de aumento | cpf=%s atual=%.2f solicitado=%.2f status=%s",
        mask_cpf(cpf), credit_request["limite_atual"], credit_request["novo_limite_solicitado"], credit_request["status_pedido"],
    )

    if credit_request["status_pedido"] == "aprovado":
        return (
            f"Solicitação aprovada. Limite anterior: R$ {credit_request['limite_atual']:.2f}. "
            f"Novo limite em vigor: R$ {credit_request['novo_limite_solicitado']:.2f}."
        )

    return (
        f"Solicitação rejeitada: o score atual do cliente não permite o limite de "
        f"R$ {credit_request['novo_limite_solicitado']:.2f}. O limite segue em "
        f"R$ {credit_request['limite_atual']:.2f}. Ofereça a entrevista financeira para "
        "tentar reajustar o score."
    )
