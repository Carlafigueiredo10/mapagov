/**
 * MessageBubbleRich - Bolha de mensagem com suporte a Markdown
 *
 * Paradigma: Mentora Estratégica (não formulário)
 * - Renderiza markdown completo (negrito, listas, código, etc.)
 * - Estilo empático e pedagógico
 * - Suporta blocos de alerta/destaque
 */

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MessageBubbleRichProps {
  tipo: 'user' | 'helena';
  texto: string;
  isLoading?: boolean;
}

export const MessageBubbleRich: React.FC<MessageBubbleRichProps> = ({
  tipo,
  texto,
  isLoading = false
}) => {
  const isUser = tipo === 'user';

  return (
    <div
      style={{
        alignSelf: isUser ? 'flex-end' : 'flex-start',
        maxWidth: '80%',
        animation: 'fadeIn 0.3s ease-in'
      }}
    >
      <div
        style={{
          padding: '16px 20px',
          borderRadius: '16px',
          background: isUser
            ? 'linear-gradient(135deg, #1B4F72 0%, #2874A6 100%)'
            : 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          border: isUser ? 'none' : '1px solid rgba(27, 79, 114, 0.2)',
          boxShadow: isUser
            ? '0 4px 12px rgba(27, 79, 114, 0.3)'
            : '0 4px 12px rgba(27, 79, 114, 0.1)',
          color: isUser ? '#ffffff' : '#2C3E50'
        }}
      >
        {isLoading ? (
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span style={{ fontSize: '18px' }}>⏳</span>
            <span>Helena está pensando...</span>
          </div>
        ) : isUser ? (
          // Mensagem do usuário: sem markdown
          <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
            {texto}
          </div>
        ) : (
          // Mensagem da Helena: com markdown rico
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              // Estilização customizada para elementos markdown
              p: ({ children }) => (
                <p style={{ margin: '8px 0', lineHeight: 1.7 }}>{children}</p>
              ),
              strong: ({ children }) => (
                <strong style={{ fontWeight: 700, color: '#1B4F72' }}>{children}</strong>
              ),
              em: ({ children }) => (
                <em style={{ fontStyle: 'italic', color: '#2874A6' }}>{children}</em>
              ),
              ul: ({ children }) => (
                <ul style={{
                  marginLeft: '20px',
                  marginTop: '8px',
                  marginBottom: '8px',
                  listStyleType: 'disc'
                }}>
                  {children}
                </ul>
              ),
              ol: ({ children }) => (
                <ol style={{
                  marginLeft: '20px',
                  marginTop: '8px',
                  marginBottom: '8px'
                }}>
                  {children}
                </ol>
              ),
              li: ({ children }) => (
                <li style={{ marginBottom: '4px', lineHeight: 1.6 }}>{children}</li>
              ),
              code: ({ children, className }) => {
                const isInline = !className;
                return isInline ? (
                  <code style={{
                    background: 'rgba(27, 79, 114, 0.1)',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    fontSize: '0.9em',
                    fontFamily: 'monospace',
                    color: '#1B4F72'
                  }}>
                    {children}
                  </code>
                ) : (
                  <code style={{
                    display: 'block',
                    background: 'rgba(27, 79, 114, 0.08)',
                    padding: '12px',
                    borderRadius: '8px',
                    fontSize: '0.9em',
                    fontFamily: 'monospace',
                    overflowX: 'auto',
                    marginTop: '8px',
                    marginBottom: '8px'
                  }}>
                    {children}
                  </code>
                );
              },
              blockquote: ({ children }) => (
                <blockquote style={{
                  borderLeft: '4px solid #1B4F72',
                  paddingLeft: '16px',
                  marginLeft: '0',
                  marginTop: '12px',
                  marginBottom: '12px',
                  fontStyle: 'italic',
                  color: '#555'
                }}>
                  {children}
                </blockquote>
              ),
              hr: () => (
                <hr style={{
                  border: 'none',
                  borderTop: '1px solid rgba(27, 79, 114, 0.2)',
                  margin: '16px 0'
                }} />
              ),
              h1: ({ children }) => (
                <h1 style={{
                  fontSize: '1.5em',
                  fontWeight: 700,
                  marginTop: '16px',
                  marginBottom: '12px',
                  color: '#1B4F72'
                }}>
                  {children}
                </h1>
              ),
              h2: ({ children }) => (
                <h2 style={{
                  fontSize: '1.3em',
                  fontWeight: 700,
                  marginTop: '14px',
                  marginBottom: '10px',
                  color: '#1B4F72'
                }}>
                  {children}
                </h2>
              ),
              h3: ({ children }) => (
                <h3 style={{
                  fontSize: '1.1em',
                  fontWeight: 700,
                  marginTop: '12px',
                  marginBottom: '8px',
                  color: '#2874A6'
                }}>
                  {children}
                </h3>
              ),
              // Links
              a: ({ children, href }) => (
                <a
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    color: '#1B4F72',
                    textDecoration: 'underline',
                    fontWeight: 600
                  }}
                >
                  {children}
                </a>
              )
            }}
          >
            {texto}
          </ReactMarkdown>
        )}
      </div>
    </div>
  );
};

export default MessageBubbleRich;
