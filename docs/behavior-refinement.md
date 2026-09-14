# Refinamento de comportamento

Data: 14/09/2026

## Problema observado

Na primeira implementação, o FastAPI construía o cliente do LLM como dependência antes
de executar o fluxo. Isso produzia dois comportamentos inadequados:

- uma entrada inválida podia tentar carregar configuração externa antes de retornar 422;
- o cenário de prompt injection exigia uma chave de API mesmo devendo ser bloqueado antes
  de qualquer comunicação com o provedor.

O problema foi revelado por um teste automatizado: `test_api_rejeita_entrada_invalida`
falhou com `ConfiguracaoLLMError` em vez de receber a validação HTTP esperada.

## Alteração realizada

A dependência passou a fornecer uma fábrica, não um cliente pronto. Em seguida foi criado
o `AnalisadorPreguicoso`, que só instancia Gemini ou GPT dentro do node
`analisar_chamado`. O node `validar_seguranca` permanece antes dele no grafo.

## Resultado obtido

- entrada inválida retorna HTTP 422 sem chave;
- prompt injection retorna HTTP 200 com rota `entrada_bloqueada` sem chave;
- uma entrada normal sem configuração retorna HTTP 503 controlado;
- os logs mostram somente `validar_seguranca`, a decisão de roteamento e
  `bloquear_entrada` no cenário adversarial;
- todos os testes passaram após o refinamento.

Esse refinamento mantém a segurança em uma regra determinística e evita depender do LLM
para decidir se o próprio LLM deve receber uma entrada não confiável.

