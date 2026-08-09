from langgraph.graph import StateGraph, START, END

from langgraph.checkpoint.memory import InMemorySaver

from .state_model import BankState

from src.agents.triage_agent.agent import triage_agent
from src.agents.credit_agent.agent import credit_agent
from src.agents.credit_interview_agent.agent import credit_interview_agent
from src.agents.exchange_agent.agent import exchange_agent

def next_agent(state: BankState) -> str:
    return state.current_agent

agentsWorkflow = StateGraph(state_schema=BankState)

agentsWorkflow.add_node("triage_agent", triage_agent)
agentsWorkflow.add_node("credit_agent", credit_agent)
agentsWorkflow.add_node("credit_interview_agent", credit_interview_agent)
agentsWorkflow.add_node("exchange_agent", exchange_agent)

agentsWorkflow.add_conditional_edges(
    START, next_agent, {
        "triage_agent": "triage_agent",
        "credit_agent": "credit_agent",
        "credit_interview_agent": "credit_interview_agent",
        "exchange_agent": "exchange_agent"
    }
)

agentsWorkflow.add_edge("triage_agent", END)
agentsWorkflow.add_edge("credit_agent", END)
agentsWorkflow.add_edge("credit_interview_agent", END)
agentsWorkflow.add_edge("exchange_agent", END)

orchestrator = agentsWorkflow.compile(checkpointer=InMemorySaver())
