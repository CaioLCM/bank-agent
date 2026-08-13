from langchain.agents import create_agent

from langchain.agents.middleware import wrap_model_call

from langchain.messages import SystemMessage

from src.core.auth import verify_token

from src.core.model import get_model

from ..state_model import BankState

from .prompts import AUTHENTICATED_PROMPT, UNAUTHENTICATED_PROMPT

from .tools import (
    verify_user,
)

from ..handoff_tools import (
    end_conversation,
    handoff_to_credit_agent,
    handoff_to_credit_interview_agent,
    handoff_to_exchange_agent
)

@wrap_model_call
async def gate(request, handler):
    # O token de sessão é gerado pelo verify_user e guardado no estado. Aqui ele
    # só é validado: assinatura, expiração e presença. Token inválido ou ausente
    # equivale a cliente não autenticado, e o gate fecha os handoffs.
    auth = verify_token(request.state.get("auth_token")) is not None

    new = request.override(
        tools=[
            handoff_to_credit_agent,
            handoff_to_credit_interview_agent,
            handoff_to_exchange_agent,
            end_conversation,
        ] if auth else [verify_user, end_conversation],
        system_message=SystemMessage(AUTHENTICATED_PROMPT if auth else UNAUTHENTICATED_PROMPT)
    )
    return await handler(new)

def create_triage_agent():
    return create_agent(
        model=get_model(),
        state_schema=BankState,
        tools=[verify_user, handoff_to_credit_agent, handoff_to_credit_interview_agent, handoff_to_exchange_agent, end_conversation],
        middleware=[gate]
    )

triage_agent = create_triage_agent()
