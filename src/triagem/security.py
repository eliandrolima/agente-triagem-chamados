"""Validações determinísticas para conteúdo não confiável."""

import re

PADROES_PROMPT_INJECTION = (
    r"ignore\s+(todas\s+)?as\s+instru[cç][oõ]es",
    r"revele\s+.*(chave|token|senha|segredo)",
    r"mostre\s+.*(prompt|mensagem)\s+(do\s+)?sistema",
    r"system\s+prompt",
    r"developer\s+message",
)


def detectar_prompt_injection(texto: str) -> bool:
    """Detecta padrões explícitos usados no cenário adversarial demonstrável."""

    texto_normalizado = texto.casefold()
    return any(re.search(padrao, texto_normalizado) for padrao in PADROES_PROMPT_INJECTION)

