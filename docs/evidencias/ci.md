# Evidência da extensão de CI

Data: 14/09/2026

O pipeline **Qualidade** executa Ruff e pytest no Ubuntu a cada push para `main` e em
pull requests.

Execução validada: https://github.com/eliandrolima/agente-triagem-chamados/actions/runs/34889282155

Resultado:

```text
Instalar dependências  OK
Verificar código       OK
Executar testes        OK
```

A primeira execução revelou uma diferença de importação entre Windows e Linux. A suíte
foi corrigida com um pacote de testes explícito, validada localmente e reenviada. A
execução acima confirma a correção no runner Linux e constitui evidência funcional da
extensão técnica.
