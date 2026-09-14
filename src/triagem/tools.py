"""Tools utilizadas pelo fluxo de triagem."""

import json
from pathlib import Path
from typing import Any

from langchain_core.tools import tool
from pydantic import BaseModel

from triagem.models import Categoria

CAMINHO_RUNBOOKS = Path(__file__).resolve().parents[2] / "data" / "runbooks.json"


class ConsultaRunbookEntrada(BaseModel):
    categoria: Categoria


class RunbookNaoEncontradoError(ValueError):
    """Indica que a base não possui procedimento para a categoria."""


def carregar_runbook(categoria: Categoria) -> dict[str, Any]:
    """Consulta e valida um runbook na base JSON local."""

    with CAMINHO_RUNBOOKS.open(encoding="utf-8") as arquivo:
        runbooks = json.load(arquivo)

    runbook = runbooks.get(categoria.value)
    if not runbook:
        raise RunbookNaoEncontradoError(
            f"Nenhum runbook foi encontrado para a categoria '{categoria.value}'."
        )
    if not runbook.get("titulo") or not runbook.get("passos"):
        raise ValueError("O runbook encontrado possui formato inválido.")
    return runbook


@tool(args_schema=ConsultaRunbookEntrada)
def consultar_runbook(categoria: Categoria) -> dict[str, Any]:
    """Recupera o procedimento técnico indicado para uma categoria de chamado."""

    return carregar_runbook(categoria)

