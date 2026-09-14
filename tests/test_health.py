from fastapi.testclient import TestClient

from tests.fakes import AnalisadorFalso
from triagem.api import app
from triagem.models import AnaliseLLM, Categoria, Severidade

client = TestClient(app)


def test_health_check_retorna_aplicacao_disponivel() -> None:
    resposta = client.get("/api/health")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "status": "ok",
        "aplicacao": "agente-triagem-chamados",
        "versao": "0.1.0",
    }


def test_api_executa_triagem_com_saida_estruturada() -> None:
    from triagem.api import obter_fabrica_analisador

    analisador = AnalisadorFalso(
        AnaliseLLM(
            categoria=Categoria.INFRAESTRUTURA,
            severidade=Severidade.ALTA,
            resumo="Serviço instável em produção.",
            justificativa="Há impacto no serviço principal.",
        )
    )
    app.dependency_overrides[obter_fabrica_analisador] = lambda: lambda: analisador
    try:
        resposta = client.post(
            "/api/tickets/triage",
            json={
                "titulo": "API de pagamentos instável",
                "descricao": "A API apresenta erros intermitentes no ambiente de produção.",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["categoria"] == "infraestrutura"
    assert corpo["rota"] == "com_runbook"
    assert corpo["requer_revisao_humana"] is True


def test_api_rejeita_entrada_invalida() -> None:
    resposta = client.post(
        "/api/tickets/triage",
        json={"titulo": "Erro", "descricao": "Falhou"},
    )

    assert resposta.status_code == 422
