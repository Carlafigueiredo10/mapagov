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
import { X, FileText, ArrowLeft, Save, Download } from 'lucide-react';
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

  const {
    dadosPOP, viewMode, setViewMode, fullscreenChat,
    resetChat, updateDadosPOP, setPopIdentifiers, carregarHistorico,
  } = useChatStore();
  const modoRevisao = viewMode === 'final_review';

  // Se entrou via /pop/chat, garantir viewMode correto
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

      setViewMode('chat_canvas');
      navigate('/pop/chat');
    } catch (err) {
      console.error('[MapeamentoProcessosPage] Falha ao retomar POP:', err);
    }
  }, [requireAuth, setPopIdentifiers, updateDadosPOP, carregarHistorico, setViewMode, navigate]);

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

  // Landing institucional (apenas em /pop, nunca em /pop/chat)
  if (!startInChat && viewMode === 'landing') {
    return (
      <LandingShell onBack={() => navigate(-1)}>
        <MapeamentoProcessosLanding
          onIniciar={handleCriarNovo}
          onRetomar={handleRetomar}
          onRevisar={handleRevisar}
          onVerVersoes={handleVerVersoes}
        />
      </LandingShell>
    );
  }

  // Chat + POP
  return (
    <div className={`mp-page${modoRevisao ? ' mp-page--revisao' : ''}${fullscreenChat && !modoRevisao ? ' mp-page--fullscreen-chat' : ''}`}>
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
