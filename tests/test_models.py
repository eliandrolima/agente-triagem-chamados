import pytest
from pydantic import ValidationError

from triagem.models import ChamadoEntrada


def test_chamado_invalido_e_rejeitado() -> None:
    with pytest.raises(ValidationError):
        ChamadoEntrada(titulo="Erro", descricao="Falhou")

