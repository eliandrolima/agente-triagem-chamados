# Agente de Triagem de Chamados Técnicos

Projeto avaliativo de recuperação do curso **IA para Desenvolvedores — SCTEC**.

## Objetivo

Receber chamados relacionados a software, infraestrutura ou suporte, analisá-los com um
modelo de linguagem e produzir uma recomendação estruturada para apoiar a triagem.

## Estado atual

Fundação do projeto concluída:

- API FastAPI com health check;
- contratos Pydantic para entrada, análise e saída;
- configuração de Gemini ou GPT por variáveis de ambiente;
- base local de runbooks e cenários reproduzíveis;
- primeiro teste automatizado;
- proteção de credenciais com `.gitignore` e `.env.example`.

O fluxo LangGraph, a interface web e as evidências serão adicionados incrementalmente.

## Requisitos

- Python 3.11 ou superior.

## Instalação local

```bash
python -m venv .venv
```

Ative o ambiente virtual e instale o projeto:

```bash
python -m pip install -e ".[dev]"
```

Copie `.env.example` para `.env` e preencha somente a chave do provedor escolhido.

## Execução

```bash
uvicorn triagem.api:app --reload
```

Health check: `http://127.0.0.1:8000/api/health`

Documentação interativa: `http://127.0.0.1:8000/docs`

## Testes

```bash
pytest
ruff check .
```

## Segurança

O arquivo `.env` é ignorado pelo Git. Nunca adicione chaves reais ao repositório.

