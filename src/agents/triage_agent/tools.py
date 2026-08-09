from langchain.tools import tool

@tool
def verify_user(CPF: str, birth: str):
    """Autentica o cliente pelo CPF e data de nascimento na base de clientes."""
    pass
