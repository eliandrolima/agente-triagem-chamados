from triagem.models import AnaliseLLM, ChamadoEntrada


class AnalisadorFalso:
    def __init__(self, analise: AnaliseLLM) -> None:
        self.analise = analise
        self.chamadas = 0

    def analisar(self, chamado: ChamadoEntrada) -> AnaliseLLM:
        self.chamadas += 1
        return self.analise

