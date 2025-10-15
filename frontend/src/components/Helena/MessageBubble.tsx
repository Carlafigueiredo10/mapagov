import './MessageBubble.css';
import './InterfaceDinamica.css';
import type { HelenaMessage } from '../../types/simples';
import InterfaceDinamica from './InterfaceDinamica';
import { useChat } from '../../hooks/useChat';

interface MessageBubbleProps {
  message: HelenaMessage;
}

function MessageBubble({ message }: MessageBubbleProps) {
  const { responderInterface } = useChat();

  const handleInterfaceResponse = (resposta: string) => {
    responderInterface(resposta);
  };

  // ✅ VALIDAÇÃO 1: Não renderizar se mensagem vazia
  if (!message.mensagem || message.mensagem.trim() === '') {
    console.warn('⚠️ Mensagem vazia detectada:', message);
    return null;
  }

  // ✅ VALIDAÇÃO 2: Verificar se interface é válida
  const temInterfaceValida =
    message.interface &&
    message.interface.tipo &&
    message.interface.tipo.trim() !== '';

  // Debug: Ver o que está chegando
  if (message.interface) {
    console.log('📦 MessageBubble - Interface recebida:', message.interface);
  }

  return (
    <div className={`message-container ${message.tipo}`}>
      <div className="message-wrapper">
        {/* Avatar da Helena (só para mensagens dela) */}
        {message.tipo === 'helena' && (
          <div className="message-avatar">
            <img
              src="/helena_mapeamento.png"
              alt="Helena"
              className="avatar-image"
            />
          </div>
        )}

        <div className={`message ${message.tipo} ${message.loading ? 'loading' : ''}`}>
          {message.mensagem}
        </div>
      </div>

      {/* ✅ Só renderizar interface se for válida E tiver conteúdo */}
      {temInterfaceValida && (
        <InterfaceDinamica
          interfaceData={message.interface!}
          onRespond={handleInterfaceResponse}
        />
      )}
    </div>
  );
}

export default MessageBubble;