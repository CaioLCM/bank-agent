from langchain.agents import create_agent

from src.core.model import get_model

from ..state_model import BankState

from .tools import (
    request_credit
)

def create_credit_agent():
    return create_agent(
        model=get_model(),
        state_schema=BankState,
        tools=[request_credit],
        system_prompt="""
            Você é um agente de crédito, responsável por:
            - entender a necessidade de crédito do cliente,
            - coletar o valor desejado,
            - registrar a solicitação de crédito
        """
    )

credit_agent = create_credit_agent()
