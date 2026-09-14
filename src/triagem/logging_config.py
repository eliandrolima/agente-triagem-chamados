"""Logs estruturados mínimos para reconstruir uma execução."""

import json
import logging
from typing import Any

from triagem.config import settings

logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(message)s",
)

logger = logging.getLogger("triagem")


def registrar_evento(execution_id: str, evento: str, **dados: Any) -> None:
    """Registra um evento em JSON com correlação por execução."""

    registro = {"execution_id": execution_id, "evento": evento, **dados}
    logger.info(json.dumps(registro, ensure_ascii=False, default=str))

