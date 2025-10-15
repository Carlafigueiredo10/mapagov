import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './FluxogramaChat.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface Message {
  type: 'helena' | 'user';
  text: string;
}

interface FluxogramaChatProps {
  enabled: boolean;
  popInfo: any;
  onFluxogramaGenerated: (code: string) => void;
}

export default function FluxogramaChat({ enabled, popInfo, onFluxogramaGenerated }: FluxogramaChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    { type: 'helena', text: 'Olá! Faça upload de um PDF de POP para começarmos a criar o fluxograma. 📊' }
  ]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (enabled && popInfo) {
      const welcomeMessage = `PDF analisado com sucesso! Encontrei o processo: "${popInfo.atividade || 'processo não identificado'}". Vamos mapear as etapas para criar o fluxograma?`;
      setMessages(prev => [...prev, { type: 'helena', text: welcomeMessage }]);
    }
  }, [enabled, popInfo]);

  useEffect(() => {
    // Auto-scroll para última mensagem
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || !enabled || sending) return;

    const userMessage = input.trim();
    setMessages(prev => [...prev, { type: 'user', text: userMessage }]);
    setInput('');
    setSending(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/fluxograma-from-pdf/`, {
        message: userMessage,
      });

      const helenaResponse = response.data.resposta || 'Desculpe, não entendi.';
      setMessages(prev => [...prev, { type: 'helena', text: helenaResponse }]);

      // Verificar se a conversa está completa
      if (response.data.conversa_completa) {
        setMessages(prev => [...prev, {
          type: 'helena',
          text: '✅ Fluxograma completo! Gerando visualização...'
        }]);

        // Aqui você pode chamar uma API para obter o código Mermaid
        // Por enquanto, vamos gerar um exemplo
        const mermaidCode = `graph TD
    A[Início: ${popInfo?.atividade || 'Processo'}]
    B[Etapa 1]
    C[Etapa 2]
    D[Decisão?]
    E[Sim]
    F[Não]
    G[Fim]

    A --> B
    B --> C
    C --> D
    D -->|Sim| E
    D -->|Não| F
    E --> G
    F --> G`;

        onFluxogramaGenerated(mermaidCode);
      }
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      setMessages(prev => [...prev, {
        type: 'helena',
        text: '❌ Erro ao processar mensagem. Tente novamente.'
      }]);
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  return (
    <div className="fluxograma-chat">
      <div className="chat-messages" ref={chatContainerRef}>
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.type}`}>
            {msg.text}
          </div>
        ))}
        {sending && (
          <div className="message helena typing">
            <span></span>
            <span></span>
            <span></span>
          </div>
        )}
      </div>

      <div className="chat-input-group">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Digite sua mensagem..."
          disabled={!enabled || sending}
        />
        <button
          onClick={sendMessage}
          disabled={!enabled || !input.trim() || sending}
        >
          Enviar
        </button>
      </div>
    </div>
  );
}
