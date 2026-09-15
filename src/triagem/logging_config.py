"""Logs estruturados mínimos para reconstruir uma execução."""

import json
import logging
from typing import Any

from triagem.config import settings

logging.basicConfig(
    level=logging.WARNING,
    format="%(message)s",
)

logger = logging.getLogger("triagem")
logger.setLevel(getattr(logging, settings.log_level, logging.INFO))

# Mantém a demonstração focada nos eventos do grafo, sem logs internos dos SDKs.
logging.getLogger("google_genai.models").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.WARNING)


def registrar_evento(execution_id: str, evento: str, **dados: Any) -> None:
    """Registra um evento em JSON com correlação por execução."""

    registro = {"execution_id": execution_id, "evento": evento, **dados}
    logger.info(json.dumps(registro, ensure_ascii=False, default=str))
