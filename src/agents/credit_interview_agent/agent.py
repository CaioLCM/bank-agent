from langchain.agents import create_agent

from src.core.model import get_model

from ..state_model import BankState

from .tools import (
    update_score,
    transfer_to_credit_agent
)

def create_credit_interview_agent():
    return create_agent(
        model=get_model(),
        state_schema=BankState,
        tools=[update_score, transfer_to_credit_agent],
        system_prompt="""
            Você é um agente de entrevista de crédito, responsável por:
            - conduzir a entrevista com o cliente para levantar informações financeiras,
            - atualizar o score de crédito a partir do que foi coletado,
            - redirecionar o cliente para o agente de crédito ao final da entrevista
        """
    )

credit_interview_agent = create_credit_interview_agent()
