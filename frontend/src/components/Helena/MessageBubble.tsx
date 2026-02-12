import './MessageBubble.css';
import './InterfaceDinamica.css';
import type { HelenaMessage } from '../../types/simples';
import InterfaceDinamica from './InterfaceDinamica';
import BadgeTrofeu from './BadgeTrofeu';
import { useChat } from '../../hooks/useChat';
import ReactMarkdown from 'react-markdown';
import { useState, useEffect, useRef } from 'react';

interface MessageBubbleProps {
  message: HelenaMessage;
}

function MessageBubble({ message }: MessageBubbleProps) {
  const { responderInterface } = useChat();
  const [partesVisiveis, setPartesVisiveis] = useState<string[]>([]);
  const messageEndRef = useRef<HTMLDivElement>(null);

  const handleInterfaceResponse = (resposta: string) => {
    responderInterface(resposta).catch((err) => {
      const status = err?.response?.status;
      const body = err?.response?.data;
      console.error(`[MessageBubble] Erro na resposta de interface (HTTP ${status}):`, body || err);
    });
  };

  // ✅ VALIDAÇÃO 1: Não renderizar se mensagem vazia E sem interface
  // Mensagem pode ser vazia quando há interface (ex: card de atividade, lista de áreas)
  if ((!message.mensagem || message.mensagem.trim() === '') && !message.interface) {
    console.warn('⚠️ Mensagem vazia SEM interface detectada:', message);
    return null;
  }

  // ✅ Detectar mensagens com delay e quebrar em partes
  const mensagemTexto = message.mensagem || '';  // Garantir string (pode ser vazia se só houver interface)
  const temDelay = mensagemTexto.includes('[DELAY:');
  const partesMensagem = temDelay
    ? mensagemTexto.split(/\[DELAY:\d+\]/).map(p => p.trim()).filter(p => p)
    : mensagemTexto ? [mensagemTexto] : [];

  // ✅ Extrair valores reais dos delays (não usar fixo 1000ms)
  const extractDelays = (text: string): number[] => {
    const matches = text.match(/\[DELAY:(\d+)\]/g);
    if (!matches) return [];
    return matches.map(match => {
      const num = match.match(/\d+/);
      return num ? parseInt(num[0]) : 1000;
    });
  };

  const delays = extractDelays(mensagemTexto);

  // ✅ Efeito para mostrar partes progressivamente
  useEffect(() => {
    // Reset sempre que mensagem mudar
    setPartesVisiveis([]);

    if (partesMensagem.length === 0) {
      // Sem texto, só interface
      return;
    }

    if (temDelay && partesMensagem.length > 1) {
      // Mostrar primeira parte imediatamente
      setPartesVisiveis([partesMensagem[0]]);

      // Limpar timeouts anteriores (evitar duplicação)
      const timeouts: ReturnType<typeof setTimeout>[] = [];

      // Acumular delays para efeito cascata
      let delayAcumulado = 0;

      // Mostrar partes seguintes com delays reais do backend
      partesMensagem.slice(1).forEach((parte, index) => {
        const delayMs = delays[index] || 1000; // Fallback para 1000ms
        delayAcumulado += delayMs;

        const timeout = setTimeout(() => {
          setPartesVisiveis(prev => [...prev, parte]);
        }, delayAcumulado);

        timeouts.push(timeout);
      });

      // Cleanup: limpar timeouts quando componente desmontar ou mensagem mudar
      return () => {
        timeouts.forEach(t => clearTimeout(t));
      };
    } else {
      setPartesVisiveis(partesMensagem);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [message.id]);

  // ✅ Auto-scroll suave conforme partes vão aparecendo
  useEffect(() => {
    if (partesVisiveis.length > 0 && messageEndRef.current) {
      messageEndRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest'
      });
    }
  }, [partesVisiveis.length]);

  // Interface já vem como { tipo, dados } do helenaApi — só consumir
  const iface = typeof message.interface === 'object' ? message.interface : null;
  const tipoInterface = iface?.tipo;
  const dadosInterface = iface?.dados ?? null;
  const temInterfaceValida = !!tipoInterface;

  // ✅ VALIDAÇÃO 3: Verificar se tem badge nos metadados
  const temBadge = message.metadados?.badge && message.metadados.badge.mostrar_animacao;

  // ✅ Interface só aparece após última parte ser exibida
  const mostrarInterface = temInterfaceValida && (
    !temDelay || partesVisiveis.length === partesMensagem.length
  );

  return (
    <div className={`message-container ${message.tipo}`}>
      {/* Renderizar partes progressivamente */}
      {partesVisiveis.map((parte, index) => (
        <div
          key={index}
          className="message-wrapper progressive-message"
          style={{
            animation: 'fadeInUp 0.5s ease-out',
            animationFillMode: 'both'
          }}
        >
          {/* Avatar da Helena (só na primeira mensagem) */}
          {message.tipo === 'helena' && index === 0 && (
            <div className="message-avatar">
              <img
                src="/helena_mapeamento.png"
                alt="Helena"
                className="avatar-image"
              />
            </div>
          )}

          <div className={`message ${message.tipo} ${message.loading ? 'loading' : ''}`}>
            <ReactMarkdown>{parte}</ReactMarkdown>
          </div>
        </div>
      ))}

      {/* ✅ Ref para auto-scroll progressivo */}
      <div ref={messageEndRef} style={{ height: '1px' }} />

      {/* ✅ Badge animado (se vier nos metadados) */}
      {temBadge && (
        <BadgeTrofeu
          nomeBadge={message.metadados.badge.titulo}
          emoji={message.metadados.badge.emoji}
          descricao={message.metadados.badge.descricao}
          onContinuar={() => handleInterfaceResponse('continuar')}
        />
      )}

      {/* ✅ Interface só aparece após última parte */}
      {mostrarInterface && (
        <InterfaceDinamica
          interfaceData={{ tipo: tipoInterface!, dados: dadosInterface }}
          onRespond={handleInterfaceResponse}
        />
      )}
    </div>
  );
}

export default MessageBubble;
