import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import DOMPurify from 'dompurify';
import type { ProductCode, PortalChatMessage } from '../../types/portal.types';
import { chatRecepcao } from '../../services/helenaApi';
import InterfaceDecisaoProduto from './InterfaceDecisaoProduto';
import styles from './PortalChat.module.css';

// Dados dos produtos disponíveis para o menu inicial (espelhado do backend)
const PRODUTOS_MENU = [
  {
    key: 'pop',
    nome: 'Gerador de POP',
    descricao_curta: 'Estrutura o processo e gera o Procedimento Operacional Padrão.',
  },
  {
    key: 'fluxograma',
    nome: 'Gerador de Fluxograma',
    descricao_curta: 'Representa visualmente o fluxo do processo mapeado.',
  },
  {
    key: 'riscos',
    nome: 'Análise de Riscos',
    descricao_curta: 'Identifica, avalia e sugere tratamento de riscos do processo.',
  },
  {
    key: 'planejamento',
    nome: 'Planejamento Estratégico',
    descricao_curta: 'Organiza objetivos, metas e diretrizes institucionais.',
  },
];

interface PortalChatProps {
  selectedProduct: ProductCode;
}

export default function PortalChat({ selectedProduct }: PortalChatProps) {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<PortalChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [sessionId] = useState(() => {
    const stored = localStorage.getItem('helena_portal_session_id');
    if (stored) return stored;
    const newId = `portal_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
    localStorage.setItem('helena_portal_session_id', newId);
    return newId;
  });

  const messagesAreaRef = useRef<HTMLDivElement>(null);

  const inputDesabilitado = isTransitioning;

  // Mensagem inicial institucional com menu de produtos
  useEffect(() => {
    const welcomeMessage: PortalChatMessage = {
      id: 'welcome',
      text: 'Olá. Posso orientar você sobre o uso da plataforma ou ajudar a localizar '
        + 'o produto adequado para sua necessidade.<br><br>'
        + 'Você pode selecionar um produto abaixo ou digitar sua pergunta.',
      sender: 'helena',
      timestamp: new Date(),
      tipo_interface: 'decisao_produto',
      dados_interface: {
        produtos: PRODUTOS_MENU,
        permite_texto: true,
        estado: 'INICIO',
      },
    };
    setMessages([welcomeMessage]);
  }, []);

  const scrollToBottom = () => {
    if (messagesAreaRef.current) {
      messagesAreaRef.current.scrollTop = messagesAreaRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addMessage = (msg: PortalChatMessage) => {
    setMessages((prev) => [...prev, msg]);
  };

  const handleSendMessage = async (messageText?: string) => {
    const message = messageText || inputMessage.trim();
    if (!message || isLoading || isTransitioning) return;

    // Adicionar mensagem do usuario (nao mostrar chaves de produto como texto)
    const isProdutoKey = ['pop', 'riscos', 'planejamento', 'fluxograma', 'ainda_nao_sei'].includes(message);
    if (!isProdutoKey) {
      addMessage({
        id: `${Date.now()}_user`,
        text: message,
        sender: 'user',
        timestamp: new Date(),
      });
    }

    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await chatRecepcao({
        message,
        produto: selectedProduct,
        session_id: sessionId,
      });

      // Transicao para produto: mostrar mensagem e navegar
      if (response.tipo_interface === 'transicao_produto' && response.route) {
        setIsTransitioning(true);
        addMessage({
          id: `${Date.now()}_transicao`,
          text: response.resposta,
          sender: 'helena',
          timestamp: new Date(),
          tipo_interface: 'transicao_produto',
        });
        setTimeout(() => {
          navigate(response.route!);
        }, 1500);
        return;
      }

      // Mensagem normal (possivelmente com interface de decisao)
      addMessage({
        id: `${Date.now()}_helena`,
        text: response.resposta,
        sender: 'helena',
        timestamp: new Date(),
        tipo_interface: response.tipo_interface,
        dados_interface: response.dados_interface,
      });
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      addMessage({
        id: `${Date.now()}_erro`,
        text: 'Desculpe, ocorreu um erro. Tente novamente.',
        sender: 'helena',
        timestamp: new Date(),
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleProductSelect = (produtoKey: string) => {
    handleSendMessage(produtoKey);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
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
          <h2>Iniciar trabalho</h2>
          <p>Selecione um produto ou tire dúvidas com a assistente.</p>
        </div>
      </div>

      {/* Area de Mensagens */}
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
            <div className={styles.messageContent}>
              {/* Texto da mensagem */}
              {message.tipo_interface === 'transicao_produto' ? (
                <div className={styles.transitionMessage}>
                  {message.text}
                </div>
              ) : (
                <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(message.text) }} />
              )}

              {/* Interface de decisao de produto */}
              {message.tipo_interface === 'decisao_produto' && message.dados_interface && (
                <InterfaceDecisaoProduto
                  dados={message.dados_interface as {
                    produtos: Array<{ key: string; nome: string; descricao_curta: string }>;
                    permite_texto: boolean;
                    estado: string;
                  }}
                  onConfirm={handleProductSelect}
                />
              )}
            </div>
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
        {inputDesabilitado ? (
          <div className={styles.inputDisabledMessage}>
            Redirecionando para o produto selecionado...
          </div>
        ) : (
          <div className={styles.inputWrapper}>
            <input
              type="text"
              className={styles.messageInput}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Digite sua dúvida..."
              disabled={isLoading}
            />
            <button
              className={styles.sendButton}
              onClick={() => handleSendMessage()}
              disabled={isLoading || !inputMessage.trim()}
            >
              <span>Enviar</span>
              <span>&rarr;</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
