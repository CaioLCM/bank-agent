import pandas as pd

from datetime import datetime
from pathlib import Path

from src.core.logger import get_logger, mask_cpf

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
CLIENTS_PATH = DATA_DIR / "clientes.csv"
SCORE_LIMIT_PATH = DATA_DIR / "score_limite.csv"
REQUESTS_PATH = DATA_DIR / "solicitacoes_aumento_limite.csv"

logger = get_logger(__name__)

REQUEST_COLUMNS = [
    "cpf_cliente",
    "data_hora_solicitacao",
    "limite_atual",
    "novo_limite_solicitado",
    "status_pedido",
]

score_limit_df = pd.read_csv(SCORE_LIMIT_PATH)

def get_clients():
    """Base de clientes lida do disco a cada chamada, já que limite e score mudam."""
    return pd.read_csv(CLIENTS_PATH, dtype={"cpf": str})

def get_user(CPF: str, birth: str):
    clients_df = get_clients()
    mask = (clients_df["cpf"] == CPF) & (clients_df["data_nascimento"] == birth)
    return clients_df[mask]

def get_user_by_cpf(CPF: str):
    """Retorna a linha do cliente, ou None se o CPF não existir na base."""
    clients_df = get_clients()
    found = clients_df[clients_df["cpf"] == CPF]
    return None if found.empty else found.iloc[0]

def consult_credit_limit(CPF: str) -> float | None:
    """Limite de crédito disponível do cliente."""
    client = get_user_by_cpf(CPF)
    return None if client is None else float(client["limite_credito"])

def get_max_allowed_limit(score: int) -> float:
    """Teto de limite que a tabela score_limite permite para esse score."""
    mask = (score_limit_df["score_minimo"] <= score) & (score <= score_limit_df["score_maximo"])
    band = score_limit_df[mask]
    return 0.0 if band.empty else float(band.iloc[0]["limite_maximo_permitido"])

def _update_client(CPF: str, column: str, value) -> None:
    """Grava um campo do cliente em clientes.csv."""
    clients_df = get_clients()
    if column not in clients_df.columns:
        raise ValueError(f"Coluna inexistente em clientes.csv: {column}")

    mask = clients_df["cpf"] == CPF
    if not mask.any():
        raise ValueError(f"CPF não encontrado na base de clientes: {CPF}")

    clients_df.loc[mask, column] = value
    clients_df.to_csv(CLIENTS_PATH, index=False)
    logger.info("clientes.csv atualizado | cpf=%s coluna=%s valor=%s", mask_cpf(CPF), column, value)

def update_credit_limit(CPF: str, new_limit: float) -> float:
    """Atualiza o limite de crédito do cliente e devolve o valor gravado."""
    _update_client(CPF, "limite_credito", float(new_limit))
    return float(new_limit)

def update_score(CPF: str, new_score: int) -> int:
    """Atualiza o score de crédito do cliente e devolve o valor gravado."""
    _update_client(CPF, "score_credito", int(new_score))
    return int(new_score)

def request_limit_increase(CPF: str, new_limit: float) -> dict:
    """Registra o pedido de aumento em CSV, já avaliado contra o score do cliente.

    Devolve o pedido com status 'aprovado' ou 'rejeitado'. Quando aprovado,
    o novo limite passa a valer em clientes.csv.
    """
    client = get_user_by_cpf(CPF)
    if client is None:
        raise ValueError(f"CPF não encontrado na base de clientes: {CPF}")

    current_limit = float(client["limite_credito"])
    allowed_limit = get_max_allowed_limit(int(client["score_credito"]))

    credit_request = {
        "cpf_cliente": CPF,
        "data_hora_solicitacao": datetime.now().isoformat(),
        "limite_atual": current_limit,
        "novo_limite_solicitado": float(new_limit),
        "status_pedido": "aprovado" if float(new_limit) <= allowed_limit else "rejeitado",
    }

    df = pd.concat([get_requests(), pd.DataFrame([credit_request])], ignore_index=True)
    df.to_csv(REQUESTS_PATH, index=False, columns=REQUEST_COLUMNS)
    logger.info(
        "solicitacao registrada | cpf=%s solicitado=%.2f status=%s",
        mask_cpf(CPF), credit_request["novo_limite_solicitado"], credit_request["status_pedido"],
    )

    if credit_request["status_pedido"] == "aprovado":
        update_credit_limit(CPF, new_limit)

    return credit_request

def get_requests(CPF: str | None = None):
    """Solicitações registradas; filtradas por CPF quando informado."""
    if not REQUESTS_PATH.exists() or REQUESTS_PATH.stat().st_size == 0:
        return pd.DataFrame(columns=REQUEST_COLUMNS)

    df = pd.read_csv(REQUESTS_PATH, dtype={"cpf_cliente": str})
    return df if CPF is None else df[df["cpf_cliente"] == CPF]
