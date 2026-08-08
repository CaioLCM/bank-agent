from langchain.tools import tool

@tool
def verify_user(CPF: str, birth: str):
    """Autentica o cliente pelo CPF e data de nascimento na base de clientes."""
    pass

@tool
def transfer_to_credit_agent():
    """Transfere o atendimento para o agente de crédito."""
    pass

@tool
def transfer_to_credit_interview_agent():
    """Transfere o atendimento para o agente de entrevista de crédito."""
    pass

@tool
def transfer_to_exchange_agent():
    """Transfere o atendimento para o agente de câmbio."""
    pass
