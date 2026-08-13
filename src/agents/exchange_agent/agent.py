from langchain.agents import create_agent

from src.core.model import get_model

from ..state_model import BankState

from .prompts import SYSTEM_PROMPT

from .tools import (
    get_exchange_rate
)

from ..handoff_tools import (
    end_conversation,
    handoff_to_triage_agent
)

def create_exchange_agent():
    return create_agent(
        model=get_model(),
        state_schema=BankState,
        tools=[get_exchange_rate, handoff_to_triage_agent, end_conversation],
        system_prompt=SYSTEM_PROMPT
    )

exchange_agent = create_exchange_agent()
