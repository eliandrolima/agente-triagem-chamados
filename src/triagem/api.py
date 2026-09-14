"""Ponto de entrada HTTP da aplicação."""

from fastapi import FastAPI

from triagem import __version__
from triagem.models import SaudeResposta

app = FastAPI(
    title="Agente de Triagem de Chamados Técnicos",
    description="Projeto avaliativo do curso IA para Desenvolvedores do SCTEC.",
    version=__version__,
)


@app.get("/api/health", response_model=SaudeResposta, tags=["sistema"])
def verificar_saude() -> SaudeResposta:
    """Confirma que a API está disponível sem depender do provedor de LLM."""

    return SaudeResposta(
        status="ok",
        aplicacao="agente-triagem-chamados",
        versao=__version__,
    )

