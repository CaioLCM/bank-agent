import pandas as pd

from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
CLIENTES_PATH = DATA_DIR / "clientes.csv"
SOLICITACOES_PATH = DATA_DIR / "solicitacoes_aumento_limite.csv"

SOLICITACOES_COLUNAS = [
    "cpf_cliente",
    "data_hora_solicitacao",
    "limite_atual",
    "novo_limite_solicitado",
    "status_pedido",
]

score_limite_df = pd.read_csv(DATA_DIR / "score_limite.csv")

def get_clientes():
    """Base de clientes lida do disco a cada chamada, já que limite e score mudam."""
    return pd.read_csv(CLIENTES_PATH, dtype={"cpf": str})

def get_user(CPF: str, birth: str):
    clientes_df = get_clientes()
    mask = (clientes_df["cpf"] == CPF) & (clientes_df["data_nascimento"] == birth)
    return clientes_df[mask]

def get_user_by_cpf(CPF: str):
    """Retorna a linha do cliente, ou None se o CPF não existir na base."""
    clientes_df = get_clientes()
    encontrado = clientes_df[clientes_df["cpf"] == CPF]
    return None if encontrado.empty else encontrado.iloc[0]

def consult_credit_limit(CPF: str) -> float | None:
    """Limite de crédito disponível do cliente."""
    cliente = get_user_by_cpf(CPF)
    return None if cliente is None else float(cliente["limite_credito"])

def get_limite_maximo_permitido(score: int) -> float:
    """Teto de limite que a tabela score_limite permite para esse score."""
    mask = (score_limite_df["score_minimo"] <= score) & (score <= score_limite_df["score_maximo"])
    faixa = score_limite_df[mask]
    return 0.0 if faixa.empty else float(faixa.iloc[0]["limite_maximo_permitido"])

def _atualizar_cliente(CPF: str, coluna: str, valor) -> None:
    """Grava um campo do cliente em clientes.csv."""
    clientes_df = get_clientes()
    if coluna not in clientes_df.columns:
        raise ValueError(f"Coluna inexistente em clientes.csv: {coluna}")

    mask = clientes_df["cpf"] == CPF
    if not mask.any():
        raise ValueError(f"CPF não encontrado na base de clientes: {CPF}")

    clientes_df.loc[mask, coluna] = valor
    clientes_df.to_csv(CLIENTES_PATH, index=False)

def update_credit_limit(CPF: str, novo_limite: float) -> float:
    """Atualiza o limite de crédito do cliente e devolve o valor gravado."""
    _atualizar_cliente(CPF, "limite_credito", float(novo_limite))
    return float(novo_limite)

def update_score(CPF: str, novo_score: int) -> int:
    """Atualiza o score de crédito do cliente e devolve o valor gravado."""
    _atualizar_cliente(CPF, "score_credito", int(novo_score))
    return int(novo_score)

def request_limit_increase(CPF: str, novo_limite: float) -> dict:
    """Registra o pedido de aumento em CSV, já avaliado contra o score do cliente.

    Devolve o pedido com status 'aprovado' ou 'rejeitado'. Quando aprovado,
    o novo limite passa a valer em clientes.csv.
    """
    cliente = get_user_by_cpf(CPF)
    if cliente is None:
        raise ValueError(f"CPF não encontrado na base de clientes: {CPF}")

    limite_atual = float(cliente["limite_credito"])
    permitido = get_limite_maximo_permitido(int(cliente["score_credito"]))

    pedido = {
        "cpf_cliente": CPF,
        "data_hora_solicitacao": datetime.now().isoformat(),
        "limite_atual": limite_atual,
        "novo_limite_solicitado": float(novo_limite),
        "status_pedido": "aprovado" if float(novo_limite) <= permitido else "rejeitado",
    }

    df = pd.concat([get_solicitacoes(), pd.DataFrame([pedido])], ignore_index=True)
    df.to_csv(SOLICITACOES_PATH, index=False, columns=SOLICITACOES_COLUNAS)

    if pedido["status_pedido"] == "aprovado":
        update_credit_limit(CPF, novo_limite)

    return pedido

def get_solicitacoes(CPF: str | None = None):
    """Solicitações registradas; filtradas por CPF quando informado."""
    if not SOLICITACOES_PATH.exists() or SOLICITACOES_PATH.stat().st_size == 0:
        return pd.DataFrame(columns=SOLICITACOES_COLUNAS)

    df = pd.read_csv(SOLICITACOES_PATH, dtype={"cpf_cliente": str})
    return df if CPF is None else df[df["cpf_cliente"] == CPF]
