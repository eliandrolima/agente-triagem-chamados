const form = document.querySelector("#triage-form");
const submitButton = document.querySelector("#submit-button");
const formMessage = document.querySelector("#form-message");
const resultPanel = document.querySelector("#result-panel");
const emptyState = document.querySelector("#empty-state");
const resultContent = document.querySelector("#result-content");
const severityBadge = document.querySelector("#severity-badge");

const fields = {
  categoria: document.querySelector("#category"),
  resumo: document.querySelector("#summary"),
  acao_sugerida: document.querySelector("#action"),
  requer_revisao_humana: document.querySelector("#human-review"),
  rota: document.querySelector("#route"),
  fontes_contexto: document.querySelector("#source"),
  execution_id: document.querySelector("#execution-id"),
};

document.querySelector("#fill-example").addEventListener("click", () => {
  form.elements.titulo.value = "API de pagamentos indisponível";
  form.elements.descricao.value =
    "A API retorna erro 503 para todos os clientes desde as 14h e afeta o ambiente de produção.";
  form.elements.servico.value = "pagamentos";
  form.elements.ambiente.value = "producao";
});

function mostrarResultado(resultado) {
  fields.categoria.textContent = resultado.categoria;
  fields.resumo.textContent = resultado.resumo;
  fields.acao_sugerida.textContent = resultado.acao_sugerida;
  fields.requer_revisao_humana.textContent = resultado.requer_revisao_humana ? "Sim" : "Não";
  fields.rota.textContent = resultado.rota;
  fields.fontes_contexto.textContent = resultado.fontes_contexto.join(", ") || "Nenhuma";
  fields.execution_id.textContent = resultado.execution_id;
  fields.execution_id.title = resultado.execution_id;

  severityBadge.textContent = resultado.severidade;
  severityBadge.className = `badge ${resultado.severidade}`;
  severityBadge.hidden = false;
  emptyState.hidden = true;
  resultContent.hidden = false;
  resultPanel.classList.remove("empty");
}

function extrairMensagemErro(corpo) {
  if (Array.isArray(corpo.detail)) {
    return corpo.detail.map((item) => item.msg).join(" ");
  }
  return corpo.detail?.mensagem || "Não foi possível concluir a triagem.";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  formMessage.textContent = "";
  submitButton.disabled = true;
  submitButton.querySelector("span").textContent = "Analisando...";

  const dados = Object.fromEntries(new FormData(form));
  for (const chave of ["servico", "ambiente"]) {
    if (!dados[chave]) delete dados[chave];
  }

  try {
    const resposta = await fetch("/api/tickets/triage", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados),
    });
    const corpo = await resposta.json();
    if (!resposta.ok) throw new Error(extrairMensagemErro(corpo));
    mostrarResultado(corpo);
  } catch (erro) {
    formMessage.textContent = erro.message;
  } finally {
    submitButton.disabled = false;
    submitButton.querySelector("span").textContent = "Analisar chamado";
  }
});

