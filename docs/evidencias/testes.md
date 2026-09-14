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
12 passed, 1 warning in 5.75s

All checks passed!
```

O aviso é originado no `TestClient` do Starlette por uma API de compatibilidade do AnyIO.
Ele não altera o resultado dos testes nem indica falha no código da aplicação.

