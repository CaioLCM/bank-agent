from typing import Literal

from langchain.tools import tool

import httpx

from src.core.logger import get_logger

logger = get_logger(__name__)

QUOTES_API_URL = "https://br.dolarapi.com/v1/cotacoes"
TIMEOUT_SECONDS = 10

Currency = Literal["USD", "EUR", "ARS", "CLP", "UYU"]

CURRENCY_NAMES = {
    "USD": "Dólar",
    "EUR": "Euro",
    "ARS": "Peso Argentino",
    "CLP": "Peso Chileno",
    "UYU": "Peso Uruguaio",
}

@tool
async def get_exchange_rate(currency: Currency = "USD"):
    """Busca a cotação atual da moeda informada, em reais.

    Use USD quando o cliente não especificar a moeda.
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(f"{QUOTES_API_URL}/{currency.lower()}")
            response.raise_for_status()
            data = response.json()

        name = CURRENCY_NAMES.get(currency, currency)
        logger.info(
            "cotacao consultada | moeda=%s compra=%s venda=%s",
            currency, data["compra"], data["venda"],
        )
        return (
            f"{name} ({currency}): R$ {data['compra']:.4f} (compra) / "
            f"R$ {data['venda']:.4f} (venda). Atualizado em {data['dataAtualizacao']}."
        )

    except httpx.TimeoutException:
        logger.warning("timeout na consulta de cotacao | moeda=%s", currency)
        return (
            "A consulta de cotação demorou demais e foi interrompida. "
            "Informe ao cliente que o serviço está lento agora e ofereça tentar novamente."
        )
    except httpx.HTTPStatusError as error:
        logger.warning("cotacao respondeu %s | moeda=%s", error.response.status_code, currency)
        return (
            f"A fonte de cotação respondeu com erro {error.response.status_code}. "
            "Informe ao cliente que a cotação está indisponível no momento."
        )
    except httpx.HTTPError:
        logger.exception("falha de rede na consulta de cotacao | moeda=%s", currency)
        return (
            "Não foi possível alcançar a fonte de cotação. "
            "Informe ao cliente que a cotação está indisponível no momento."
        )
    except (KeyError, ValueError):
        logger.exception("formato inesperado na resposta de cotacao | moeda=%s", currency)
        return (
            "A fonte de cotação respondeu em um formato inesperado. "
            "Informe ao cliente que a cotação está indisponível no momento."
        )
