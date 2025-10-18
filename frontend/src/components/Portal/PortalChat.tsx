import { useState, useEffect, useRef } from 'react';
import type { ProductCode, PortalChatMessage } from '../../types/portal.types';
import { chatRecepcao } from '../../services/helenaApi';
import { productMessages } from '../../data/products';
import styles from './PortalChat.module.css';

interface PortalChatProps {
  selectedProduct: ProductCode;
}

export default function PortalChat({ selectedProduct }: PortalChatProps) {
  const [messages, setMessages] = useState<PortalChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => {
    const stored = localStorage.getItem('helena_portal_session_id');
    if (stored) return stored;
    const newId = `portal_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('helena_portal_session_id', newId);
    return newId;
  });

  const messagesAreaRef = useRef<HTMLDivElement>(null);

  // Mensagem inicial da Helena
  useEffect(() => {
    const welcomeMessage: PortalChatMessage = {
      id: 'welcome',
      text: `Oi! 👋<br>
      Eu sou a <strong>Helena</strong>, sua agente de Inteligência Artificial aqui no MapaGov.
      <br><br>
      Meu papel é te guiar dentro deste projeto — ajudando a organizar processos, criar fluxogramas, montar POPs, gerar dossiês ou apoiar em análises, tudo a partir desta plataforma.
      <br><br>
      Ali no lado esquerdo, você vai ver o <strong>catálogo de produtos do MapaGov</strong>.<br>
      É por lá que você pode explorar as ferramentas disponíveis e acompanhar o que está sendo desenvolvido.
      <br><br>
      Antes de começarmos, me conta um pouco sobre você:<br>
      <strong>em que área trabalha ou com que tipo de atividade lida no dia a dia?</strong>
      <br><br>
      Assim eu consigo entender melhor seu contexto e te mostrar os caminhos mais úteis pra sua rotina.
      <br><br>
      Pode falar livremente — eu estou aqui pra ouvir e te ajudar no que precisar. 🌿`,
      sender: 'helena',
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);

    // Verificar mensagem inicial do localStorage (vinda da landing)
    const initialMessage = localStorage.getItem('initialMessage');
    if (initialMessage) {
      localStorage.removeItem('initialMessage');
      setInputMessage(initialMessage);
      // Pequeno delay para garantir que o input foi renderizado
      setTimeout(() => handleSendMessage(initialMessage), 100);
    }
  }, []);

  // Adicionar mensagem quando produto é selecionado
  useEffect(() => {
    if (messages.length > 1) { // Não adicionar na primeira renderização
      const productMessage = productMessages[selectedProduct] || 'Produto selecionado!';
      addMessage(productMessage, 'helena');
    }
  }, [selectedProduct]);

  const scrollToBottom = () => {
    if (messagesAreaRef.current) {
      messagesAreaRef.current.scrollTop = messagesAreaRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addMessage = (text: string, sender: 'user' | 'helena') => {
    const newMessage: PortalChatMessage = {
      id: `${Date.now()}_${Math.random()}`,
      text,
      sender,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newMessage]);
  };

  const handleSendMessage = async (messageText?: string) => {
    const message = messageText || inputMessage.trim();
    if (!message || isLoading) return;

    addMessage(message, 'user');
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await chatRecepcao({
        message,
        produto: selectedProduct,
        session_id: sessionId,
      });

      addMessage(response.resposta, 'helena');
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      addMessage('Desculpe, ocorreu um erro. Tente novamente.', 'helena');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className={styles.chatContainer}>
      {/* Chat Header */}
      <div className={styles.chatHeader}>
        <div className={styles.helenaAvatar}>
          <img src="/helena_avatar.png" alt="Helena" />
        </div>
        <div className={styles.headerInfo}>
          <h2>Helena - Assistente GRC</h2>
          <p>Especialista em Governança, Riscos e Conformidade</p>
        </div>
      </div>

      {/* Área de Mensagens */}
      <div className={styles.messagesArea} ref={messagesAreaRef}>
        {messages.map((message) => (
          <div
            key={message.id}
            className={`${styles.message} ${styles[message.sender]}`}
          >
            <div className={styles.messageAvatar}>
              {message.sender === 'helena' ? (
                <img src="/helena_avatar.png" alt="Helena" />
              ) : (
                'U'
              )}
            </div>
            <div
              className={styles.messageContent}
              dangerouslySetInnerHTML={{ __html: message.text }}
            />
          </div>
        ))}

        {isLoading && (
          <div className={`${styles.message} ${styles.helena}`}>
            <div className={styles.messageAvatar}>
              <img src="/helena_avatar.png" alt="Helena" />
            </div>
            <div className={styles.typingIndicator}>
              <div className={styles.typingDot}></div>
              <div className={styles.typingDot}></div>
              <div className={styles.typingDot}></div>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className={styles.inputArea}>
        <div className={styles.inputWrapper}>
          <input
            type="text"
            className={styles.messageInput}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Digite sua mensagem..."
            disabled={isLoading}
          />
          <button
            className={styles.sendButton}
            onClick={() => handleSendMessage()}
            disabled={isLoading || !inputMessage.trim()}
          >
            <span>Enviar</span>
            <span>→</span>
          </button>
        </div>
      </div>
    </div>
  );
}
