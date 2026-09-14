"""Configurações da aplicação obtidas de variáveis de ambiente."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True, slots=True)
class Settings:
    """Configurações externas sem armazenar segredos no código."""

    llm_provider: str = os.getenv("LLM_PROVIDER", "google").lower()
    llm_model: str = os.getenv("LLM_MODEL", "")
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()

    def validate_provider(self) -> None:
        if self.llm_provider not in {"google", "openai"}:
            raise ValueError("LLM_PROVIDER deve ser 'google' ou 'openai'.")


settings = Settings()

