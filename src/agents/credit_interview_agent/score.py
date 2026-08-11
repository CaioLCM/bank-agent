"""Fórmula ponderada de score de crédito, conforme o enunciado do desafio."""

from typing import Literal

EmploymentType = Literal["formal", "autonomo", "desempregado"]

MIN_SCORE = 0
MAX_SCORE = 1000

INCOME_WEIGHT = 30

EMPLOYMENT_WEIGHT = {
    "formal": 300,
    "autonomo": 200,
    "desempregado": 0,
}

DEPENDENTS_WEIGHT = {
    0: 100,
    1: 80,
    2: 60,
    "3+": 30,
}

DEBT_WEIGHT = {
    True: -100,
    False: 100,
}

def calculate_score(
    monthly_income: float,
    employment_type: EmploymentType,
    fixed_expenses: float,
    num_dependents: int,
    has_debts: bool,
) -> int:
    """Novo score de crédito a partir dos dados da entrevista, limitado a 0-1000.

    Levanta ValueError se algum valor numérico for negativo.
    """

    if monthly_income < 0 or fixed_expenses < 0 or num_dependents < 0:
        raise ValueError("Renda, despesas e número de dependentes não podem ser negativos.")

    dependents_key = num_dependents if num_dependents <= 2 else "3+"

    score = (
        (monthly_income / (fixed_expenses + 1)) * INCOME_WEIGHT
        + EMPLOYMENT_WEIGHT[employment_type]
        + DEPENDENTS_WEIGHT[dependents_key]
        + DEBT_WEIGHT[bool(has_debts)]
    )

    return int(max(MIN_SCORE, min(MAX_SCORE, score)))
