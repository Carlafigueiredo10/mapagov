// Helena Natural - Sistema que FUNCIONA DE VERDADE
class HelenaNatural {
    constructor() {
        this.dadosExtraidos = {};
        this.conversaAtiva = true;
        this.inicializar();
    }

    inicializar() {
        // Primeira mensagem automática
        this.adicionarMensagem('Helena', 'Bom dia! Sou a Helena, sua assistente para mapeamento de processos. Qual é o seu nome?');
        
        // Event listeners
        document.getElementById('enviar-btn').addEventListener('click', () => this.enviarMensagem());
        document.getElementById('user-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.enviarMensagem();
        });
    }

    async enviarMensagem() {
        const input = document.getElementById('user-input');
        const mensagem = input.value.trim();
        
        if (!mensagem) return;
        
        // Mostrar mensagem do usuário
        this.adicionarMensagem('Usuário', mensagem);
        input.value = '';
        
        try {
            // Enviar para Helena
            const response = await fetch('/api/chat_message/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    message: mensagem,
                    contexto: 'mapeamento_natural',
                    dados_atuais: this.dadosExtraidos
                })
            });
            
            const data = await response.json();
            
            // Mostrar resposta da Helena
            this.adicionarMensagem('Helena', data.resposta);
            
            // Verificar se Helena extraiu dados
            if (data.dados_extraidos) {
                this.dadosExtraidos = { ...this.dadosExtraidos, ...data.dados_extraidos };
            }
            
            // Verificar se conversa está completa
            if (data.conversa_completa) {
                this.mostrarResumoFinal();
            }
            
        } catch (error) {
            console.error('Erro:', error);
            this.adicionarMensagem('Sistema', '❌ Erro na comunicação. Tente novamente.');
        }
    }

    mostrarResumoFinal() {
        const dados = this.dadosExtraidos;
        
        const resumo = `
        📋 <strong>RESUMO DO QUE ENTENDI:</strong><br><br>
        
        📍 <strong>Processo:</strong> ${dados.nome_processo || 'Não informado'}<br>
        🎯 <strong>Objetivo:</strong> ${dados.objetivo || 'Não informado'}<br>
        👤 <strong>Responsável:</strong> ${dados.responsavel || 'Não informado'}<br>
        📥 <strong>Recebe de:</strong> ${dados.origem || 'Não informado'}<br>
        📤 <strong>Envia para:</strong> ${dados.destino || 'Não informado'}<br><br>
        
        <strong>Etapas principais:</strong><br>
        ${dados.etapas ? dados.etapas.map((etapa, i) => `${i+1}. ${etapa}`).join('<br>') : 'Não informadas'}<br><br>
        
        ✅ <strong>Posso preencher o formulário com esses dados?</strong>
        `;
        
        this.adicionarMensagem('Helena', resumo);
        this.mostrarBotoesConfirmacao();
    }

    mostrarBotoesConfirmacao() {
        const chatContainer = document.getElementById('chat-container');
        
        const botoesDiv = document.createElement('div');
        botoesDiv.className = 'confirmacao-botoes';
        botoesDiv.innerHTML = `
            <div style="text-align: center; margin: 20px 0;">
                <button onclick="helena.preencherFormulario()" class="btn-confirmar">
                    ✅ Sim, preencher formulário
                </button>
                <button onclick="helena.continuarConversa()" class="btn-continuar">
                    ✏️ Preciso ajustar algo
                </button>
            </div>
        `;
        
        chatContainer.appendChild(botoesDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    preencherFormulario() {
        const dados = this.dadosExtraidos;
        let preenchidos = 0;
        
        // Preencher campos se existirem
        const campos = {
            'nome_processo': dados.nome_processo,
            'objetivo': dados.objetivo,
            'responsavel': dados.responsavel,
            'origem': dados.origem,
            'destino': dados.destino,
            'etapas': dados.etapas ? dados.etapas.join('\n') : '',
            'descricao': dados.descricao,
            'observacoes': dados.observacoes
        };
        
        Object.entries(campos).forEach(([id, valor]) => {
            const campo = document.getElementById(id);
            if (campo && valor) {
                campo.value = valor;
                campo.style.backgroundColor = '#e8f5e8';
                campo.style.border = '2px solid #4CAF50';
                preenchidos++;
            }
        });
        
        // Feedback
        this.adicionarMensagem('Helena', 
            `✅ Perfeito! Preenchidos ${preenchidos} campos no formulário. ` +
            `Agora você pode revisar os dados e salvar o processo!`
        );
        
        // Remover botões de confirmação
        const botoes = document.querySelector('.confirmacao-botoes');
        if (botoes) botoes.remove();
        
        // Scroll para o formulário
        document.getElementById('formulario-container').scrollIntoView({ 
            behavior: 'smooth' 
        });
    }

    continuarConversa() {
        // Remover botões
        const botoes = document.querySelector('.confirmacao-botoes');
        if (botoes) botoes.remove();
        
        this.adicionarMensagem('Helena', 
            'Sem problemas! Me diga o que precisa ajustar e continuamos o mapeamento.'
        );
        
        document.getElementById('user-input').focus();
    }

    adicionarMensagem(remetente, mensagem) {
        const chatContainer = document.getElementById('chat-container');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${remetente.toLowerCase()}-message`;
        
        const isHelena = remetente === 'Helena';
        const avatar = isHelena ? '🤖' : '👤';
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="avatar">${avatar}</span>
                <span class="sender">${remetente}</span>
                <span class="timestamp">${new Date().toLocaleTimeString()}</span>
            </div>
            <div class="message-content">${mensagem}</div>
        `;
        
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

// CSS inline para não precisar de arquivo separado
const style = document.createElement('style');
style.textContent = `
    .message { margin: 15px 0; padding: 15px; border-radius: 10px; }
    .helena-message { background: #f0f8ff; border-left: 4px solid #4CAF50; }
    .usuário-message { background: #f9f9f9; border-left: 4px solid #2196F3; }
    .message-header { font-size: 12px; color: #666; margin-bottom: 8px; }
    .avatar { font-size: 16px; margin-right: 8px; }
    .sender { font-weight: bold; }
    .timestamp { float: right; }
    .message-content { line-height: 1.5; }
    .btn-confirmar, .btn-continuar { 
        padding: 12px 24px; margin: 0 10px; border: none; border-radius: 6px; 
        cursor: pointer; font-size: 14px; font-weight: bold; 
    }
    .btn-confirmar { background: #4CAF50; color: white; }
    .btn-continuar { background: #ff9800; color: white; }
    .btn-confirmar:hover { background: #45a049; }
    .btn-continuar:hover { background: #e68900; }
`;
document.head.appendChild(style);

// Inicializar quando a página carregar
let helena;
document.addEventListener('DOMContentLoaded', () => {
    helena = new HelenaNatural();
});