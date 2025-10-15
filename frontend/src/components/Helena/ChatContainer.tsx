import React, { useState, useRef, useEffect } from 'react';
import { Send, Save } from 'lucide-react';
import MessageBubble from './MessageBubble';
import ErrorMessage from './ErrorMessage';
import SaveIndicator from './SaveIndicator';
import { useChat } from '../../hooks/useChat';
import { useAutoSave } from '../../hooks/useAutoSave';
import { useChatStore } from '../../store/chatStore';
import './ChatContainer.css';

interface ChatContainerProps {
  className?: string;
}

const ChatContainer: React.FC<ChatContainerProps> = ({ className = '' }) => {
  const [inputValue, setInputValue] = useState('');
  const [saveStatus, setSaveStatus] = useState<'salvando' | 'salvo' | 'erro' | 'idle'>('idle');
  const [ultimoSalvamento, setUltimoSalvamento] = useState<Date | undefined>(undefined);
  const [mostrarSeta, setMostrarSeta] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-save automático com callback para atualizar status
  const handleAutoSave = async () => {
    setSaveStatus('salvando');
    const result = await saveNow();

    if (result.success) {
      setSaveStatus('salvo');
      setUltimoSalvamento(new Date());
      setTimeout(() => setSaveStatus('idle'), 3000);
    } else {
      setSaveStatus('erro');
      setTimeout(() => setSaveStatus('idle'), 5000);
    }
  };

  const {
    messages,
    isProcessing,
    error,
    progresso,
    enviarMensagem,
    clearError,
  } = useChat(handleAutoSave);

  // Auto-save automático
  const { saveNow } = useAutoSave({ interval: 30000, enabled: true });

  // Auto-scroll para última mensagem
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focar input quando não está processando
  useEffect(() => {
    if (!isProcessing && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isProcessing]);

  // Mostrar seta quando mensagem sobre POP aparecer
  useEffect(() => {
    const temMensagemPOP = messages.some(msg =>
      msg.tipo === 'helena' && msg.mensagem.includes('formulário de Procedimento Operacional Padrão - POP')
    );

    if (temMensagemPOP) {
      setMostrarSeta(true);
      // Esconde a seta após 8 segundos
      const timer = setTimeout(() => setMostrarSeta(false), 8000);
      return () => clearTimeout(timer);
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!inputValue.trim() || isProcessing) return;

    const texto = inputValue.trim();
    setInputValue('');
    
    try {
      await enviarMensagem(texto);
    } catch (err) {
      console.error('Erro ao enviar mensagem:', err);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      // Trigger submit manually
      if (!inputValue.trim() || isProcessing) return;
      const texto = inputValue.trim();
      setInputValue('');
      enviarMensagem(texto);
    }
  };

  const reiniciarConversa = () => {
    if (confirm('Tem certeza que deseja iniciar um novo mapeamento? Isso irá limpar a conversa atual.')) {
      // Reset completo da conversa
      const { resetChat } = useChatStore.getState();
      resetChat();
      setInputValue('');
      
      // Inicia nova conversa
      iniciarMapeamento();
    }
  };

  const iniciarMapeamento = async () => {
    try {
      await enviarMensagem('Iniciar novo mapeamento de POP');
    } catch (error) {
      console.error('Erro ao iniciar mapeamento:', error);
    }
  };

  const handleSalvarManual = async () => {
    setSaveStatus('salvando');
    const result = await saveNow();
    if (result.success) {
      setSaveStatus('salvo');
      setUltimoSalvamento(new Date());
      setTimeout(() => setSaveStatus('idle'), 3000);
    } else {
      setSaveStatus('erro');
      setTimeout(() => setSaveStatus('idle'), 5000);
    }
  };

  return (
    <div className={`chat-container ${className}`}>
      {/* Header */}
      <div className="chat-header">
        <button
          className="header-btn start-btn"
          onClick={reiniciarConversa}
          title="Apagar chat e começar novo mapeamento de POP"
          disabled={isProcessing}
        >
          🚀 Novo POP
        </button>

        <div className="header-content">
          <h2>Helena - Assistente DECIPEX</h2>
          <p>Mapeamento conversacional de POPs</p>
        </div>

        {/* Área de salvamento - só mostra se houver mensagens */}
        {messages.length > 0 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginLeft: 'auto' }}>
            <SaveIndicator status={saveStatus} ultimoSalvamento={ultimoSalvamento} />
            <button
              onClick={handleSalvarManual}
              disabled={saveStatus === 'salvando'}
              className="header-btn save-btn"
              title="Salvar conversa manualmente"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 12px',
                fontSize: '13px',
                backgroundColor: '#f3f4f6',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                cursor: saveStatus === 'salvando' ? 'not-allowed' : 'pointer',
                opacity: saveStatus === 'salvando' ? 0.6 : 1,
              }}
            >
              <Save size={14} />
              Salvar
            </button>
          </div>
        )}

        {/* Barra de Progresso */}
        <div className="progress-container">
          <div
            className="progress-bar"
            style={{ width: `${(progresso.atual / progresso.total) * 100}%` }}
          />
        </div>
        <div className="progress-text">{progresso.texto}</div>
      </div>

      {/* Messages Area */}
      <div className="messages-area">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <MessageBubble
              message={{
                id: 'welcome',
                tipo: 'helena',
                mensagem: '👋 Olá! Sou a Helena, assistente de IA da DECIPEX especializada em mapeamento de processos.\n\nVou te ajudar a documentar seu procedimento de forma clara e estruturada, pergunta por pergunta.\n\nPara começarmos, qual seu nome?',
                timestamp: new Date().toISOString()
              }}
            />
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))
        )}
        
        {error && (
          <ErrorMessage 
            message={error}
            onClose={clearError}
            type="error"
          />
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Section */}
      <form onSubmit={handleSubmit} className="input-section">
        <div className="input-group">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Digite sua mensagem..."
            maxLength={2000}
            disabled={isProcessing}
            className="message-input"
          />

          <button
            type="submit"
            disabled={isProcessing || !inputValue.trim()}
            className="send-button"
          >
            {isProcessing ? (
              <span className="loading-spinner" />
            ) : (
              <Send size={18} />
            )}
            {isProcessing ? 'Enviando...' : 'Enviar'}
          </button>
        </div>
      </form>

      {/* Seta Animada apontando para o POP */}
      {mostrarSeta && (
        <div className="arrow-to-pop">
          ➡️
        </div>
      )}
    </div>
  );
};

export default ChatContainer;