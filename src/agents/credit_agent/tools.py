from langchain.tools import tool

from langgraph.prebuilt import ToolRuntime

from src.storage import csv_handlers

from ..state_model import get_authenticated_cpf

SESSAO_INVALIDA = "Sessão inválida ou expirada. É necessário autenticar o cliente novamente."

@tool
def consult_credit_limit(runtime: ToolRuntime):
    """Consulta o limite de crédito disponível do cliente autenticado."""
    cpf = get_authenticated_cpf(runtime)
    if cpf is None:
        return SESSAO_INVALIDA

    try:
        limite = csv_handlers.consult_credit_limit(cpf)
    except OSError:
        return (
            "Não foi possível ler a base de clientes agora. Informe ao cliente que "
            "a consulta está indisponível e ofereça tentar novamente."
        )

    if limite is None:
        return "Cliente não encontrado na base. Informe que não foi possível localizar o cadastro."

    return f"Limite de crédito disponível: R$ {limite:.2f}."

@tool
def request_credit(amount: float, runtime: ToolRuntime):
    """Registra uma solicitação de aumento de limite e devolve o status do pedido.

    O pedido é gravado em solicitacoes_aumento_limite.csv e avaliado contra o
    score atual do cliente: 'aprovado' se o valor couber no teto do score,
    'rejeitado' caso contrário.
    """
    cpf = get_authenticated_cpf(runtime)
    if cpf is None:
        return SESSAO_INVALIDA

    if amount <= 0:
        return "O valor solicitado deve ser maior que zero. Peça o valor novamente ao cliente."

    try:
        pedido = csv_handlers.request_limit_increase(cpf, amount)
    except ValueError:
        return "Cliente não encontrado na base. Informe que não foi possível localizar o cadastro."
    except OSError:
        return (
            "Não foi possível registrar a solicitação agora. Informe ao cliente que "
            "o serviço está indisponível e ofereça tentar novamente."
        )

    if pedido["status_pedido"] == "aprovado":
        return (
            f"Solicitação aprovada. Limite anterior: R$ {pedido['limite_atual']:.2f}. "
            f"Novo limite em vigor: R$ {pedido['novo_limite_solicitado']:.2f}."
        )

    return (
        f"Solicitação rejeitada: o score atual do cliente não permite o limite de "
        f"R$ {pedido['novo_limite_solicitado']:.2f}. O limite segue em "
        f"R$ {pedido['limite_atual']:.2f}. Ofereça a entrevista financeira para "
        "tentar reajustar o score."
    )
