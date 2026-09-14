import pytest

from triagem.models import Categoria
from triagem.tools import RunbookNaoEncontradoError, carregar_runbook


def test_tool_retorna_runbook_valido() -> None:
    runbook = carregar_runbook(Categoria.SOFTWARE)

    assert runbook["titulo"] == "Falha em aplicação"
    assert len(runbook["passos"]) >= 1


def test_tool_trata_categoria_sem_runbook() -> None:
    with pytest.raises(RunbookNaoEncontradoError):
        carregar_runbook(Categoria.OUTRO)

