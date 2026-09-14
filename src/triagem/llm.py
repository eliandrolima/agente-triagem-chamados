"""Abstração mínima para alternar entre Gemini e GPT."""

import os
from typing import Protocol

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from triagem.config import Settings, settings
from triagem.models import AnaliseLLM, ChamadoEntrada

INSTRUCAO_SISTEMA = """
Você classifica chamados técnicos de software, infraestrutura ou suporte.
Considere somente os fatos informados no chamado. Não invente sintomas, causas ou ações.
Retorne a categoria, a severidade, um resumo objetivo e uma justificativa curta.
Use severidade crítica somente quando houver indisponibilidade ampla, risco de segurança
ou impacto grave em produção. Pedidos fora do domínio devem usar a categoria 'outro'.
""".strip()


class ConfiguracaoLLMError(RuntimeError):
    """Indica configuração ausente ou inválida do provedor de LLM."""


class AnalisadorChamado(Protocol):
    def analisar(self, chamado: ChamadoEntrada) -> AnaliseLLM: ...


class AnalisadorComLLM:
    """Executa classificação com saída estruturada pelo provedor escolhido."""

    def __init__(self, configuracao: Settings = settings) -> None:
        configuracao.validate_provider()
        if not configuracao.llm_model:
            raise ConfiguracaoLLMError("Configure LLM_MODEL no arquivo .env.")

        if configuracao.llm_provider == "google":
            if not os.getenv("GOOGLE_API_KEY"):
                raise ConfiguracaoLLMError("Configure GOOGLE_API_KEY no arquivo .env.")
            modelo = ChatGoogleGenerativeAI(model=configuracao.llm_model, temperature=0)
        else:
            if not os.getenv("OPENAI_API_KEY"):
                raise ConfiguracaoLLMError("Configure OPENAI_API_KEY no arquivo .env.")
            modelo = ChatOpenAI(model=configuracao.llm_model, temperature=0)

        self._modelo_estruturado = modelo.with_structured_output(AnaliseLLM)

    def analisar(self, chamado: ChamadoEntrada) -> AnaliseLLM:
        conteudo = (
            f"Título: {chamado.titulo}\n"
            f"Descrição: {chamado.descricao}\n"
            f"Serviço: {chamado.servico or 'não informado'}\n"
            f"Ambiente: {chamado.ambiente or 'não informado'}"
        )
        resultado = self._modelo_estruturado.invoke(
            [SystemMessage(content=INSTRUCAO_SISTEMA), HumanMessage(content=conteudo)]
        )
        return AnaliseLLM.model_validate(resultado)

