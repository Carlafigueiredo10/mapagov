import React, { useState, useRef, useEffect } from 'react';
import { Send, Pencil, HelpCircle } from 'lucide-react';
import { CHAT_CMD } from '../../constants/chatCommands';
import MessageBubble from './MessageBubble';
import ErrorMessage from './ErrorMessage';

import { useChat } from '../../hooks/useChat';
import { useAutoSave } from '../../hooks/useAutoSave';
import { useSyncHistorico } from '../../hooks/useSyncHistorico';
import { useChatStore } from '../../store/chatStore';
import { loadPOP } from '../../services/helenaApi';
import './ChatContainer.css';

// ── Stepper: 5 macro-fases do POP ──────────────────────────────────
const FASES_POP = [
  { label: 'Identificação', key: 'identificacao' },
  { label: 'Classificação', key: 'classificacao' },
  { label: 'Estrutura',     key: 'estrutura' },
  { label: 'Etapas',        key: 'etapas' },
  { label: 'Consolidação',  key: 'consolidacao' },
] as const;

const ESTADO_PARA_FASE: Record<string, number> = {
  // 0 — Identificação
  nome_usuario: 0,
  escolha_tipo_explicacao: 0,
  explicacao_longa: 0,
  duvidas_explicacao: 0,
  explicacao: 0,
  pedido_compromisso: 0,
  // 1 — Classificação
  area_decipex: 1,
  subarea_decipex: 1,
  arquitetura: 1,
  confirmacao_arquitetura: 1,
  selecao_hierarquica: 1,
  nome_processo: 1,
  entrega_esperada: 1,
  confirmacao_entrega: 1,
  reconhecimento_entrega: 1,
  // 2 — Estrutura
  dispositivos_normativos: 2,
  transicao_roadtrip: 2,
  operadores: 2,
  sistemas: 2,
  fluxos: 2,
  pontos_atencao: 2,
  revisao_pre_delegacao: 2,
  transicao_epica: 2,
  selecao_edicao: 2,
  // 3 — Etapas
  delegacao_etapas: 3,
  etapa_form: 3,
  etapa_descricao: 3,
  etapa_operador: 3,
  etapa_sistemas: 3,
  etapa_docs_requeridos: 3,
  etapa_docs_gerados: 3,
  etapa_tempo: 3,
  etapa_condicional: 3,
  etapa_tipo_condicional: 3,
  etapa_antes_decisao: 3,
  etapa_cenarios: 3,
  etapa_subetapas_cenario: 3,
  etapa_detalhes: 3,
  etapa_mais: 3,
  etapa_revisao: 3,
  // 4 — Consolidação
  revisao_final: 4,
  finalizado: 4,
};

function getFaseAtual(estadoAtual: string): number {
  return ESTADO_PARA_FASE[estadoAtual] ?? 0;
}

interface ChatContainerProps {
  className?: string;
}

