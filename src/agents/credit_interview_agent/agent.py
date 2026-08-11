from langchain.agents import create_agent

from src.core.model import get_model

from ..state_model import BankState

from .prompts import SYSTEM_PROMPT

from .tools import (
    update_score
)

from ..handoff_tools import (
    end_conversation,
    handoff_to_credit_agent,
    handoff_to_triage_agent
)

def create_credit_interview_agent():
    return create_agent(
        model=get_model(),
        state_schema=BankState,
        tools=[update_score, handoff_to_credit_agent, handoff_to_triage_agent, end_conversation],
        system_prompt=SYSTEM_PROMPT
    )

credit_interview_agent = create_credit_interview_agent()
