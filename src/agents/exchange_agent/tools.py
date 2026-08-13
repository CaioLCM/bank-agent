from langchain.tools import tool

import httpx

from src.core.logger import get_logger

logger = get_logger(__name__)

DOLAR_API_URL = "https://br.dolarapi.com/v1/cotacoes/usd"
TIMEOUT_SECONDS = 10

@tool
async def get_dollar_rate():
    """Busca a cotação atual do dólar."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(DOLAR_API_URL)
            response.raise_for_status()
            data = response.json()

        return (
            f"Dólar: R$ {data['compra']:.4f} (compra) / R$ {data['venda']:.4f} (venda). "
            f"Atualizado em {data['dataAtualizacao']}."
        )

    except httpx.TimeoutException:
        logger.warning("timeout na consulta de cotacao | url=%s", DOLAR_API_URL)
        return (
            "A consulta de cotação demorou demais e foi interrompida. "
            "Informe ao cliente que o serviço está lento agora e ofereça tentar novamente."
        )
    except httpx.HTTPStatusError as error:
        logger.warning("cotacao respondeu %s", error.response.status_code)
        return (
            f"A fonte de cotação respondeu com erro {error.response.status_code}. "
            "Informe ao cliente que a cotação está indisponível no momento."
        )
    except httpx.HTTPError:
        logger.exception("falha de rede na consulta de cotacao")
        return (
            "Não foi possível alcançar a fonte de cotação. "
            "Informe ao cliente que a cotação está indisponível no momento."
        )
    except (KeyError, ValueError):
        logger.exception("formato inesperado na resposta de cotacao")
        return (
            "A fonte de cotação respondeu em um formato inesperado. "
            "Informe ao cliente que a cotação está indisponível no momento."
        )
