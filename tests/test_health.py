from fastapi.testclient import TestClient

from triagem.api import app

client = TestClient(app)


def test_health_check_retorna_aplicacao_disponivel() -> None:
    resposta = client.get("/api/health")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "status": "ok",
        "aplicacao": "agente-triagem-chamados",
        "versao": "0.1.0",
    }
