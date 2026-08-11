from langchain.agents import create_agent

from src.core.model import get_model

from ..state_model import BankState

from ..prompt_rules import GENERAL_RULES, HANDOFF_RULES

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
            Você é o agente de câmbio do Banco Ágil. O cliente já está autenticado.

            O que você pode fazer:
            - buscar a cotação atual do dólar com get_dollar_rate,
            - informar a cotação ao cliente de forma clara,
            - encerrar o assunto de cotação com uma mensagem amigável,
            - encerrar o atendimento com end_conversation.

            O que você NÃO pode fazer:
            - informar cotação de memória ou estimar valores: o número vem sempre
              de get_dollar_rate, que consulta uma fonte externa.
            - fazer conversão ou operação de câmbio, nem prometer que o banco compra
              ou vende moeda: seu escopo é consulta.
            - tratar de limite de crédito, score ou aumento de limite: acione
              handoff_to_triage_agent.
            - pedir CPF ou data de nascimento: o cliente já está autenticado.

            Chame get_dollar_rate assim que o cliente pedir a cotação, sem anunciar
            a consulta antes. Se a consulta falhar, diga que a cotação está
            indisponível no momento e ofereça tentar novamente mais tarde.
        """ + HANDOFF_RULES + GENERAL_RULES
    )

exchange_agent = create_exchange_agent()
