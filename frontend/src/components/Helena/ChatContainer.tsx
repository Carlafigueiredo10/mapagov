import React, { useState, useRef, useEffect } from 'react';
import { Send, Save, Pencil } from 'lucide-react';
import MessageBubble from './MessageBubble';
import ErrorMessage from './ErrorMessage';
import SaveIndicator from './SaveIndicator';

import { useChat } from '../../hooks/useChat';
import { useAutoSave } from '../../hooks/useAutoSave';
import { useSyncHistorico } from '../../hooks/useSyncHistorico';
import { useChatStore } from '../../store/chatStore';
import { loadPOP } from '../../services/helenaApi';
import './ChatContainer.css';

interface ChatContainerProps {
  className?: string;
}

const ChatContainer: React.FC<ChatContainerProps> = ({ className = '' }) => {
  const [inputValue, setInputValue] = useState('');
  const [saveStatus, setSaveStatus] = useState<'salvando' | 'salvo' | 'erro' | 'idle'>('idle');
  const [ultimoSalvamento, setUltimoSalvamento] = useState<Date | undefined>(undefined);
  const [mostrarSeta, setMostrarSeta] = useState(false);
  const [conflictDetected, setConflictDetected] = useState(false);
  const [editandoNome, setEditandoNome] = useState(false);
  const [nomeTemp, setNomeTemp] = useState('');
  const nomeInputRef = useRef<HTMLInputElement>(null);

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
    } else if ((result as { conflict?: boolean }).conflict) {
      setConflictDetected(true);
      setSaveStatus('erro');
    } else {
      setSaveStatus('erro');
      setTimeout(() => setSaveStatus('idle'), 5000);
    }
  };

  // Recarregar dados do servidor após conflito
  const reloadFromServer = async () => {
    const { popUuid, popId: pid, sessionId: sid, updateDadosPOP, setPopIdentifiers } = useChatStore.getState();
    const identifier = popUuid || pid?.toString() || sid;
    if (!identifier) return;

    try {
      const res = await loadPOP(identifier);
      if (res.success && res.pop) {
        updateDadosPOP(res.pop.dados as Record<string, unknown>);
        setPopIdentifiers(res.pop.id, res.pop.uuid, res.pop.integrity_hash);
        setConflictDetected(false);
        setSaveStatus('idle');
      }
    } catch {
      // fallback: manter estado local
    }
  };

  const {
    messages,
    isProcessing,
    error,
    progresso,
    dadosPOP,
    enviarMensagem,
    clearError,
  } = useChat(handleAutoSave);

  const { updateDadosPOP } = useChatStore();
  const nomeUsuario = dadosPOP.nome_usuario || '';

  // Abrir edição inline do nome
  const iniciarEdicaoNome = () => {
    setNomeTemp(nomeUsuario);
    setEditandoNome(true);
    setTimeout(() => nomeInputRef.current?.focus(), 50);
  };

  // Confirmar edição do nome
  const confirmarNome = () => {
    const novoNome = nomeTemp.trim();
    if (novoNome && novoNome !== nomeUsuario) {
      updateDadosPOP({ nome_usuario: novoNome });
    }
    setEditandoNome(false);
  };

  // Sincronizar histórico ao montar componente
  useSyncHistorico();

  // Carregar POP do backend ao montar (backend é fonte de verdade)
  useEffect(() => {
    const { popUuid, popId, sessionId: sid, updateDadosPOP, setPopIdentifiers } = useChatStore.getState();
    const identifier = popUuid || popId?.toString() || sid;
    if (!identifier) return;

    loadPOP(identifier)
      .then((res) => {
        if (res.success && res.pop) {
          const serverSeq = res.pop.autosave_sequence ?? 0;
          const localSeq = useChatStore.getState().popId ? 0 : -1; // se nao tem popId local, backend vence
          if (serverSeq > localSeq || !useChatStore.getState().popId) {
            updateDadosPOP(res.pop.dados as Record<string, unknown>);
            setPopIdentifiers(res.pop.id, res.pop.uuid, res.pop.integrity_hash);
          }
        }
      })
      .catch(() => {
        // 404 = POP ainda nao existe no backend (primeiro acesso), manter dados locais
      });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Auto-save automático
  const { saveNow } = useAutoSave({ interval: 30000, enabled: true });

  // Auto-scroll inteligente: se última mensagem tem interface, rola para o início da mensagem
  useEffect(() => {
    if (messages.length === 0) return;

    const ultimaMensagem = messages[messages.length - 1];

    // Se a última mensagem da Helena tem interface, rolar para o início da mensagem (não para o final)
    if (ultimaMensagem.tipo === 'helena' && ultimaMensagem.interface) {
      // Pequeno delay para garantir que o DOM foi renderizado
      setTimeout(() => {
        const messageElements = document.querySelectorAll('.message-container.helena');
        const ultimoElemento = messageElements[messageElements.length - 1];

        if (ultimoElemento) {
          ultimoElemento.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);
    } else {
      // Mensagens normais: scroll para o final
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
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

      // Limpa qualquer estado persistido no localStorage
      localStorage.removeItem('chat-storage');

      // Recarrega a página para garantir limpeza total
      window.location.reload();
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
      <div className="chat-header-pop">
        {/* Linha superior com botões de ação */}
        <div className="header-top-bar">
          <div className="header-left-buttons">
            <button
              className="header-btn start-btn"
              onClick={reiniciarConversa}
              title="Apagar chat e começar novo mapeamento de POP"
              disabled={isProcessing}
            >
              🚀 Novo POP
            </button>


          </div>

          {/* Área de salvamento - só mostra se houver mensagens */}
          {messages.length > 0 && (
            <div className="header-save-area">
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
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  borderRadius: '8px',
                  cursor: saveStatus === 'salvando' ? 'not-allowed' : 'pointer',
                  opacity: saveStatus === 'salvando' ? 0.6 : 1,
                  color: 'white'
                }}
              >
                <Save size={14} />
                Salvar
              </button>
            </div>
          )}
        </div>

        <div className="header-content">
          <h2>POP — Mapeamento de Procedimento Operacional</h2>
          <p>DECIPEX · Ministério da Gestão e da Inovação</p>
          {(nomeUsuario || dadosPOP.codigo_cap) && (
            <div className="header-meta-line">
              {nomeUsuario && (
                <span className="header-meta-item">
                  <span className="meta-label">Responsável:</span>
                  {editandoNome ? (
                    <input
                      ref={nomeInputRef}
                      type="text"
                      value={nomeTemp}
                      onChange={(e) => setNomeTemp(e.target.value)}
                      onBlur={confirmarNome}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') confirmarNome();
                        if (e.key === 'Escape') setEditandoNome(false);
                      }}
                      className="nome-usuario-input"
                      maxLength={40}
                    />
                  ) : (
                    <span
                      className="nome-usuario-label"
                      onClick={iniciarEdicaoNome}
                      title="Clique para alterar seu nome"
                    >
                      {nomeUsuario} <Pencil size={12} />
                    </span>
                  )}
                </span>
              )}
              {dadosPOP.codigo_cap && (
                <span className="header-meta-item">
                  <span className="meta-label">Código CAP:</span>
                  <span>{dadosPOP.codigo_cap}</span>
                </span>
              )}
            </div>
          )}
        </div>

        {/* Barra de Progresso */}
        <div className="progress-container">
          <div
            className="progress-bar"
            style={{ width: `${(progresso.atual / progresso.total) * 100}%` }}
          />
        </div>
        <div className="progress-text">{progresso.texto}</div>
      </div>

      {/* Banner de conflito */}
      {conflictDetected && (
        <div style={{
          background: '#fff3cd',
          border: '1px solid #ffc107',
          borderRadius: '6px',
          padding: '10px 16px',
          margin: '8px 12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '13px',
          color: '#664d03',
        }}>
          <span>Este POP foi modificado em outra aba.</span>
          <button
            onClick={reloadFromServer}
            style={{
              background: '#ffc107',
              border: 'none',
              borderRadius: '4px',
              padding: '4px 12px',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '13px',
            }}
          >
            Recarregar dados
          </button>
        </div>
      )}

      {/* Messages Area */}
      <div className="messages-area">
        {/* ✅ FIX DUPLICAÇÃO: Removido fallback hardcoded */}
        {/* useSyncHistorico já injeta a mensagem no store */}
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        
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
            key={isProcessing ? 'processing' : 'idle'}
          >
            {isProcessing ? (
              <>
                <span className="loading-spinner" />
                <span>Enviando...</span>
              </>
            ) : (
              <>
                <Send size={18} />
                <span>Enviar</span>
              </>
            )}
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