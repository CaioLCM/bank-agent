"""Token de sessão do cliente autenticado pelo agente de triagem."""

from datetime import datetime, timedelta, timezone

import jwt

from src.core.settings import settings

def create_token(CPF: str) -> str:
    """Gera o token de sessão do cliente recém-autenticado."""
    now = datetime.now(timezone.utc)
    payload = {
        "CPF": CPF,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_ttl_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def verify_token(token: str | None) -> str | None:
    """Devolve o CPF do token válido, ou None se estiver ausente, expirado ou adulterado."""
    if not token:
        return None

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.InvalidTokenError:
        return None

    return payload.get("CPF")
