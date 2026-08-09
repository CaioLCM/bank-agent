from langchain.agents import create_agent

from src.core.model import get_model

from ..state_model import BankState

from .tools import (
    verify_user,
    transfer_to_credit_agent,
    transfer_to_credit_interview_agent,
    transfer_to_exchange_agent
)

def create_triage_agent():
    return create_agent(
        model=get_model(),
        state_schema=BankState,
        tools=[verify_user, transfer_to_credit_agent, transfer_to_credit_interview_agent, transfer_to_exchange_agent],
        system_prompt=
        """
            Você é um agente de triagem, atuando como porta de entrada no atendimento: 
            - recepcionando o cliente, 
            - coletando CPF e data de nascimento para autenticação contra uma
            base de dados (clientes.csv), 
            - direcionando para o agente mais apropriado, conforme a necessidade identificada, 
            somente após a autenticação bem-sucedida
        """
    )

triage_agent = create_triage_agent()