from langchain.agents import create_agent

from src.core.model import get_model

from ..state_model import BankState

from .tools import (
    request_credit
)

from ..handoff_tools import (
    handoff_to_credit_interview_agent,
    handoff_to_triage_agent
)

def create_credit_agent():
    return create_agent(
        model=get_model(),
        state_schema=BankState,
        tools=[request_credit, handoff_to_credit_interview_agent, handoff_to_triage_agent],
        system_prompt="""
            Você é um agente de crédito, responsável por:
            - entender a necessidade de crédito do cliente,
            - coletar o valor desejado,
            - registrar a solicitação de crédito
        """
    )

credit_agent = create_credit_agent()
