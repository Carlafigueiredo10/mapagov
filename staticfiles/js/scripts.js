// ==============================
// CONFIGURAÇÕES DO DOM
// ==============================
const messageForm = document.getElementById('message-form');
const messageInput = document.getElementById('message-input');
const chatMessages = document.getElementById('chat-messages');

// Campos do formulário POP (ordem completa)
const fields = [
  { id: 'processo', label: 'Qual o nome do processo?' },
  { id: 'subprocesso', label: 'Qual o subprocesso?' },
  { id: 'atividade', label: 'Qual a atividade principal?' },
  { id: 'entrega_esperada', label: 'Qual é a entrega esperada?' },
  { id: 'objetivo', label: 'Qual é o objetivo do processo?' },
  { id: 'beneficiario', label: 'Quem é o beneficiário?' },
  { id: 'base_normativa', label: 'Qual a fundamentação legal?' },
  { id: 'sistemas_utilizados', label: 'Quais sistemas são utilizados?' },
  { id: 'responsavel', label: 'Quem é o responsável pelo processo?' },
  { id: 'equipe', label: 'Qual é a equipe envolvida?' },
  { id: 'entradas', label: 'Quais são as entradas do processo? (uma por linha)' },
  { id: 'saidas', label: 'Quais são as saídas do processo? (uma por linha)' },
  { id: 'etapas', label: 'Liste as etapas do processo. (nome — prazo — ponto de controle)' },
  { id: 'riscos', label: 'Quais são os riscos identificados? (Risco | Consequência | Probabilidade | Impacto | Controles)' },
  { id: 'indicadores', label: 'Quais são os indicadores de acompanhamento?' },
  { id: 'licoes_boas_praticas', label: 'Há lições aprendidas ou boas práticas?' }
];

let currentFieldIndex = 0;

// ==============================
// FUNÇÕES DE CHAT
// ==============================
function addMessage(text, sender = 'bot') {
  const msg = document.createElement('div');
  msg.className = `message ${sender}`;
  msg.textContent = text;
  chatMessages.appendChild(msg);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function focusField(fieldId) {
  const field = document.getElementById(fieldId);
  if (field) {
    field.classList.add('border', 'border-danger');
    field.scrollIntoView({ behavior: 'smooth', block: 'center' });
    field.focus();
  }
}

function askNextField() {
  if (currentFieldIndex < fields.length) {
    const { label, id } = fields[currentFieldIndex];
    addMessage(label);
    focusField(id);
  } else {
    addMessage('✅ Formulário completo. Você pode salvar ou gerar o POP.');
  }
}

function handleUserInput(text) {
  if (currentFieldIndex < fields.length) {
    const { id } = fields[currentFieldIndex];
    const field = document.getElementById(id);
    if (field) {
      field.value = text;
      field.classList.remove('border', 'border-danger');
    }
    currentFieldIndex++;
    askNextField();
  }
}

// ==============================
// EVENTOS
// ==============================
messageForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const text = messageInput.value.trim();
  if (!text) return;
  addMessage(text, 'user');
  messageInput.value = '';
  handleUserInput(text);
});

// ==============================
// INICIALIZAÇÃO
// ==============================
window.addEventListener('DOMContentLoaded', () => {
  askNextField();
});