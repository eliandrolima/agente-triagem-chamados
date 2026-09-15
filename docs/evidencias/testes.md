# Evidência de testes locais

Data: 14/09/2026

## Comandos executados

```powershell
pytest -q
ruff check .
```

## Resultado

```text
............                                                             [100%]
12 passed

All checks passed!
```

Um aviso de depreciação originado internamente no `TestClient` do Starlette foi filtrado
na configuração do pytest. Ele não se refere ao código da aplicação.
