from langchain.tools import tool
from langchain.messages import AIMessage
from langgraph.graph import END
from langgraph.types import Command
from langgraph.prebuilt import ToolRuntime

from .state_model import state_as_dict

# O Command com graph=PARENT aborta o subgrafo antes de as escritas dele
# propagarem, então o que uma tool gravou no mesmo turno se perderia. Estes
# campos são relidos do estado do subgrafo e repassados junto do handoff.
CAMPOS_PROPAGADOS = ("auth_token", "auth_attempts")

def _estado_propagado(runtime: ToolRuntime) -> dict:
    state = state_as_dict(runtime)
    return {campo: state[campo] for campo in CAMPOS_PROPAGADOS if campo in state}

@tool
def end_conversation(runtime: ToolRuntime):
    """Encerra o atendimento e finaliza o loop de execução.

    Use quando o cliente pedir para encerrar a conversa, se despedir, ou quando
    o assunto tiver sido resolvido e ele não quiser mais nada. Use também quando
    a autenticação falhar pela terceira vez consecutiva.

    Depois disso nenhum agente responde: só chame quando não houver mais nada a
    fazer. Se o cliente ainda quiser outro serviço, prefira uma tool de handoff.
    """
    return Command(
        graph=Command.PARENT,
        update={
            **_estado_propagado(runtime),
            "messages": [
                AIMessage(content="Atendimento encerrado")
            ],
            "conversation_ended": True,
            "auth_token": None
        },
        goto=END
    )

@tool
def handoff_to_triage_agent(runtime: ToolRuntime):
    """Devolve o atendimento para o agente de triagem.

    O agente de triagem é a porta de entrada: autentica o cliente por CPF e data
    de nascimento e identifica qual assunto ele quer tratar.

    Use quando o assunto atual estiver concluído e o cliente trouxer uma demanda
    fora do seu escopo, ou quando não estiver claro para qual agente encaminhar.
    O cliente continua autenticado, então ele não precisará se identificar de novo.
    """
    return Command(
        graph=Command.PARENT,
        update={
            **_estado_propagado(runtime),
            "current_agent": "triage_agent"
        },
        goto="triage_agent"
    )

@tool
def handoff_to_credit_agent(runtime: ToolRuntime):
    """Transfere o atendimento para o agente de crédito.

    O agente de crédito consulta o limite de crédito disponível do cliente e
    processa pedidos de aumento de limite, avaliando-os contra o score atual.

    Use quando o cliente perguntar qual é o seu limite, pedir aumento de limite,
    ou tratar de qualquer assunto relacionado ao crédito dele. Use também para
    devolver o cliente ao crédito depois de a entrevista recalcular o score,
    para que o pedido seja reavaliado. Exige cliente autenticado.
    """
    return Command(
        graph=Command.PARENT,
        update={
            **_estado_propagado(runtime),
            "current_agent": "credit_agent"
        },
        goto="credit_agent"
    )

@tool
def handoff_to_credit_interview_agent(runtime: ToolRuntime):
    """Transfere o atendimento para o agente de entrevista de crédito.

    O agente de entrevista faz perguntas sobre renda mensal, tipo de emprego,
    despesas fixas, dependentes e dívidas ativas, recalcula o score do cliente
    com esses dados e o devolve ao agente de crédito para nova análise.

    Use quando um pedido de aumento de limite for rejeitado e o cliente aceitar
    passar pela entrevista para tentar reajustar o score. Não transfira sem o
    cliente concordar, e não use se ele só quiser consultar o score.
    """
    return Command(
        graph=Command.PARENT,
        update={
            **_estado_propagado(runtime),
            "current_agent": "credit_interview_agent"
        },
        goto="credit_interview_agent"
    )

@tool
def handoff_to_exchange_agent(runtime: ToolRuntime):
    """Transfere o atendimento para o agente de câmbio.

    O agente de câmbio consulta a cotação atual do dólar em
    uma fonte externa e informa o valor ao cliente.

    Use quando o cliente perguntar sobre cotação, câmbio, ou o valor do dólar. 
    Não use para assuntos de crédito ou limite.
    """
    return Command(
        graph=Command.PARENT,
        update={
            **_estado_propagado(runtime),
            "current_agent": "exchange_agent"
        },
        goto="exchange_agent"
    )
