from langchain.agents import create_agent

from src.core.model import get_model

from .tools import (
    get_dollar_rate
)

def create_exchange_agent():
    return create_agent(
        model=get_model(),
        tools=[get_dollar_rate],
        system_prompt="""
            Você é um agente de câmbio, responsável por:
            - atender dúvidas do cliente sobre câmbio,
            - buscar a cotação atual do dólar,
            - informar a cotação de forma clara ao cliente
        """
    )
