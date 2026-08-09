from langchain.tools import tool
from langchain.messages import ToolMessage
from langgraph.graph import END
from langgraph.types import Command
from langgraph.prebuilt import ToolRuntime

@tool
def end_conversation(runtime: ToolRuntime):
    """Encerra o atendimento quando o cliente pede para finalizar a conversa."""
    return Command(
        graph=Command.PARENT,
        update={
            "messages": [
                ToolMessage(
                    content="Atendimento encerrado",
                    tool_call_id=runtime.tool_call_id
                )
            ],
            "conversation_ended": True
        },
        goto=END
    )

@tool
def handoff_to_triage_agent(runtime: ToolRuntime):
    """Devolve o atendimento para o agente de triagem."""
    return Command(
        graph=Command.PARENT,
        update={
            "messages": [
                ToolMessage(
                    content="Transferido para agente de triagem",
                    tool_call_id=runtime.tool_call_id
                )
            ],
            "current_agent": "triage_agent"
        },
        goto="triage_agent"
    )

@tool
def handoff_to_credit_agent(runtime: ToolRuntime):
    """Transfere o atendimento para o agente de crédito."""
    return Command(
        graph=Command.PARENT,
        update={
            "messages": [
                ToolMessage(
                    content="Transferido para agente de crédito",
                    tool_call_id=runtime.tool_call_id
                )
            ],
            "current_agent": "credit_agent"
        },
        goto="credit_agent"
    )

@tool
def handoff_to_credit_interview_agent(runtime: ToolRuntime):
    """Transfere o atendimento para o agente de entrevista de crédito."""
    return Command(
        graph=Command.PARENT,
        update={
            "messages": [
                ToolMessage(
                    content="Transferido para agente de entrevista de crédito",
                    tool_call_id=runtime.tool_call_id
                )
            ],
            "current_agent": "credit_interview_agent"
        },
        goto="credit_interview_agent"
    )

@tool
def handoff_to_exchange_agent(runtime: ToolRuntime):
    """Transfere o atendimento para o agente de câmbio."""
    return Command(
        graph=Command.PARENT,
        update={
            "messages": [
                ToolMessage(
                    content="Transferido para agente de câmbio",
                    tool_call_id=runtime.tool_call_id
                )
            ],
            "current_agent": "exchange_agent"
        },
        goto="exchange_agent"
    )
