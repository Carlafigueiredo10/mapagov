import { useState, useEffect, useRef } from 'react';
import api from '../../services/api';
import './FluxogramaChat.css';

interface Message {
  type: 'helena' | 'user';
  text: string;
}

interface FluxogramaChatProps {
  enabled: boolean;
  popInfo: any;
  onFluxogramaGenerated: (code: string, steps?: any[], decisoes?: any[]) => void;
}

export default function FluxogramaChat({ enabled, popInfo, onFluxogramaGenerated }: FluxogramaChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    { type: 'helena', text: 'Olá! Você pode importar um PDF de POP ao lado, ou descrever o processo diretamente aqui. Digite "iniciar" para começar.' }
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
      const response = await api.post('/fluxograma-from-pdf/', {
        message: userMessage,
      });

      const data = response.data;
      const helenaResponse = data.resposta || 'Desculpe, não entendi.';
      setMessages(prev => [...prev, { type: 'helena', text: helenaResponse }]);

      if (data.completo && data.fluxograma_mermaid) {
        setMessages(prev => [...prev, {
          type: 'helena',
          text: 'Fluxograma completo! Gerando visualização...'
        }]);
        onFluxogramaGenerated(data.fluxograma_mermaid, data.steps, data.decisoes);
      }
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      setMessages(prev => [...prev, {
        type: 'helena',
        text: 'Erro ao processar mensagem. Tente novamente.'
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
