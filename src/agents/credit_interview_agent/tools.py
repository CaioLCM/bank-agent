from langchain.tools import tool

from langgraph.prebuilt import ToolRuntime

from src.storage import csv_handlers

from src.core.logger import get_logger, mask_cpf

from ..state_model import get_authenticated_cpf

from .score import EmploymentType, calculate_score

logger = get_logger(__name__)

INVALID_SESSION = "Sessão inválida ou expirada. É necessário autenticar o cliente novamente."

@tool
def update_score(
    monthly_income: float,
    employment_type: EmploymentType,
    fixed_expenses: float,
    num_dependents: int,
    has_debts: bool,
    runtime: ToolRuntime,
):
    """Recalcula o score de crédito do cliente com os dados da entrevista e grava
    o novo valor na base.

    Chame apenas depois de ter as cinco respostas do cliente.
    """
    cpf = get_authenticated_cpf(runtime)
    if cpf is None:
        logger.warning("atualizacao de score sem sessao valida")
        return INVALID_SESSION

    if monthly_income <= 0 and employment_type != "desempregado":
        logger.warning("update_score bloqueado: dados nao coletados | cpf=%s", mask_cpf(cpf))
        return (
            "Renda mensal ausente ou zerada para quem não está desempregado. "
            "Não invente valores: pergunte ao cliente a renda mensal, as despesas "
            "fixas, o número de dependentes e se há dívidas ativas antes de chamar "
            "esta ferramenta novamente."
        )

    try:
        new_score = calculate_score(
            monthly_income=monthly_income,
            employment_type=employment_type,
            fixed_expenses=fixed_expenses,
            num_dependents=num_dependents,
            has_debts=has_debts,
        )
    except ValueError as error:
        logger.warning("dados invalidos no calculo de score: %s", error)
        return f"Dados inválidos para o cálculo: {error} Confirme a informação com o cliente."

    try:
        client = csv_handlers.get_user_by_cpf(cpf)
        previous_score = None if client is None else int(client["score_credito"])
        csv_handlers.update_score(cpf, new_score)
    except ValueError:
        return "Cliente não encontrado na base. Informe que não foi possível localizar o cadastro."
    except OSError:
        logger.exception("falha ao gravar score em clientes.csv")
        return (
            "Não foi possível gravar o novo score agora. Informe ao cliente que "
            "o serviço está indisponível e ofereça tentar novamente."
        )

    logger.info(
        "score atualizado | cpf=%s anterior=%s novo=%d", mask_cpf(cpf), previous_score, new_score
    )

    allowed_limit = csv_handlers.get_max_allowed_limit(new_score)

    if previous_score is None:
        return f"Score atualizado para {new_score}. Teto de limite permitido: R$ {allowed_limit:.2f}."

    return (
        f"Score atualizado de {previous_score} para {new_score}. "
        f"Teto de limite permitido para o novo score: R$ {allowed_limit:.2f}."
    )
