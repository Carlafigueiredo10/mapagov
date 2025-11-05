/**
 * ChatBubble - Componente de mensagem individual
 *
 * Exibe mensagens do usuário e da Helena com animações e metadados
 */

import React from 'react';
import './ChatBubble.css';
import { Mensagem } from '../../hooks/useHelenaPE';

interface ChatBubbleProps {
  mensagem: Mensagem;
  animacao?: boolean;
}

export const ChatBubble: React.FC<ChatBubbleProps> = ({ mensagem, animacao = true }) => {
  const isHelena = mensagem.tipo === 'helena';

  return (
    <div
      className={`chat-bubble-container ${isHelena ? 'helena' : 'usuario'} ${
        animacao ? 'animate-in' : ''
      }`}
    >
      {/* Avatar */}
      {isHelena && (
        <div className="chat-avatar">
          <img src="/helena_plano.png" alt="Helena" />
        </div>
      )}

      {/* Bubble */}
      <div className={`chat-bubble ${mensagem.tipo}`}>
        {/* Conteúdo principal */}
        <div className="chat-texto">{mensagem.texto}</div>

        {/* Metadados (progresso, percentual) */}
        {mensagem.metadados && (
          <div className="chat-metadados">
            {mensagem.metadados.progresso && (
              <div className="chat-progresso">
                <span className="progresso-icon">📊</span>
                <span className="progresso-texto">{mensagem.metadados.progresso}</span>
              </div>
            )}

            {mensagem.metadados.percentual !== undefined && (
              <div className="chat-percentual">
                <div className="percentual-barra-fundo">
                  <div
                    className="percentual-barra-progresso"
                    style={{ width: `${mensagem.metadados.percentual}%` }}
                  />
                </div>
                <span className="percentual-texto">{mensagem.metadados.percentual}%</span>
              </div>
            )}

            {mensagem.metadados.modelo_selecionado && (
              <div className="chat-modelo">
                <span className="modelo-icon">🎯</span>
                <span className="modelo-texto">
                  Modelo: {mensagem.metadados.modelo_selecionado}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Timestamp */}
        <div className="chat-timestamp">
          {mensagem.timestamp.toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit'
          })}
        </div>
      </div>

      {/* Avatar do usuário (placeholder) */}
      {!isHelena && (
        <div className="chat-avatar usuario-avatar">
          <div className="usuario-inicial">U</div>
        </div>
      )}
    </div>
  );
};

export default ChatBubble;
