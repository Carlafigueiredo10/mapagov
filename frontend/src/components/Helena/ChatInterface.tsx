/**
 * ChatInterface - Interface de chat principal
 *
 * Componente central que integra mensagens, input, scroll automático e estados de loading
 */

import React, { useState, useRef, useEffect } from 'react';
import './ChatInterface.css';
import ChatBubble from './ChatBubble';
import ProgressBar from './ProgressBar';
import { useHelenaPE } from '../../hooks/useHelenaPE';

interface ChatInterfaceProps {
  onMudancaEstado?: (estado: string) => void;
  className?: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  onMudancaEstado,
  className = ''
}) => {
  const {
    mensagens,
    sessionData,
    isLoading,
    isInitialized,
    isSaving,
    erro,
    ultimoSave,
    enviarMensagem,
    limparErro
  } = useHelenaPE();

  const [inputTexto, setInputTexto] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const mensagensEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // ============================================================================
  // SCROLL AUTOMÁTICO
  // ============================================================================

  const scrollParaFinal = (comportamento: ScrollBehavior = 'smooth') => {
    mensagensEndRef.current?.scrollIntoView({ behavior: comportamento });
  };

  useEffect(() => {
    if (mensagens.length > 0) {
      scrollParaFinal();
    }
  }, [mensagens]);

  // ============================================================================
  // INDICADOR DE DIGITAÇÃO (simula Helena digitando)
  // ============================================================================

  useEffect(() => {
    if (isLoading) {
      setIsTyping(true);
    } else {
      // Delay para remover typing indicator após resposta chegar
      const timer = setTimeout(() => setIsTyping(false), 300);
      return () => clearTimeout(timer);
    }
  }, [isLoading]);

  // ============================================================================
  // CALLBACK DE MUDANÇA DE ESTADO
  // ============================================================================

  useEffect(() => {
    if (sessionData && onMudancaEstado) {
      onMudancaEstado(sessionData.estado_atual);
    }
  }, [sessionData?.estado_atual, onMudancaEstado]);

  // ============================================================================
  // HANDLERS
  // ============================================================================

  const handleEnviar = async () => {
    const texto = inputTexto.trim();
    if (!texto || isLoading) return;

    setInputTexto('');
    await enviarMensagem(texto);

    // Focar input novamente após enviar
    setTimeout(() => inputRef.current?.focus(), 100);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleEnviar();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputTexto(e.target.value);

    // Auto-ajustar altura do textarea
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  };

  // ============================================================================
  // RENDERIZAÇÃO CONDICIONAL
  // ============================================================================

  if (!isInitialized) {
    return (
      <div className="chat-interface-loading">
        <div className="loading-spinner" />
        <p>Inicializando Helena...</p>
      </div>
    );
  }

  return (
    <div className={`chat-interface ${className}`}>
      {/* Header com progresso */}
      <div className="chat-header">
        <div className="chat-header-info">
          <img src="/helena_plano.png" alt="Helena" className="chat-header-avatar" />
          <div className="chat-header-texto">
            <h3>Helena Planejamento Estratégico</h3>
            <p className="chat-status">
              {isSaving ? (
                <span className="status-salvando">
                  <span className="status-dot pulsing" />
                  Salvando...
                </span>
              ) : ultimoSave ? (
                <span className="status-salvo">
                  <span className="status-dot" />
                  Salvo {new Date(ultimoSave).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                </span>
              ) : (
                <span className="status-online">
                  <span className="status-dot online" />
                  Online
                </span>
              )}
            </p>
          </div>
        </div>

        {/* Barra de progresso */}
        {sessionData && sessionData.percentual_conclusao > 0 && (
          <div className="chat-progresso-container">
            <ProgressBar
              percentual={sessionData.percentual_conclusao}
              altura={6}
              mostrarLabel={false}
              cor="padrao"
            />
            <span className="progresso-texto">{sessionData.percentual_conclusao}% concluído</span>
          </div>
        )}
      </div>

      {/* Lista de mensagens */}
      <div className="chat-mensagens">
        {mensagens.map(mensagem => (
          <ChatBubble key={mensagem.id} mensagem={mensagem} animacao={true} />
        ))}

        {/* Indicador de digitação */}
        {isTyping && (
          <div className="typing-indicator">
            <div className="typing-avatar">
              <img src="/helena_plano.png" alt="Helena" />
            </div>
            <div className="typing-bubble">
              <div className="typing-dots">
                <span />
                <span />
                <span />
              </div>
            </div>
          </div>
        )}

        {/* Erro */}
        {erro && (
          <div className="chat-erro">
            <div className="erro-conteudo">
              <span className="erro-icone">⚠️</span>
              <span className="erro-texto">{erro}</span>
              <button className="erro-fechar" onClick={limparErro}>
                ✕
              </button>
            </div>
          </div>
        )}

        {/* Referência para scroll */}
        <div ref={mensagensEndRef} />
      </div>

      {/* Input de mensagem */}
      <div className="chat-input-container">
        <textarea
          ref={inputRef}
          className="chat-input"
          placeholder="Digite sua mensagem... (Enter para enviar, Shift+Enter para nova linha)"
          value={inputTexto}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          rows={1}
        />
        <button
          className="chat-enviar"
          onClick={handleEnviar}
          disabled={!inputTexto.trim() || isLoading}
        >
          {isLoading ? (
            <span className="loading-spinner-small" />
          ) : (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          )}
        </button>
      </div>

      {/* Dicas */}
      {mensagens.length === 1 && (
        <div className="chat-dicas">
          <p className="dica-titulo">💡 Dicas:</p>
          <ul>
            <li>Use <strong>Enter</strong> para enviar, <strong>Shift+Enter</strong> para nova linha</li>
            <li>Seu progresso é <strong>salvo automaticamente</strong> a cada 5 segundos</li>
            <li>Explore os diferentes <strong>modelos estratégicos</strong> disponíveis</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default ChatInterface;
