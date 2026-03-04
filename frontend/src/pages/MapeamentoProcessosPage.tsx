/**
 * MapeamentoProcessosPage - Página dedicada para Mapeamento de Atividades (POP)
 *
 * Rota: /pop
 *
 * Fluxo:
 * 1. Exibe landing institucional (enquadramento)
 * 2. Ao clicar em "Iniciar mapeamento da atividade", exibe o chat + POP
 *
 * Layout responsivo:
 * - >= 1280px: Chat + POP lado a lado
 * - 1024–1279px: POP off-canvas colapsável
 * - < 1024px: POP como drawer fullscreen
 *
 * Modo Revisão Final: POP fullscreen com toolbar (Voltar | Salvar | Gerar PDF)
 */
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChatStore } from '../store/chatStore';
import type { DadosPOP } from '../store/chatStore';
import { useRequireAuth } from '../hooks/useRequireAuth';
import { X, FileText, ArrowLeft, Save, Download, AlertTriangle } from 'lucide-react';
import MapeamentoProcessosLanding from '../components/Helena/MapeamentoProcessosLanding';
import ChatContainer from '../components/Helena/ChatContainer';
import FormularioPOP from '../components/Helena/FormularioPOP';
import LandingShell from '../components/ui/LandingShell';
import { loadPOP, buscarMensagensV2 } from '../services/helenaApi';
import './MapeamentoProcessosPage.css';

const TODOS_CAMPOS = [
  'area', 'codigo_processo', 'macroprocesso', 'processo_especifico',
  'subprocesso', 'nome_processo', 'entrega_esperada', 'dispositivos_normativos',
  'sistemas', 'operadores', 'etapas',
  'fluxos_entrada', 'fluxos_saida', 'pontos_atencao'
] as const;

interface MapeamentoProcessosPageProps {
  startInChat?: boolean;
}

