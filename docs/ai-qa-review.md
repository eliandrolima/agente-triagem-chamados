# Evidência de QA com IA

Data: 14/09/2026  
Ferramenta: ChatGPT Work / Codex

## Alteração revisada

Foram revisados o fluxo LangGraph, a tool de consulta de runbooks e os testes da API.
No início da revisão, o projeto possuía somente o teste do health check.

## Problema identificado

A rubrica exigia evidência de sucesso, falha ou entrada inválida e comportamento relevante
do grafo ou da tool. O teste inicial não verificava a ramificação condicional nem a falha
da consulta de contexto. Assim, uma regressão poderia fazer a tool deixar de ser chamada
sem que a suíte detectasse o problema.

## Sugestão da IA

Adicionar testes independentes para:

1. confirmar que severidade crítica percorre `consultar_base`;
2. confirmar que o runbook recuperado influencia `acao_sugerida`;
3. provocar uma categoria sem runbook e verificar a exceção esperada;
4. garantir que prompt injection encerra o grafo sem chamar o LLM;
5. manter os testes sem dependência de rede ou chave externa.

## Decisão adotada pelo aluno

A sugestão foi aceita. Foi criado um `AnalisadorFalso` injetável e foram adicionados testes
de API, grafo, validação, segurança e tool. A opção por um falso simples foi preferida a
mockar internamente os SDKs dos provedores, pois deixa o teste menor e focado no fluxo.

## Resultado

Após a alteração, a suíte passou a cobrir os caminhos direto, com runbook e bloqueado,
além das falhas de entrada e configuração. O resultado local em 14/09/2026 foi:

```text
12 passed
All checks passed!
```

O alerta de depreciação emitido internamente pelo `TestClient` não representa falha do
código do projeto e será acompanhado pelas atualizações das dependências.