const ChatContainer: React.FC<ChatContainerProps> = ({ className = '' }) => {
  const [inputValue, setInputValue] = useState('');
  const [saveStatus, setSaveStatus] = useState<'salvando' | 'salvo' | 'erro' | 'idle'>('idle');
  const [ultimoSalvamento, setUltimoSalvamento] = useState<Date | undefined>(undefined);
  const [mostrarSeta, setMostrarSeta] = useState(false);
  const [conflictDetected, setConflictDetected] = useState(false);
  const [editandoNome, setEditandoNome] = useState(false);
  const [nomeTemp, setNomeTemp] = useState('');
  const nomeInputRef = useRef<HTMLInputElement>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-save automático com callback para atualizar status
  const handleAutoSave = async () => {
    setSaveStatus('salvando');
    const result = await saveNow();

    if (result.success) {
      setSaveStatus('salvo');
      setUltimoSalvamento(new Date());
      setTimeout(() => setSaveStatus('idle'), 3000);
    } else if ((result as { conflict?: boolean }).conflict) {
      setConflictDetected(true);
      setSaveStatus('erro');
    } else {
      setSaveStatus('erro');
      setTimeout(() => setSaveStatus('idle'), 5000);
    }
  };

  // Recarregar dados do servidor após conflito
  const reloadFromServer = async () => {
    const { popUuid, popId: pid, sessionId: sid, updateDadosPOP, setPopIdentifiers } = useChatStore.getState();
    const identifier = popUuid || pid?.toString() || sid;
    if (!identifier) return;

    try {
      const res = await loadPOP(identifier);
      if (res.success && res.pop) {
        updateDadosPOP(res.pop.dados as Record<string, unknown>);
        setPopIdentifiers(res.pop.id, res.pop.uuid, res.pop.integrity_hash);
        setConflictDetected(false);
        setSaveStatus('idle');
      }
    } catch {
      // fallback: manter estado local
    }
  };

  const {
    messages,
    isProcessing,
    error,
    dadosPOP,
    enviarMensagem,
    clearError,
  } = useChat(handleAutoSave);

  const { updateDadosPOP, estadoAtual, modoAjudaAtivo } = useChatStore();
  const nomeUsuario = dadosPOP.nome_usuario || '';

  // Abrir edição inline do nome
  const iniciarEdicaoNome = () => {
    setNomeTemp(nomeUsuario);
    setEditandoNome(true);
    setTimeout(() => nomeInputRef.current?.focus(), 50);
  };

  // Confirmar edição do nome
  const confirmarNome = () => {
    const novoNome = nomeTemp.trim();
    if (novoNome && novoNome !== nomeUsuario) {
      updateDadosPOP({ nome_usuario: novoNome });
    }
    setEditandoNome(false);
  };

  // Sincronizar histórico ao montar componente
  useSyncHistorico();

  // Carregar POP do backend ao montar (backend é fonte de verdade)
  useEffect(() => {
    const { popUuid, popId, sessionId: sid, updateDadosPOP, setPopIdentifiers } = useChatStore.getState();
    const identifier = popUuid || popId?.toString() || sid;
    if (!identifier) return;

    loadPOP(identifier)
      .then((res) => {
        if (res.success && res.pop) {
          const serverSeq = res.pop.autosave_sequence ?? 0;
          const localSeq = useChatStore.getState().popId ? 0 : -1; // se nao tem popId local, backend vence
          if (serverSeq > localSeq || !useChatStore.getState().popId) {
            updateDadosPOP(res.pop.dados as Record<string, unknown>);
            setPopIdentifiers(res.pop.id, res.pop.uuid, res.pop.integrity_hash);
          }
        }
      })
      .catch(() => {
        // 404 = POP ainda nao existe no backend (primeiro acesso), manter dados locais
      });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Auto-save automático
  const { saveNow } = useAutoSave({ interval: 30000, enabled: true });

  // Auto-scroll inteligente: se última mensagem tem interface, rola para o início da mensagem
  useEffect(() => {
    if (messages.length === 0) return;

    const ultimaMensagem = messages[messages.length - 1];

    // Se a última mensagem da Helena tem interface, rolar para o início da mensagem (não para o final)
    if (ultimaMensagem.tipo === 'helena' && ultimaMensagem.interface) {
      // Pequeno delay para garantir que o DOM foi renderizado
      setTimeout(() => {
        const messageElements = document.querySelectorAll('.message-container.helena');
        const ultimoElemento = messageElements[messageElements.length - 1];

        if (ultimoElemento) {
          ultimoElemento.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);
    } else {
      // Mensagens normais: scroll para o final
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Focar input quando não está processando
  useEffect(() => {
    if (!isProcessing && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isProcessing]);

  // Mostrar seta quando mensagem sobre POP aparecer
  useEffect(() => {
    const temMensagemPOP = messages.some(msg =>
      msg.tipo === 'helena' && msg.mensagem.includes('formulário de Procedimento Operacional Padrão - POP')
    );

    if (temMensagemPOP) {
      setMostrarSeta(true);
      // Esconde a seta após 8 segundos
      const timer = setTimeout(() => setMostrarSeta(false), 8000);
      return () => clearTimeout(timer);
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!inputValue.trim() || isProcessing) return;

    const texto = inputValue.trim();
    setInputValue('');
    
    try {
      await enviarMensagem(texto);
    } catch (err) {
      console.error('Erro ao enviar mensagem:', err);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      // Trigger submit manually
      if (!inputValue.trim() || isProcessing) return;
      const texto = inputValue.trim();
      setInputValue('');
      enviarMensagem(texto);
    }
  };

  const reiniciarConversa = () => {
    if (confirm('Tem certeza que deseja iniciar um novo mapeamento? Isso irá limpar a conversa atual.')) {
      // Reset completo da conversa
      const { resetChat } = useChatStore.getState();
      resetChat();
      setInputValue('');

      // Limpa qualquer estado persistido no localStorage
      localStorage.removeItem('chat-storage');

      // Recarrega na rota do chat para garantir limpeza total
      window.location.href = '/pop/chat';
    }
  };


  // Detectar se a última mensagem da Helena tem interface que espera clique (não texto)
  const interfaceBloqueiaInput = (() => {
    // Modo ajuda ativo: input NUNCA bloqueia
    if (modoAjudaAtivo) return false;
    if (messages.length === 0) return false;
    const ultima = messages[messages.length - 1];
    if (ultima.tipo !== 'helena') return false;
    const iface = typeof ultima.interface === 'object' ? ultima.interface : null;
    if (!iface?.tipo) return false;
    // Tipos que esperam digitação no input do chat — liberar
    const tiposPermitemDigitacao = ['texto_livre', 'texto_com_exemplos', 'texto'];
    return !tiposPermitemDigitacao.includes(iface.tipo);
  })();

  const handleSalvarManual = async () => {
    setSaveStatus('salvando');
    const result = await saveNow();
    if (result.success) {
      setSaveStatus('salvo');
      setUltimoSalvamento(new Date());
      setTimeout(() => setSaveStatus('idle'), 3000);
    } else {
      setSaveStatus('erro');
      setTimeout(() => setSaveStatus('idle'), 5000);
    }
  };

  return (
    <div className={`chat-container ${className}`}>
      {/* Header */}
      <div className="chat-header-pop">
        {/* Botões removidos do banner para reduzir altura */}

        <div className="header-content">
          <h2>POP — Mapeamento de Procedimento Operacional</h2>
          <div className="header-meta-line" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', flexWrap: 'wrap', fontSize: '13px', opacity: 0.9, padding: '0 16px' }}>
            {nomeUsuario && (
              <span className="header-meta-item">
                <span className="meta-label">Responsável:</span>
                {editandoNome ? (
                  <input
                    ref={nomeInputRef}
                    type="text"
                    value={nomeTemp}
                    onChange={(e) => setNomeTemp(e.target.value)}
                    onBlur={confirmarNome}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') confirmarNome();
                      if (e.key === 'Escape') setEditandoNome(false);
                    }}
                    className="nome-usuario-input"
                    maxLength={40}
                  />
                ) : (
                  <span
                    className="nome-usuario-label"
                    onClick={iniciarEdicaoNome}
                    title="Clique para alterar seu nome"
                  >
                    {nomeUsuario} <Pencil size={12} />
                  </span>
                )}
              </span>
            )}
            {dadosPOP.codigo_cap && (
              <span className="header-meta-item">
                <span className="meta-label">Código CAP:</span>
                <span>{dadosPOP.codigo_cap}</span>
              </span>
            )}
          </div>
        </div>

        {/* Progresso removido do banner — já aparece no FormularioPOP lateral */}
      </div>

      {/* Stepper: 5 macro-fases */}
      {(() => {
        const faseIdx = getFaseAtual(estadoAtual);
        return (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0',
            padding: '8px 16px',
            background: '#f8f9fa',
            borderBottom: '1px solid #e0e0e0',
            overflowX: 'auto',
            whiteSpace: 'nowrap',
          }}>
            {FASES_POP.map((fase, idx) => {
              const isCompleted = idx < faseIdx;
              const isActive = idx === faseIdx;
              return (
                <React.Fragment key={fase.key}>
                  {idx > 0 && (
                    <div style={{
                      width: '24px',
                      height: '2px',
                      background: isCompleted || isActive ? '#1351B4' : '#ccc',
                      flexShrink: 0,
                    }} />
                  )}
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '5px',
                    flexShrink: 0,
                  }}>
                    <div style={{
                      width: '18px',
                      height: '18px',
                      borderRadius: '50%',
                      background: isCompleted ? '#1351B4' : isActive ? '#1351B4' : '#ccc',
                      border: isActive ? '2px solid #1351B4' : 'none',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '10px',
                      color: '#fff',
                      fontWeight: 600,
                      boxShadow: isActive ? '0 0 0 3px rgba(19,81,180,0.2)' : 'none',
                    }}>
                      {isCompleted ? '✓' : idx + 1}
                    </div>
                    <span style={{
                      fontSize: '12px',
                      fontWeight: isActive ? 600 : 400,
                      color: isCompleted ? '#1351B4' : isActive ? '#1351B4' : '#888',
                    }}>
                      {fase.label}
                    </span>
                  </div>
                </React.Fragment>
              );
            })}
          </div>
        );
      })()}

      {/* Banner de conflito */}
      {conflictDetected && (
        <div style={{
          background: '#fff3cd',
          border: '1px solid #ffc107',
          borderRadius: '6px',
          padding: '10px 16px',
          margin: '8px 12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '13px',
          color: '#664d03',
        }}>
          <span>Este POP foi modificado em outra aba.</span>
          <button
            onClick={reloadFromServer}
            style={{
              background: '#ffc107',
              border: 'none',
              borderRadius: '4px',
              padding: '4px 12px',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '13px',
            }}
          >
            Recarregar dados
          </button>
        </div>
      )}

      {/* Messages Area */}
      <div className="messages-area">
        {/* ✅ FIX DUPLICAÇÃO: Removido fallback hardcoded */}
        {/* useSyncHistorico já injeta a mensagem no store */}
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        
        {error && (
          <ErrorMessage 
            message={error}
            onClose={clearError}
            type="error"
          />
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Section */}
      <form onSubmit={handleSubmit} className="input-section">
        <div className="input-group">
          {/* Botão Ajuda / Voltar ao mapeamento */}
          {messages.length > 0 && (
            <button
              type="button"
              onClick={() => {
                const cmd = modoAjudaAtivo ? CHAT_CMD.SAIR_DUVIDAS : CHAT_CMD.ENTRAR_DUVIDAS;
                enviarMensagem(cmd, 'gerador_pop', false);
              }}
              disabled={isProcessing}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                padding: '8px 14px',
                border: modoAjudaAtivo ? '1px solid #1351B4' : '1px solid #ccc',
                borderRadius: '20px',
                background: modoAjudaAtivo ? '#1351B4' : 'transparent',
                color: modoAjudaAtivo ? '#fff' : '#1351B4',
                cursor: isProcessing ? 'not-allowed' : 'pointer',
                fontSize: '13px',
                fontWeight: 600,
                whiteSpace: 'nowrap',
                opacity: isProcessing ? 0.5 : 1,
                transition: 'all 0.2s ease',
                flexShrink: 0,
              }}
              title={modoAjudaAtivo ? 'Sair do modo ajuda e voltar ao mapeamento' : 'Tirar dúvidas com a Helena'}
            >
              {modoAjudaAtivo ? (
                <span>Voltar ao mapeamento</span>
              ) : (
                <>
                  <HelpCircle size={15} />
                  <span>Ajuda</span>
                </>
              )}
            </button>
          )}

          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              modoAjudaAtivo
                ? "Escreva sua dúvida..."
                : interfaceBloqueiaInput
                  ? "Use os botões acima para responder"
                  : "Digite sua mensagem..."
            }
            maxLength={2000}
            disabled={isProcessing || interfaceBloqueiaInput}
            className="message-input"
          />

          <button
            type="submit"
            disabled={isProcessing || interfaceBloqueiaInput || !inputValue.trim()}
            className="send-button"
            key={isProcessing ? 'processing' : 'idle'}
          >
            {isProcessing ? (
              <>
                <span className="loading-spinner" />
                <span>Enviando...</span>
              </>
            ) : (
              <>
                <Send size={18} />
                <span>Enviar</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Seta Animada apontando para o POP */}
      {mostrarSeta && (
        <div className="arrow-to-pop">
          ➡️
        </div>
      )}
    </div>
  );
};

export default ChatContainer;