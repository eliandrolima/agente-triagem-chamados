"""Ponto de entrada HTTP da aplicação."""

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from triagem import __version__
from triagem.graph import executar_triagem
from triagem.llm import (
    AnalisadorChamado,
    AnalisadorComLLM,
    AnalisadorPreguicoso,
    ConfiguracaoLLMError,
)
from triagem.models import ChamadoEntrada, SaudeResposta, TriagemResposta

app = FastAPI(
    title="Agente de Triagem de Chamados Técnicos",
    description="Projeto avaliativo do curso IA para Desenvolvedores do SCTEC.",
    version=__version__,
)

PASTA_STATIC = Path(__file__).parent / "static"


@app.get("/api/health", response_model=SaudeResposta, tags=["sistema"])
def verificar_saude() -> SaudeResposta:
    """Confirma que a API está disponível sem depender do provedor de LLM."""

    return SaudeResposta(
        status="ok",
        aplicacao="agente-triagem-chamados",
        versao=__version__,
    )


@app.get("/", include_in_schema=False)
def pagina_inicial() -> FileResponse:
    """Entrega a interface web da demonstração."""

    return FileResponse(PASTA_STATIC / "index.html")


def obter_fabrica_analisador() -> Callable[[], AnalisadorChamado]:
    """Fornece a fábrica do analisador sem acessar segredos antes da validação."""

    return AnalisadorComLLM


@app.post("/api/tickets/triage", response_model=TriagemResposta, tags=["triagem"])
def realizar_triagem(
    chamado: ChamadoEntrada,
    fabrica_analisador: Annotated[
        Callable[[], AnalisadorChamado], Depends(obter_fabrica_analisador)
    ],
) -> TriagemResposta:
    """Executa o fluxo completo de triagem do chamado."""

    try:
        analisador = AnalisadorPreguicoso(fabrica_analisador)
        return executar_triagem(chamado, analisador)
    except ConfiguracaoLLMError as erro:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"codigo": "llm_nao_configurado", "mensagem": str(erro)},
        ) from erro
    except Exception as erro:
        logging.getLogger("triagem").exception("Falha controlada durante a triagem")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "codigo": "falha_na_triagem",
                "mensagem": "Não foi possível concluir a triagem. Tente novamente.",
            },
        ) from erro


app.mount("/static", StaticFiles(directory=PASTA_STATIC), name="static")
