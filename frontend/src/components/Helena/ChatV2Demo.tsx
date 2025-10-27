/**
 * 🚀 FASE 1 - Componente de Demonstração da Nova API
 *
 * Testa o endpoint /api/chat-v2/ com HelenaCore
 * Mostra:
 * - Progresso das etapas
 * - Sugestão de contexto
 * - Metadados (versão do agente)
 * - Estado persistente entre mensagens
 */

import React, { useState } from 'react';
import { chatV2, type ChatV2Request, type ChatV2Response } from '../../services/helenaApi';
import { Send, Loader } from 'lucide-react';

export const ChatV2Demo: React.FC = () => {
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(false);
  const [progresso, setProgresso] = useState<string | undefined>(undefined);
  const [agentInfo, setAgentInfo] = useState<{ name: string; version: string } | undefined>(undefined);
  const [contextoAtual, setContextoAtual] = useState<string | undefined>(undefined);
  const [sugestaoContexto, setSugestaoContexto] = useState<string | undefined>(undefined);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);

    // Adicionar mensagem do usuário
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
      setAgentInfo({
        name: response.metadados.agent_name,
        version: response.metadados.agent_version,
      });
      setContextoAtual(response.contexto_atual);
      setSugestaoContexto(response.sugerir_contexto || undefined);

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

  return (
    <div style={{
      maxWidth: '800px',
      margin: '0 auto',
      padding: '20px',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '20px',
        borderRadius: '12px',
        marginBottom: '20px'
      }}>
        <h1 style={{ margin: '0 0 10px 0', fontSize: '24px' }}>
          🚀 Helena V2 - FASE 1 Demo
        </h1>
        <p style={{ margin: 0, opacity: 0.9, fontSize: '14px' }}>
          Nova arquitetura com HelenaCore + SessionManager + Redis
        </p>
      </div>

      {/* Info Panel */}
      {(sessionId || progresso || agentInfo) && (
        <div style={{
          background: '#f8f9fa',
          border: '1px solid #e9ecef',
          borderRadius: '8px',
          padding: '15px',
          marginBottom: '20px',
          fontSize: '14px'
        }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            {sessionId && (
              <div>
                <strong>Session ID:</strong>
                <div style={{ fontFamily: 'monospace', fontSize: '12px', color: '#666' }}>
                  {sessionId.substring(0, 8)}...
                </div>
              </div>
            )}
            {progresso && (
              <div>
                <strong>Progresso:</strong>
                <div style={{ color: '#28a745', fontWeight: 'bold' }}>{progresso}</div>
              </div>
            )}
            {agentInfo && (
              <div>
                <strong>Agente:</strong>
                <div>{agentInfo.name} v{agentInfo.version}</div>
              </div>
            )}
            {contextoAtual && (
              <div>
                <strong>Contexto:</strong>
                <div style={{ textTransform: 'capitalize' }}>{contextoAtual}</div>
              </div>
            )}
          </div>
          {sugestaoContexto && (
            <div style={{
              marginTop: '10px',
              padding: '10px',
              background: '#fff3cd',
              borderRadius: '6px',
              borderLeft: '3px solid #ffc107'
            }}>
              💡 <strong>Sugestão:</strong> Mudar para contexto "{sugestaoContexto}"
            </div>
          )}
        </div>
      )}

      {/* Messages */}
      <div style={{
        background: 'white',
        border: '1px solid #e9ecef',
        borderRadius: '8px',
        padding: '20px',
        minHeight: '400px',
        maxHeight: '500px',
        overflowY: 'auto',
        marginBottom: '20px'
      }}>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: '#999', padding: '40px 0' }}>
            <p>👋 Olá! Sou a Helena.</p>
            <p>Digite algo como "Quero mapear o processo de compras" para começar.</p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} style={{
            display: 'flex',
            justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
            marginBottom: '15px'
          }}>
            <div style={{
              maxWidth: '70%',
              padding: '12px 16px',
              borderRadius: '12px',
              background: msg.role === 'user' ? '#667eea' : '#f1f3f5',
              color: msg.role === 'user' ? 'white' : '#212529',
              whiteSpace: 'pre-wrap',
              lineHeight: '1.5'
            }}>
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#999' }}>
            <Loader size={16} className="animate-spin" />
            <span>Helena está pensando...</span>
          </div>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '10px' }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Digite sua mensagem..."
          disabled={isLoading}
          style={{
            flex: 1,
            padding: '12px 16px',
            border: '1px solid #e9ecef',
            borderRadius: '8px',
            fontSize: '14px',
            outline: 'none'
          }}
          autoFocus
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          style={{
            padding: '12px 24px',
            background: isLoading || !input.trim() ? '#e9ecef' : '#667eea',
            color: isLoading || !input.trim() ? '#999' : 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: isLoading || !input.trim() ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '14px',
            fontWeight: 500
          }}
        >
          <Send size={16} />
          Enviar
        </button>
      </form>

      <div style={{
        marginTop: '20px',
        padding: '15px',
        background: '#e7f3ff',
        borderRadius: '8px',
        fontSize: '13px',
        color: '#004085'
      }}>
        <strong>ℹ️ Recursos FASE 1:</strong>
        <ul style={{ margin: '10px 0 0 0', paddingLeft: '20px' }}>
          <li>✅ Stateless architecture (estado no DB/Redis)</li>
          <li>✅ Multi-tenancy por Orgão</li>
          <li>✅ Versionamento de agentes</li>
          <li>✅ Progresso tracking em tempo real</li>
          <li>✅ Sugestão automática de contexto</li>
          <li>✅ Idempotência (req_uuid)</li>
        </ul>
      </div>
    </div>
  );
};

export default ChatV2Demo;
