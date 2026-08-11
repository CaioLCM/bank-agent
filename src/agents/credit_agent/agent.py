from langchain.agents import create_agent

from src.core.model import get_model

from ..state_model import BankState

from .prompts import SYSTEM_PROMPT

from .tools import (
    request_credit
)

from ..handoff_tools import (
    end_conversation,
    handoff_to_credit_interview_agent,
    handoff_to_triage_agent
)

def create_credit_agent():
    return create_agent(
        model=get_model(),
        state_schema=BankState,
        tools=[request_credit, handoff_to_credit_interview_agent, handoff_to_triage_agent, end_conversation],
        system_prompt=SYSTEM_PROMPT
    )

credit_agent = create_credit_agent()
