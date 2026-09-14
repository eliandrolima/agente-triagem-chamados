"""Contratos de entrada e saída da API."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Categoria(StrEnum):
    SOFTWARE = "software"
    INFRAESTRUTURA = "infraestrutura"
    SUPORTE = "suporte"
    OUTRO = "outro"


class Severidade(StrEnum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class ChamadoEntrada(BaseModel):
    titulo: str = Field(min_length=5, max_length=160)
    descricao: str = Field(min_length=10, max_length=4_000)
    servico: str | None = Field(default=None, max_length=100)
    ambiente: str | None = Field(default=None, max_length=50)

    @field_validator("titulo", "descricao", "servico", "ambiente")
    @classmethod
    def remover_espacos_extras(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        return " ".join(valor.split())


class AnaliseLLM(BaseModel):
    categoria: Categoria
    severidade: Severidade
    resumo: str = Field(min_length=5, max_length=500)
    justificativa: str = Field(min_length=5, max_length=500)


class TriagemResposta(BaseModel):
    categoria: Categoria
    severidade: Severidade
    resumo: str
    acao_sugerida: str
    requer_revisao_humana: bool
    execution_id: str
    rota: str
    fontes_contexto: list[str] = Field(default_factory=list)


class ErroControlado(BaseModel):
    codigo: str
    mensagem: str
    detalhes: dict[str, Any] = Field(default_factory=dict)


class SaudeResposta(BaseModel):
    status: str
    aplicacao: str
    versao: str

