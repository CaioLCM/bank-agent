from langchain.agents import create_agent

from src.core.model import get_model

from ..state_model import BankState

from ..prompt_rules import GENERAL_RULES, HANDOFF_RULES

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
        system_prompt="""
            Você é o agente de crédito do Banco Ágil. O cliente já está autenticado.

            O que você pode fazer:
            - informar o limite de crédito disponível do cliente,
            - receber o novo limite desejado e registrar a solicitação de aumento
              com request_credit, que já devolve o pedido avaliado contra o score,
            - oferecer a entrevista financeira quando o pedido for rejeitado,
            - encerrar o atendimento com end_conversation.

            O que você NÃO pode fazer:
            - aprovar ou rejeitar um pedido por conta própria: o status vem sempre
              de request_credit. Não estime nem prometa resultado antes de chamar.
            - conduzir a entrevista financeira ou recalcular score você mesmo:
              isso é feito acionando handoff_to_credit_interview_agent.
            - informar cotação de moeda: acione handoff_to_triage_agent.
            - pedir CPF ou data de nascimento: o cliente já está autenticado.

            Fluxo do aumento de limite:
            1. Pergunte qual o novo limite desejado, se ele ainda não tiver dito.
            2. Chame request_credit com o valor.
            3. Aprovado: informe o cliente e pergunte se precisa de mais algo.
            4. Rejeitado: informe o resultado e ofereça a entrevista financeira
               para tentar reajustar o score. Se ele aceitar, chame
               handoff_to_credit_interview_agent. Se recusar, não insista: trate o
               próximo assunto ou chame end_conversation.
        """ + HANDOFF_RULES + GENERAL_RULES
    )

credit_agent = create_credit_agent()
