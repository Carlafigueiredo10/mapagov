import './MessageBubble.css';
import './InterfaceDinamica.css';
import type { HelenaMessage } from '../../types/simples';
import InterfaceDinamica from './InterfaceDinamica';
import BadgeTrofeu from './BadgeTrofeu';
import { useChat } from '../../hooks/useChat';
import ReactMarkdown from 'react-markdown';
import { useState, useEffect } from 'react';

interface MessageBubbleProps {
  message: HelenaMessage;
}

function MessageBubble({ message }: MessageBubbleProps) {
  const { responderInterface } = useChat();
  const [partesVisiveis, setPartesVisiveis] = useState<string[]>([]);

  const handleInterfaceResponse = (resposta: string) => {
    responderInterface(resposta);
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

  // ✅ Efeito para mostrar partes progressivamente
  useEffect(() => {
    if (partesMensagem.length === 0) {
      // Sem texto, só interface
      setPartesVisiveis([]);
      return;
    }

    if (temDelay && partesMensagem.length > 1) {
      // Mostrar primeira parte imediatamente
      setPartesVisiveis([partesMensagem[0]]);

      // Mostrar partes seguintes com delay
      partesMensagem.slice(1).forEach((parte, index) => {
        setTimeout(() => {
          setPartesVisiveis(prev => [...prev, parte]);
        }, (index + 1) * 1000); // 1 segundo entre cada parte
      });
    } else {
      setPartesVisiveis(partesMensagem);
    }
  }, [mensagemTexto]);

  // ============================================================
  // 🔧 PATCH: Compatibilidade entre backend antigo e novo formato
  // ============================================================
  // Alguns retornos vêm com `interface: "sugestao_atividade"` (string)
  // enquanto outros usam `{ tipo: "sugestao_atividade", dados: {...} }` (objeto).
  // Este bloco garante compatibilidade entre ambos.
  // ============================================================

  const tipoInterface =
    typeof message.interface === 'string'
      ? message.interface
      : message.interface?.tipo;

  const dadosInterface =
    typeof message.interface === 'object'
      ? message.interface.dados
      : message.dados_interface || null;

  const temInterfaceValida = tipoInterface && tipoInterface.trim() !== '';

  // Debug: Ver o que está chegando
  if (message.interface) {
    console.log('📦 MessageBubble - Interface recebida:', {
      raw: message.interface,
      tipo: tipoInterface,
      dados: dadosInterface,
      valida: temInterfaceValida
    });
  }

  // ✅ VALIDAÇÃO 3: Verificar se tem badge nos metadados
  const temBadge = message.metadados?.badge && message.metadados.badge.mostrar_animacao;

  // ✅ Interface só aparece após última parte ser exibida
  const mostrarInterface = temInterfaceValida && (
    !temDelay || partesVisiveis.length === partesMensagem.length
  );

  // 🔍 DEBUG ROADTRIP: Log especial para interface roadtrip
  if (tipoInterface === 'roadtrip') {
    console.log('🚗 ROADTRIP DETECTADO!', {
      message,
      tipoInterface,
      dadosInterface,
      temInterfaceValida,
      mostrarInterface,
      partesVisiveis,
      partesMensagem
    });
  }

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
