from langchain.agents import create_agent

from src.core.model import get_model

from ..state_model import BankState

from .tools import (
    get_dollar_rate
)

from ..handoff_tools import (
    end_conversation,
    handoff_to_triage_agent
)

def create_exchange_agent():
    return create_agent(
        model=get_model(),
        state_schema=BankState,
        tools=[get_dollar_rate, handoff_to_triage_agent, end_conversation],
        system_prompt="""
            Você é um agente de câmbio, responsável por:
            - atender dúvidas do cliente sobre câmbio,
            - buscar a cotação atual do dólar,
            - informar a cotação de forma clara ao cliente
        """
    )

exchange_agent = create_exchange_agent()
