/**
 * P6 - Plano de Acao
 *
 * Interface para criacao de planos de acao estruturados (5W2H)
 * Integracao com Helena via contexto 'plano_acao'
 */

import React, { useState, useEffect } from 'react';
import { chatV2, mudarContextoV2, type ChatV2Request, type ChatV2Response } from '../services/helenaApi';
import { Send, Loader, ClipboardList, Target } from 'lucide-react';

export const PlanoAcaoPage: React.FC = () => {
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(false);
  const [progresso, setProgresso] = useState<string | undefined>(undefined);
  const [contextoAtual, setContextoAtual] = useState<string | undefined>(undefined);

  // Inicializa sessao e muda contexto para plano_acao
  useEffect(() => {
    const inicializarSessao = async () => {
      try {
        // Gera session_id unico
        const newSessionId = `plano-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        setSessionId(newSessionId);

        // Primeira mensagem para criar a sessao
        const request: ChatV2Request = {
          mensagem: 'oi',
          session_id: newSessionId,
        };

        const response: ChatV2Response = await chatV2(request);

        // Muda para contexto plano_acao
        const contextResponse = await mudarContextoV2({
          session_id: response.session_id,
          novo_contexto: 'plano_acao'
        });

        setSessionId(contextResponse.session_id);
        setContextoAtual('plano_acao');

        // Adiciona mensagem de boas-vindas
        setMessages([{
          role: 'assistant',
          content: contextResponse.resposta
        }]);

      } catch (error) {
        console.error('Erro ao inicializar sessao:', error);
      }
    };

    inicializarSessao();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);

    // Adicionar mensagem do usuario
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    try {
      const request: ChatV2Request = {
        mensagem: userMessage,
        session_id: sessionId,
      };

      const response: ChatV2Response = await chatV2(request);

      // Atualizar estado
      setSessionId(response.session_id);
      setProgresso(response.progresso);
      setContextoAtual(response.contexto_atual);

      // Adicionar resposta da Helena
      setMessages(prev => [...prev, { role: 'assistant', content: response.resposta }]);

    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Desculpe, ocorreu um erro ao processar sua mensagem.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const sugestoesRapidas = [
    { label: 'Mobilizacao para Mapeamento', texto: 'Quero mobilizar minha equipe para mapear processos' },
    { label: 'Preparacao para Auditoria', texto: 'Preciso preparar minha area para uma auditoria' },
    { label: 'Treinamento de Equipe', texto: 'Quero planejar um treinamento para minha equipe' }
  ];

  const handleSugestao = (texto: string) => {
    setInput(texto);
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px'
    }}>
      <div style={{
        maxWidth: '900px',
        margin: '0 auto'
      }}>
        {/* Header */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.95)',
          borderRadius: '12px',
          padding: '30px',
          marginBottom: '20px',
          boxShadow: '0 10px 40px rgba(0,0,0,0.1)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '10px' }}>
            <img
              src="/helena_plano.png"
              alt="Helena Plano de Ação"
              style={{
                width: '60px',
                height: '60px',
                borderRadius: '50%',
                objectFit: 'cover'
              }}
            />
            <div>
              <h1 style={{
                margin: 0,
                fontSize: '32px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontWeight: 'bold'
              }}>
                P6 - Plano de Acao
              </h1>
              <p style={{ margin: '5px 0 0 0', color: '#666', fontSize: '16px' }}>
                Crie planos estruturados com metodologia 5W2H
              </p>
            </div>
          </div>
        </div>

        {/* Info Panel */}
        {progresso && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '8px',
            padding: '15px 20px',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            gap: '15px',
            boxShadow: '0 4px 15px rgba(0,0,0,0.08)'
          }}>
            <Target size={20} color="#28a745" />
            <div>
              <div style={{ fontSize: '12px', color: '#666', marginBottom: '3px' }}>Progresso</div>
              <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#28a745' }}>{progresso}</div>
            </div>
          </div>
        )}

        {/* Chat Container */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.95)',
          borderRadius: '12px',
          overflow: 'hidden',
          boxShadow: '0 10px 40px rgba(0,0,0,0.1)'
        }}>
          {/* Messages */}
          <div style={{
            padding: '20px',
            minHeight: '450px',
            maxHeight: '500px',
            overflowY: 'auto'
          }}>
            {messages.length === 0 && !isLoading && (
              <div style={{
                textAlign: 'center',
                padding: '60px 20px',
                color: '#999'
              }}>
                <ClipboardList size={48} style={{ marginBottom: '20px', opacity: 0.3 }} />
                <p style={{ fontSize: '18px', marginBottom: '30px' }}>
                  Aguardando conexao com Helena...
                </p>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div
                key={idx}
                style={{
                  marginBottom: '15px',
                  display: 'flex',
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  alignItems: 'flex-start',
                  gap: '10px'
                }}
              >
                {msg.role === 'assistant' && (
                  <img
                    src="/helena_plano.png"
                    alt="Helena"
                    style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '50%',
                      objectFit: 'cover',
                      flexShrink: 0
                    }}
                  />
                )}
                <div style={{
                  maxWidth: '75%',
                  padding: '12px 16px',
                  borderRadius: '12px',
                  background: msg.role === 'user'
                    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                    : '#f8f9fa',
                  color: msg.role === 'user' ? 'white' : '#333',
                  whiteSpace: 'pre-wrap',
                  lineHeight: '1.5'
                }}>
                  {msg.content}
                </div>
              </div>
            ))}

            {isLoading && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                color: '#667eea',
                padding: '10px'
              }}>
                <Loader size={20} className="animate-spin" />
                <span>Helena esta pensando...</span>
              </div>
            )}
          </div>

          {/* Sugestoes Rapidas */}
          {messages.length <= 1 && !isLoading && (
            <div style={{
              padding: '15px 20px',
              borderTop: '1px solid #e9ecef',
              background: '#f8f9fa'
            }}>
              <div style={{ fontSize: '12px', color: '#666', marginBottom: '10px', fontWeight: 'bold' }}>
                Sugestoes Rapidas:
              </div>
              <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                {sugestoesRapidas.map((sug, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSugestao(sug.texto)}
                    style={{
                      padding: '8px 14px',
                      borderRadius: '20px',
                      border: '1px solid #667eea',
                      background: 'white',
                      color: '#667eea',
                      fontSize: '13px',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      fontWeight: '500'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = '#667eea';
                      e.currentTarget.style.color = 'white';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'white';
                      e.currentTarget.style.color = '#667eea';
                    }}
                  >
                    {sug.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input Form */}
          <form
            onSubmit={handleSubmit}
            style={{
              padding: '20px',
              borderTop: '1px solid #e9ecef',
              background: 'white'
            }}
          >
            <div style={{ display: 'flex', gap: '10px' }}>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Digite sua mensagem..."
                disabled={isLoading}
                style={{
                  flex: 1,
                  padding: '12px 16px',
                  border: '2px solid #e9ecef',
                  borderRadius: '8px',
                  fontSize: '15px',
                  outline: 'none',
                  transition: 'border-color 0.2s'
                }}
                onFocus={(e) => e.currentTarget.style.borderColor = '#667eea'}
                onBlur={(e) => e.currentTarget.style.borderColor = '#e9ecef'}
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                style={{
                  padding: '12px 24px',
                  background: isLoading || !input.trim()
                    ? '#ccc'
                    : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: isLoading || !input.trim() ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontWeight: 'bold',
                  fontSize: '15px',
                  transition: 'transform 0.2s'
                }}
                onMouseEnter={(e) => {
                  if (!isLoading && input.trim()) {
                    e.currentTarget.style.transform = 'scale(1.05)';
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'scale(1)';
                }}
              >
                {isLoading ? <Loader size={18} className="animate-spin" /> : <Send size={18} />}
                Enviar
              </button>
            </div>
          </form>
        </div>

        {/* Footer Info */}
        <div style={{
          marginTop: '20px',
          textAlign: 'center',
          color: 'rgba(255, 255, 255, 0.8)',
          fontSize: '14px'
        }}>
          <p>
            Helena Plano de Acao v1.0.0 | Metodologia 5W2H
          </p>
        </div>
      </div>
    </div>
  );
};

export default PlanoAcaoPage;
