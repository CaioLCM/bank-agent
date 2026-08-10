from langchain.agents import create_agent

from src.core.model import get_model

from ..state_model import BankState

from .tools import (
    verify_user,
)

from ..handoff_tools import (
    end_conversation,
    handoff_to_credit_agent,
    handoff_to_credit_interview_agent,
    handoff_to_exchange_agent
)

def create_triage_agent():
    return create_agent(
        model=get_model(),
        state_schema=BankState,
        tools=[verify_user, handoff_to_credit_agent, handoff_to_credit_interview_agent, handoff_to_exchange_agent, end_conversation],
        system_prompt=
        """
            Você é um agente de triagem, atuando como porta de entrada no atendimento:
            - recepcionando o cliente,
            - coletando CPF e data de nascimento para autenticação contra uma
            base de dados (clientes.csv),
            - direcionando para o agente mais apropriado, conforme a necessidade identificada,
            somente após a autenticação bem-sucedida

            O estado da conversa tem o campo `auth`, que indica se o cliente já foi
            autenticado. Se `auth` já for verdadeiro, o cliente está autenticado:
            não colete CPF nem data de nascimento novamente e não chame verify_user,
            apenas identifique a necessidade e faça o redirecionamento.
        """
    )

triage_agent = create_triage_agent()