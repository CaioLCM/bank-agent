from langchain.agents import create_agent

from langchain.agents.middleware import wrap_model_call

from langchain.messages import SystemMessage

from src.core.model import get_model

from ..state_model import BankState

from ..prompt_rules import GENERAL_RULES, HANDOFF_RULES

from .tools import (
    verify_user,
)

from ..handoff_tools import (
    end_conversation,
    handoff_to_credit_agent,
    handoff_to_credit_interview_agent,
    handoff_to_exchange_agent
)

PROMPT_NAO_AUTENTICADO = """
    Você é o agente de triagem do Banco Ágil, a porta de entrada do atendimento.
    O cliente AINDA NÃO está autenticado.

    O que você pode fazer agora:
    - saudar o cliente e recepcioná-lo,
    - coletar o CPF e a data de nascimento,
    - chamar verify_user com os dois dados,
    - encerrar o atendimento com end_conversation.

    O que você NÃO pode fazer:
    - tratar de limite de crédito, score, aumento de limite ou cotação de moeda.
      Se o cliente trouxer o assunto, registre que vai cuidar disso e conclua
      a autenticação primeiro.
    - prosseguir com qualquer serviço antes de verify_user confirmar os dados.
    - inventar o resultado da autenticação: ele vem sempre de verify_user.

    Fluxo:
    1. Saudação breve.
    2. Peça o CPF.
    3. Peça a data de nascimento.
    4. Chame verify_user com os dois.
    5. Se falhar, informe que os dados não conferem e peça novamente. São no
       máximo 3 tentativas; na terceira falha consecutiva, informe de maneira
       agradável que não foi possível autenticar e chame end_conversation.
""" + GENERAL_RULES

PROMPT_AUTENTICADO = """
    Você é o agente de triagem do Banco Ágil, a porta de entrada do atendimento.
    O cliente JÁ está autenticado.

    O que você pode fazer agora:
    - identificar qual assunto o cliente quer tratar,
    - acionar o handoff correspondente:
      - limite de crédito, aumento de limite, score: handoff_to_credit_agent
      - entrevista financeira para reajustar score: handoff_to_credit_interview_agent
      - cotação de moeda: handoff_to_exchange_agent
    - encerrar o atendimento com end_conversation.

    O que você NÃO pode fazer:
    - pedir CPF ou data de nascimento novamente: o cliente já se identificou.
    - informar limite, score ou cotação você mesmo: você não tem acesso a esses
      dados, acione o handoff do assunto.
    - registrar solicitação de aumento de limite ou conduzir a entrevista.
""" + HANDOFF_RULES + GENERAL_RULES

@wrap_model_call
async def gate(request, handler):
    auth = request.state.get("auth", False)

    new = request.override(
        tools=[
            handoff_to_credit_agent,
            handoff_to_credit_interview_agent,
            handoff_to_exchange_agent,
            end_conversation,
        ] if auth else [verify_user, end_conversation],
        system_message=SystemMessage(PROMPT_AUTENTICADO if auth else PROMPT_NAO_AUTENTICADO)
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