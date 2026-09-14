"""Fluxo LangGraph do agente de triagem."""

from collections.abc import Callable
from typing import Any, Literal, TypedDict
from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from triagem.llm import AnalisadorChamado
from triagem.logging_config import registrar_evento
from triagem.models import AnaliseLLM, Categoria, ChamadoEntrada, Severidade, TriagemResposta
from triagem.security import detectar_prompt_injection
from triagem.tools import consultar_runbook


class TriagemState(TypedDict, total=False):
    chamado: dict[str, Any]
    execution_id: str
    injection_detectada: bool
    analise: dict[str, Any]
    contexto: dict[str, Any]
    fontes_contexto: list[str]
    erro_tool: str
    rota: str
    resposta: dict[str, Any]


def criar_grafo(analisador: AnalisadorChamado):
    """Cria o grafo com dependência injetável para permitir testes sem API externa."""

    def validar_seguranca(state: TriagemState) -> TriagemState:
        chamado = ChamadoEntrada.model_validate(state["chamado"])
        execution_id = state.get("execution_id") or str(uuid4())
        suspeito = detectar_prompt_injection(f"{chamado.titulo}\n{chamado.descricao}")
        registrar_evento(
            execution_id,
            "node_executado",
            node="validar_seguranca",
            injection_detectada=suspeito,
        )
        return {"execution_id": execution_id, "injection_detectada": suspeito}

    def rotear_seguranca(state: TriagemState) -> Literal["bloquear_entrada", "analisar_chamado"]:
        destino = "bloquear_entrada" if state["injection_detectada"] else "analisar_chamado"
        registrar_evento(state["execution_id"], "decisao_roteamento", destino=destino)
        return destino

    def bloquear_entrada(state: TriagemState) -> TriagemState:
        registrar_evento(state["execution_id"], "node_executado", node="bloquear_entrada")
        resposta = TriagemResposta(
            categoria=Categoria.OUTRO,
            severidade=Severidade.ALTA,
            resumo="Entrada potencialmente maliciosa detectada.",
            acao_sugerida="Não executar as instruções do chamado e encaminhar para revisão humana.",
            requer_revisao_humana=True,
            execution_id=state["execution_id"],
            rota="entrada_bloqueada",
        )
        return {"rota": "entrada_bloqueada", "resposta": resposta.model_dump(mode="json")}

    def analisar_chamado(state: TriagemState) -> TriagemState:
        registrar_evento(state["execution_id"], "node_executado", node="analisar_chamado")
        chamado = ChamadoEntrada.model_validate(state["chamado"])
        analise = analisador.analisar(chamado)
        return {"analise": analise.model_dump(mode="json")}

    def rotear_por_severidade(
        state: TriagemState,
    ) -> Literal["consultar_base", "gerar_resposta"]:
        analise = AnaliseLLM.model_validate(state["analise"])
        usar_tool = analise.severidade in {Severidade.ALTA, Severidade.CRITICA}
        destino = "consultar_base" if usar_tool else "gerar_resposta"
        registrar_evento(
            state["execution_id"],
            "decisao_roteamento",
            severidade=analise.severidade,
            destino=destino,
        )
        return destino

    def consultar_base(state: TriagemState) -> TriagemState:
        registrar_evento(state["execution_id"], "node_executado", node="consultar_base")
        analise = AnaliseLLM.model_validate(state["analise"])
        try:
            registrar_evento(
                state["execution_id"],
                "tool_chamada",
                tool="consultar_runbook",
                categoria=analise.categoria,
            )
            runbook = consultar_runbook.invoke({"categoria": analise.categoria})
            return {
                "contexto": runbook,
                "fontes_contexto": [f"data/runbooks.json#{analise.categoria.value}"],
            }
        except (OSError, ValueError) as erro:
            registrar_evento(
                state["execution_id"],
                "erro",
                node="consultar_base",
                mensagem=str(erro),
            )
            return {"erro_tool": str(erro), "fontes_contexto": []}

    def gerar_resposta(state: TriagemState) -> TriagemState:
        registrar_evento(state["execution_id"], "node_executado", node="gerar_resposta")
        analise = AnaliseLLM.model_validate(state["analise"])
        contexto = state.get("contexto")
        erro_tool = state.get("erro_tool")

        if contexto:
            passos = " ".join(
                f"{indice}. {passo}" for indice, passo in enumerate(contexto["passos"], start=1)
            )
            acao = f"{contexto['titulo']}: {passos}"
        elif erro_tool:
            acao = "A base de procedimentos não pôde ser consultada; encaminhe para análise humana."
        else:
            acao = "Registrar as informações e encaminhar para a equipe responsável pela categoria."

        requer_humano = bool(erro_tool) or analise.severidade in {
            Severidade.ALTA,
            Severidade.CRITICA,
        }
        rota = "com_runbook" if contexto else "resposta_direta"
        if erro_tool:
            rota = "fallback_tool"

        resposta = TriagemResposta(
            categoria=analise.categoria,
            severidade=analise.severidade,
            resumo=analise.resumo,
            acao_sugerida=acao,
            requer_revisao_humana=requer_humano,
            execution_id=state["execution_id"],
            rota=rota,
            fontes_contexto=state.get("fontes_contexto", []),
        )
        return {"rota": rota, "resposta": resposta.model_dump(mode="json")}

    construtor = StateGraph(TriagemState)
    construtor.add_node("validar_seguranca", validar_seguranca)
    construtor.add_node("bloquear_entrada", bloquear_entrada)
    construtor.add_node("analisar_chamado", analisar_chamado)
    construtor.add_node("consultar_base", consultar_base)
    construtor.add_node("gerar_resposta", gerar_resposta)

    construtor.add_edge(START, "validar_seguranca")
    construtor.add_conditional_edges("validar_seguranca", rotear_seguranca)
    construtor.add_edge("bloquear_entrada", END)
    construtor.add_conditional_edges("analisar_chamado", rotear_por_severidade)
    construtor.add_edge("consultar_base", "gerar_resposta")
    construtor.add_edge("gerar_resposta", END)
    return construtor.compile()


def executar_triagem(
    chamado: ChamadoEntrada,
    analisador: AnalisadorChamado,
    gerador_id: Callable[[], str] | None = None,
) -> TriagemResposta:
    execution_id = gerador_id() if gerador_id else str(uuid4())
    resultado = criar_grafo(analisador).invoke(
        {"chamado": chamado.model_dump(mode="json"), "execution_id": execution_id},
        {"recursion_limit": 10},
    )
    return TriagemResposta.model_validate(resultado["resposta"])