const MapeamentoProcessosPage: React.FC<MapeamentoProcessosPageProps> = ({ startInChat }) => {
  const navigate = useNavigate();
  const requireAuth = useRequireAuth();
  const [popAberto, setPopAberto] = useState(false);
  const [salvoFeedback, setSalvoFeedback] = useState(false);
  const [bannerDismissed, setBannerDismissed] = useState(false);

  const {
    dadosPOP, viewMode, setViewMode, fullscreenChat,
    resetChat, updateDadosPOP, setPopIdentifiers, setPopStatus, popStatus,
    carregarHistorico, setSessionId, resetForClone, addMessage,
  } = useChatStore();
  const modoRevisao = viewMode === 'final_review';

  // Se entrou via /pop/chat, garantir viewMode correto
  // (auth já é garantida pelo ProtectedRoute no App.tsx)
  useEffect(() => {
    if (startInChat && viewMode === 'landing') {
      setViewMode('chat_canvas');
    }
  }, [startInChat, viewMode, setViewMode]);

  // Contagem de campos preenchidos (mesma lógica de FormularioPOP)
  const camposPreenchidos = useMemo(() => {
    return TODOS_CAMPOS.filter(campo => {
      const valor = dadosPOP[campo as keyof typeof dadosPOP];
      if (Array.isArray(valor)) return valor.length > 0;
      if (typeof valor === 'object' && valor !== null) return Object.keys(valor).length > 0;
      return valor && String(valor).trim().length > 3;
    }).length;
  }, [dadosPOP]);


  // ESC fecha drawer ou sai do modo revisão
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (modoRevisao) {
          setViewMode('chat_canvas');
        } else if (popAberto) {
          setPopAberto(false);
        }
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [popAberto, modoRevisao, setViewMode]);

  // Focar no botão fechar ao abrir drawer
  useEffect(() => {
    if (popAberto) {
      const timer = setTimeout(() => {
        const closeBtn = document.querySelector('.mp-page__pop-fechar') as HTMLElement | null;
        closeBtn?.focus();
      }, 350);
      return () => clearTimeout(timer);
    }
  }, [popAberto]);

  // Body overflow lock quando drawer aberto
  useEffect(() => {
    document.body.style.overflow = popAberto ? 'hidden' : '';
    return () => { document.body.style.overflow = ''; };
  }, [popAberto]);

  // Gerar PDF via data-qa, com fallback por textContent
  const handleGerarPDF = useCallback(() => {
    let btn = document.querySelector('[data-qa="btn-gerar-pdf"]') as HTMLButtonElement | null;
    if (!btn) {
      const buttons = document.querySelectorAll('button');
      for (const b of buttons) {
        if (b.textContent?.toLowerCase().includes('gerar pdf')) {
          btn = b;
          break;
        }
      }
    }
    if (btn) {
      btn.click();
    } else {
      console.warn('[MapeamentoProcessosPage] Botão "Gerar PDF" não encontrado.');
    }
  }, []);

  // Salvar ajustes — feedback visual (dados já são salvos em tempo real)
  const handleSalvarAjustes = useCallback(() => {
    setSalvoFeedback(true);
    setTimeout(() => setSalvoFeedback(false), 2000);
  }, []);

  // --- Hub handlers ---

  // Criar novo POP: reset completo + sessão limpa
  const handleCriarNovo = useCallback(() => {
    if (!requireAuth()) return;
    resetChat();
    setViewMode('chat_canvas');
    navigate('/pop/chat');
  }, [requireAuth, resetChat, setViewMode, navigate]);

  // Retomar draft: carrega POP + histórico do backend
  const handleRetomar = useCallback(async (uuid: string) => {
    if (!requireAuth()) return;
    try {
      const result = await loadPOP(uuid);
      if (!result.success || !result.pop) {
        console.error('[MapeamentoProcessosPage] Erro ao carregar POP:', result.error);
        return;
      }
      const { pop } = result;

      // Restaurar identidade do documento no store
      setPopIdentifiers(pop.id, pop.uuid, pop.integrity_hash);
      setPopStatus(pop.status);
      updateDadosPOP(pop.dados as Partial<DadosPOP>);

      // Restaurar histórico de mensagens se houver sessão associada
      if (pop.session_id) {
        try {
          const hist = await buscarMensagensV2(pop.session_id);
          if (hist.mensagens?.length > 0) {
            carregarHistorico(hist.mensagens);
          }
        } catch {
          console.warn('[MapeamentoProcessosPage] Sem historico de mensagens para sessao:', pop.session_id);
        }
      }

      // Decidir viewMode com dados frescos do fetch (não do store)
      const dados = pop.dados as Record<string, unknown> | null;
      const etapas = dados?.etapas as unknown[] | undefined;
      const hasSubstantialData = dados?.nome_processo && dados?.area && Array.isArray(etapas) && etapas.length > 0;

      if (hasSubstantialData) {
        setViewMode('final_review');
      } else {
        setViewMode('chat_canvas');
      }
      navigate('/pop/chat');
    } catch (err) {
      console.error('[MapeamentoProcessosPage] Falha ao retomar POP:', err);
    }
  }, [requireAuth, setPopIdentifiers, setPopStatus, updateDadosPOP, carregarHistorico, setViewMode, navigate]);

  // Revisar POP publicado (stub — será implementado como view readonly)
  const handleRevisar = useCallback((uuid: string) => {
    if (!requireAuth()) return;
    console.info('[MapeamentoProcessosPage] Revisar POP:', uuid);
    // TODO: implementar view review_readonly
    navigate(`/pop?revisar=${uuid}`);
  }, [requireAuth, navigate]);

  // Ver versões (stub — será implementado como view version_history)
  const handleVerVersoes = useCallback((uuid: string) => {
    if (!requireAuth()) return;
    console.info('[MapeamentoProcessosPage] Ver versoes POP:', uuid);
    // TODO: implementar view version_history
    navigate(`/pop?versoes=${uuid}`);
  }, [requireAuth, navigate]);

  // Clonar POP: carrega dados clonados e abre revisao_final no chat
  const handleClonar = useCallback((popData: Record<string, unknown>) => {
    if (!requireAuth()) return;

    // Limpar estado de conversa (sem gerar novo sessionId)
    resetForClone();

    // Session_id do clone: fonte de verdade unica
    setSessionId(popData.session_id as string);

    // Identificadores
    setPopIdentifiers(
      popData.id as number,
      popData.uuid as string,
      (popData.integrity_hash as string) || '',
    );

    // Carregar dados no formato get_dados_completos()
    const dados = (popData.dados || {}) as Record<string, unknown>;
    updateDadosPOP(dados as Partial<DadosPOP>);
    setPopStatus('draft');

    // Construir mensagem sintetica com interface revisao_final
    const area = dados.area as { nome?: string } | undefined;
    const etapas = (dados.etapas || []) as unknown[];
    addMessage({
      id: `clone-revisao-${Date.now()}`,
      tipo: 'helena',
      mensagem: `Agora revise todos os dados do POP clonado. Você pode editar qualquer campo antes de gerar o documento final.`,
      timestamp: new Date().toISOString(),
      interface: {
        tipo: 'revisao_final',
        dados: {
          campos_bloqueados: {
            codigo_processo: (dados.codigo_processo as string) || '',
            area: area?.nome || (dados.area_nome as string) || '',
            macroprocesso: (dados.macroprocesso as string) || '',
            processo_especifico: (dados.processo_especifico as string) || '',
            subprocesso: (dados.subprocesso as string) || '',
            atividade: (dados.nome_processo as string) || '',
          },
          campos_editaveis_inline: {
            nome_processo: (dados.nome_processo as string) || '',
            entrega_esperada: (dados.entrega_esperada as string) || '',
            dispositivos_normativos: (dados.dispositivos_normativos as string) || '',
            pontos_atencao: (dados.pontos_atencao as string) || '',
          },
          campos_editaveis_secao: {
            sistemas: dados.sistemas || [],
            operadores: dados.operadores || [],
            fluxos_entrada: dados.fluxos_entrada || [],
            fluxos_saida: dados.fluxos_saida || [],
            etapas: etapas,
          },
          total_etapas: etapas.length,
        },
      },
    });

    setViewMode('chat_canvas');
    navigate('/pop/chat');
  }, [requireAuth, resetForClone, setSessionId, setPopIdentifiers, updateDadosPOP, setPopStatus, setViewMode, navigate, addMessage]);

  // Landing institucional (apenas em /pop, nunca em /pop/chat)
  if (!startInChat && viewMode === 'landing') {
    return (
      <LandingShell onBack={() => navigate('/')}>
        <MapeamentoProcessosLanding
          onIniciar={handleCriarNovo}
          onRetomar={handleRetomar}
          onRevisar={handleRevisar}
          onVerVersoes={handleVerVersoes}
          onClonar={handleClonar}
        />
      </LandingShell>
    );
  }

  // Chat + POP
  return (
    <div className={`mp-page${modoRevisao ? ' mp-page--revisao' : ''}${fullscreenChat && !modoRevisao ? ' mp-page--fullscreen-chat' : ''}`}>
      {/* Banner de revisão — só aparece quando POP está in_review */}
      {popStatus === 'in_review' && !bannerDismissed && (
        <div className="mp-page__review-banner">
          <AlertTriangle size={16} />
          <span>Você está revisando um POP do setor. Ao salvar, seu usuário ficará registrado como revisor.</span>
          <button
            type="button"
            className="mp-page__review-banner-close"
            onClick={() => setBannerDismissed(true)}
            aria-label="Fechar aviso"
          >
            <X size={14} />
          </button>
        </div>
      )}

      {/* Chat */}
      <div className="mp-page__chat">
        <ChatContainer />
      </div>

      {/* Toggle POP (medium/mobile) */}
      {!modoRevisao && (
        <button
          className="mp-page__toggle-pop"
          onClick={() => setPopAberto(true)}
          aria-label={`Abrir formulário POP (${camposPreenchidos}/${TODOS_CAMPOS.length} campos)`}
        >
          <FileText size={18} />
          <span>Ver POP</span>
          <span className="mp-page__toggle-badge">{camposPreenchidos}/{TODOS_CAMPOS.length}</span>
        </button>
      )}

      {/* Botão revisão removido — redundante com revisão final via chat */}

      {/* Overlay (medium/mobile, fecha ao clicar) */}
      {popAberto && !modoRevisao && (
        <div
          className="mp-page__overlay"
          onClick={() => setPopAberto(false)}
          aria-hidden="true"
        />
      )}

      {/* POP (instância única) */}
      <div className={`mp-page__pop${popAberto ? ' mp-page__pop--aberto' : ''}`}>
        {!modoRevisao && (
          <button
            className="mp-page__pop-fechar"
            onClick={() => setPopAberto(false)}
            aria-label="Fechar formulário POP"
          >
            <X size={20} />
          </button>
        )}
        <FormularioPOP />
      </div>

      {/* Toolbar modo revisão */}
      {modoRevisao && (
        <div className="mp-page__revisao-bar">
          <button
            className="mp-page__revisao-btn mp-page__revisao-btn--voltar"
            onClick={() => setViewMode('chat_canvas')}
          >
            <ArrowLeft size={16} />
            Voltar ao chat
          </button>
          <span className="mp-page__revisao-titulo">Revisão Final do POP</span>
          <div className="mp-page__revisao-acoes">
            <button
              className={`mp-page__revisao-btn mp-page__revisao-btn--salvar${salvoFeedback ? ' mp-page__revisao-btn--salvo' : ''}`}
              onClick={handleSalvarAjustes}
            >
              <Save size={16} />
              {salvoFeedback ? 'Salvo!' : 'Salvar ajustes'}
            </button>
            <button
              className="mp-page__revisao-btn mp-page__revisao-btn--pdf"
              onClick={handleGerarPDF}
            >
              <Download size={16} />
              Gerar PDF
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default MapeamentoProcessosPage;
