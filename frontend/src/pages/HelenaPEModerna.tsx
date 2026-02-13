/**
 * Helena PE Moderna - Versão Funcional COMPLETA (Fase 2)
 *
 * Interface moderna com gradiente roxo e glassmorphism
 * INTEGRAÇÃO COMPLETA com backend via API
 */

import React, { useState, useEffect, useRef, CSSProperties } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Button from '../components/ui/Button';
import helenaPEService from '../services/helenaPESimples';
import { WorkspaceSWOT } from '../components/Helena/workspaces/WorkspaceSWOT';
import { WorkspaceOKR } from '../components/Helena/workspaces/WorkspaceOKR';
import { WorkspaceBSC } from '../components/Helena/workspaces/WorkspaceBSC';
import { Workspace5W2H } from '../components/Helena/workspaces/Workspace5W2H';
import { WorkspaceHoshin } from '../components/Helena/workspaces/WorkspaceHoshin';
import { ModeloInfoDrawer } from '../components/Helena/ModeloInfoDrawer';
import { MessageBubbleRich } from '../components/Helena/MessageBubbleRich';
import { PEDiagnostico } from '../components/Helena/PEDiagnostico';
import { PEModeloGrid } from '../components/Helena/PEModeloGrid';
import { PEChatIntro } from '../components/Helena/PEChatIntro';
import DashboardCard from '../components/Helena/DashboardCard';
import DashboardAreas from '../components/Helena/DashboardAreas';
import DashboardDiretor from '../components/Helena/DashboardDiretor';
import PlanejamentoLanding from '../components/Helena/PlanejamentoLanding';
import { useDashboard } from '../hooks/useDashboard';
import { sessionManager } from '../utils/sessionManager';
import type { EstadoFluxo, Mensagem, SessionData, ModeloPlanejamento, PerguntaDiagnostico } from '../types/planejamento';
import modelosData from '../data/modelosPlanejamento.json';
import perguntasData from '../data/perguntasDiagnostico.json';

// Importados de arquivos JSON externos
const PERGUNTAS_DIAGNOSTICO: PerguntaDiagnostico[] = perguntasData;
const MODELOS = modelosData as Record<string, ModeloPlanejamento>;

export const HelenaPEModerna: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [estado, setEstado] = useState<EstadoFluxo>('inicial');
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [inputTexto, setInputTexto] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionData, setSessionData] = useState<SessionData | null>(null);
  const [modeloSelecionado, setModeloSelecionado] = useState<string | null>(null);
  const [perguntaAtual, setPerguntaAtual] = useState(0);
  const [respostasDiagnostico, setRespostasDiagnostico] = useState<Record<string, string>>({});
  const [workspaceVisivel, setWorkspaceVisivel] = useState(false);
  const [dadosWorkspace, setDadosWorkspace] = useState<any>(null);
  const [modalInfoAberto, setModalInfoAberto] = useState(false);
  const [modeloInfoAtual, setModeloInfoAtual] = useState<string | null>(null);
  const [dashboardAberto, setDashboardAberto] = useState<'areas' | 'diretor' | null>(null);
  const [aguardandoConfirmacao, setAguardandoConfirmacao] = useState(false);
  const [mostrarCardIntro, setMostrarCardIntro] = useState(false); // 🆕 Card de intro fixo
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Mapeamento de ID do modelo para rota (hierarquia organizada)
  const modeloParaRota: Record<string, string> = {
    'tradicional': '/planejamento-estrategico/modelos/tradicional',
    'bsc': '/planejamento-estrategico/modelos/bsc',
    'okr': '/metodos/okr',
    'swot': '/planejamento-estrategico/modelos/swot',
    'cenarios': '/planejamento-estrategico/modelos/cenarios',
    '5w2h': '/planejamento-estrategico/modelos/5w2h',
    'hoshin': '/metodos/hoshin'
  };

  // Hook do Dashboard
  const {
    projetos,
    pedidos,
    estatisticas,
    adicionarProjeto,
    atualizarProjeto
  } = useDashboard();

  // Auto-scroll no chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [mensagens]);

  // 🔧 Persistência de sessão - carrega dados ao montar
  useEffect(() => {
    const savedSession = sessionManager.loadSession();
    const savedMessages = sessionManager.loadMessages();

    if (savedSession) {
      setSessionData(savedSession);
      console.log('[Session] Sessão recuperada:', savedSession.session_id);
    }

    if (savedMessages.length > 0) {
      setMensagens(savedMessages);
      console.log('[Session] Mensagens recuperadas:', savedMessages.length);
    }
  }, []);

  // 🔧 Persistência de sessão - salva sessionData quando muda
  useEffect(() => {
    if (sessionData) {
      sessionManager.saveSession(sessionData);
    }
  }, [sessionData]);

  // 🔧 Persistência de sessão - salva mensagens quando mudam
  useEffect(() => {
    if (mensagens.length > 0) {
      sessionManager.saveMessages(mensagens);
    }
  }, [mensagens]);

  // 🔧 Sincronização URL → Estado (URL é a fonte da verdade)
  useEffect(() => {
    const p = location.pathname;

    // 1) Home - rota raiz
    if (p === '/planejamento-estrategico') {
      setEstado('inicial');
      setModeloSelecionado(null);
      setWorkspaceVisivel(false);
      setMostrarCardIntro(false);
      setAguardandoConfirmacao(false);
      return;
    }

    // 2) Painel (dashboard)
    if (p === '/planejamento-estrategico/painel') {
      setEstado('painel');
      setModeloSelecionado(null);
      setWorkspaceVisivel(false);
      setMostrarCardIntro(false);
      return;
    }

    // 3) Diagnóstico
    if (p === '/planejamento-estrategico/diagnostico') {
      setEstado('diagnostico');
      setModeloSelecionado(null);
      setWorkspaceVisivel(false);
      setMostrarCardIntro(false);
      return;
    }

    // 3) Lista de modelos
    if (p === '/planejamento-estrategico/modelos') {
      setEstado('modelos');
      setModeloSelecionado(null);
      setWorkspaceVisivel(false);
      setMostrarCardIntro(false);
      return;
    }

    // 4) Rotas de modelo → chat
    const rotaParaModelo: Record<string, string> = {
      '/planejamento-estrategico/modelos/tradicional': 'tradicional',
      '/planejamento-estrategico/modelos/bsc': 'bsc',
      '/metodos/okr': 'okr',
      '/planejamento-estrategico/modelos/swot': 'swot',
      '/planejamento-estrategico/modelos/cenarios': 'cenarios',
      '/planejamento-estrategico/modelos/5w2h': '5w2h',
      '/metodos/hoshin': 'hoshin'
    };

    const modeloId = rotaParaModelo[p];
    if (modeloId) {
      setEstado('chat');
      setModeloSelecionado(modeloId);
      setWorkspaceVisivel(true);
      return;
    }

    // 5) Fallback seguro (qualquer outra rota)
    setEstado('inicial');
    setModeloSelecionado(null);
    setWorkspaceVisivel(false);
    setMostrarCardIntro(false);
  }, [location.pathname]); // IMPORTANTE: só pathname, sem estado/modeloSelecionado

  // Adiciona mensagem ao histórico
  const adicionarMensagem = (tipo: 'user' | 'helena', texto: string) => {
    setMensagens((prev) => [...prev, { tipo, texto }]);
  };

  // Responde pergunta do diagnóstico
  const responderPerguntaDiagnostico = async (opcaoSelecionada: string) => {
    const pergunta = PERGUNTAS_DIAGNOSTICO[perguntaAtual];

    // Salva resposta
    const novasRespostas = {
      ...respostasDiagnostico,
      [pergunta.id]: opcaoSelecionada
    };
    setRespostasDiagnostico(novasRespostas);

    // Se ainda há perguntas, avança
    if (perguntaAtual < PERGUNTAS_DIAGNOSTICO.length - 1) {
      setPerguntaAtual(perguntaAtual + 1);
    } else {
      // Finaliza diagnóstico e envia para backend
      try {
        setLoading(true);

        // Inicia sessão
        const response = await helenaPEService.iniciarSessao();
        setSessionData(response.session_data);

        // Envia que quer fazer diagnóstico
        const respDiag = await helenaPEService.enviarMensagem('Quero fazer o diagnóstico');
        setSessionData(respDiag.session_data);

        // Envia respostas sequencialmente
        for (let i = 0; i < PERGUNTAS_DIAGNOSTICO.length; i++) {
          const pergId = PERGUNTAS_DIAGNOSTICO[i].id;
          const resposta = novasRespostas[pergId];
          const opcao = PERGUNTAS_DIAGNOSTICO[i].opcoes.find(o => o.valor === resposta);

          if (opcao) {
            const resp = await helenaPEService.enviarMensagem(opcao.texto);
            setSessionData(resp.session_data);

            // Na última resposta, adiciona a recomendação ao chat
            if (i === PERGUNTAS_DIAGNOSTICO.length - 1) {
              adicionarMensagem('helena', resp.resposta);
            }
          }
        }

        setEstado('modelos');
      } catch (error) {
        console.error('Erro ao processar diagnóstico:', error);
        adicionarMensagem('helena', '⚠️ Não consegui processar o diagnóstico agora. Tente novamente em alguns segundos.');
        setEstado('inicial');
      } finally {
        setLoading(false);
      }
    }
  };

  // Inicia sessão e seleciona modelo
  const selecionarModelo = async (modeloId: string) => {
    // Guard: evita múltiplas chamadas simultâneas
    if (loading) {
      console.log('[Helena PE] Já está carregando, ignorando chamada duplicada');
      return;
    }

    // 🆕 NOVO FLUXO: Mostra card de introdução fixo (NÃO chama backend ainda)
    setModeloSelecionado(modeloId);
    setEstado('chat');
    setWorkspaceVisivel(true);
    setMostrarCardIntro(true); // Ativa card de intro

    // Navega para a rota específica do modelo
    const rota = modeloParaRota[modeloId];
    if (rota) {
      navigate(rota);
    }
  };

  // Inicia agente diretamente (sem confirmação)
  const iniciarAgente = async () => {
    if (!modeloSelecionado) return;

    try {
      setLoading(true);
      setMostrarCardIntro(false);

      try {
        const confirmacao = await helenaPEService.iniciarModeloDireto(modeloSelecionado);
        setSessionData(confirmacao.session_data);

        const response = await helenaPEService.confirmarModelo(confirmacao.session_data);
        setSessionData(response.session_data);

        adicionarMensagem('helena', response.resposta);
      } catch (backendError) {
        console.warn('Backend não disponível, mas workspace continua funcionando:', backendError);
        adicionarMensagem('helena', `Olá! Vou te ajudar a construir seu ${MODELOS[modeloSelecionado as keyof typeof MODELOS].nome}.\n\n⚠️ O servidor está offline, mas você pode usar o workspace ao lado para começar a estruturar seu planejamento.`);
      }
    } catch (error) {
      console.error('Erro ao iniciar agente:', error);
      adicionarMensagem('helena', '⚠️ Erro ao iniciar o agente. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  // Inicia agente e pede exemplos
  const verExemplos = async () => {
    if (!modeloSelecionado) return;
    setMostrarCardIntro(false);
    try {
      const confirmacao = await helenaPEService.iniciarModeloDireto(modeloSelecionado);
      setSessionData(confirmacao.session_data);
      adicionarMensagem('helena', '**Vou te mostrar alguns exemplos práticos de como este método funciona.**');
      adicionarMensagem('user', 'Me mostre exemplos');
      const response = await helenaPEService.confirmarModelo(confirmacao.session_data);
      setSessionData(response.session_data);
      await new Promise(resolve => setTimeout(resolve, 300));
      const respExemplos = await helenaPEService.enviarMensagem('exemplos', response.session_data);
      setSessionData(respExemplos.session_data);
      adicionarMensagem('helena', respExemplos.resposta);
    } catch (error) {
      console.error('Erro ao mostrar exemplos:', error);
      adicionarMensagem('helena', '⚠️ Erro ao carregar exemplos. Tente novamente.');
    }
  };

  // Inicia agente e explica o método
  const entenderMetodo = async () => {
    if (!modeloSelecionado) return;
    setMostrarCardIntro(false);
    try {
      const confirmacao = await helenaPEService.iniciarModeloDireto(modeloSelecionado);
      setSessionData(confirmacao.session_data);
      adicionarMensagem('helena', '**Vou te explicar como este método funciona.**');
      adicionarMensagem('user', 'Como funciona este método?');
      const response = await helenaPEService.confirmarModelo(confirmacao.session_data);
      setSessionData(response.session_data);
      await new Promise(resolve => setTimeout(resolve, 300));
      const respAjuda = await helenaPEService.enviarMensagem('o que é ' + modeloSelecionado, response.session_data);
      setSessionData(respAjuda.session_data);
      adicionarMensagem('helena', respAjuda.resposta);
    } catch (error) {
      console.error('Erro ao explicar método:', error);
      adicionarMensagem('helena', '⚠️ Erro ao carregar explicação. Tente novamente.');
    }
  };

  // Confirma modelo e inicia agente
  const confirmarModeloSelecionado = async () => {
    if (!sessionData) return;

    try {
      setLoading(true);

      // Chama endpoint de confirmação
      const response = await helenaPEService.confirmarModelo(sessionData);
      setSessionData(response.session_data);

      // Adiciona primeira pergunta do agente
      adicionarMensagem('helena', response.resposta);
    } catch (error) {
      console.error('Erro ao confirmar modelo:', error);
      adicionarMensagem('helena', '⚠️ Erro ao iniciar o agente. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  // Envia mensagem do usuário
  const enviarMensagem = async () => {
    if (!inputTexto.trim() || loading) return;

    const texto = inputTexto.trim();
    setInputTexto('');
    adicionarMensagem('user', texto);

    try {
      setLoading(true);
      const response = await helenaPEService.enviarMensagem(texto, sessionData || undefined);
      setSessionData(response.session_data);
      adicionarMensagem('helena', response.resposta);
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      adicionarMensagem('helena', 'Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const containerStyle: CSSProperties = {
    minHeight: '100vh',
    background: estado === 'inicial' ? '#FFFFFF' : 'linear-gradient(135deg, #f8fbff 0%, #e8f4fd 100%)',
    color: '#2C3E50',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: estado === 'inicial' ? 'flex-start' : 'center',
    padding: estado === 'inicial' ? '0' : '40px 20px',
    position: 'relative',
    overflow: 'hidden'
  };

  const fundoStyle: CSSProperties = {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    opacity: 0.05,
    pointerEvents: 'none',
    background: `
      radial-gradient(circle at 20% 50%, rgba(27, 79, 114, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 80% 80%, rgba(52, 152, 219, 0.1) 0%, transparent 50%)
    `
  };

  const renderInicial = () => (
    <PlanejamentoLanding
      onIniciar={() => navigate('/planejamento-estrategico/painel')}
    />
  );

  const renderPainel = () => (
    <div style={{ maxWidth: '1200px', width: '100%', zIndex: 1 }}>
      <div style={{ marginBottom: '24px' }}>
        <Button
          variant="outline"
          onClick={() => navigate('/planejamento-estrategico')}
          size="sm"
        >
          ← Voltar
        </Button>
      </div>
      <div style={{ marginBottom: '48px' }}>
        <DashboardCard
          onAbrirDashboardAreas={() => setDashboardAberto('areas')}
          onAbrirDashboardDiretor={() => setDashboardAberto('diretor')}
          onIniciarDiagnostico={() => navigate('/planejamento-estrategico/diagnostico')}
          onExplorarModelos={() => navigate('/planejamento-estrategico/modelos')}
          onEscolhaDireta={() => navigate('/planejamento-estrategico/modelos')}
          navigate={navigate}
          estatisticas={estatisticas ? {
            total_projetos: estatisticas.total_projetos,
            total_pedidos: estatisticas.total_pedidos,
            pedidos_atrasados: estatisticas.pedidos_atrasados
          } : undefined}
        />
      </div>
    </div>
  );

  const renderDiagnostico = () => (
    <PEDiagnostico
      perguntas={PERGUNTAS_DIAGNOSTICO}
      perguntaAtual={perguntaAtual}
      loading={loading}
      onResponder={responderPerguntaDiagnostico}
      onCancelar={() => {
        setPerguntaAtual(0);
        setRespostasDiagnostico({});
        navigate('/planejamento-estrategico');
      }}
    />
  );

  const renderModelos = () => (
    <PEModeloGrid
      modelos={MODELOS}
      loading={loading}
      onSelecionarModelo={selecionarModelo}
      onAbrirInfo={(modeloId) => {
        setModeloInfoAtual(modeloId);
        setModalInfoAberto(true);
      }}
      onVoltar={() => navigate('/planejamento-estrategico')}
    />
  );

  const renderWorkspace = () => {
    if (!modeloSelecionado) return null;

    const handleSalvarWorkspace = (dados: any) => {
      setDadosWorkspace(dados);
      console.log('Dados do workspace salvos:', dados);
      // Aqui você pode enviar para o backend futuramente
    };

    switch (modeloSelecionado) {
      case 'swot':
        return <WorkspaceSWOT dados={dadosWorkspace} onSalvar={handleSalvarWorkspace} />;
      case 'okr':
        return <WorkspaceOKR dados={dadosWorkspace} onSalvar={handleSalvarWorkspace} />;
      case 'bsc':
        return <WorkspaceBSC dados={dadosWorkspace} onSalvar={handleSalvarWorkspace} />;
      case '5w2h':
        return <Workspace5W2H dados={dadosWorkspace} onSalvar={handleSalvarWorkspace} />;
      case 'hoshin':
        return <WorkspaceHoshin onSalvar={handleSalvarWorkspace} />;
      default:
        return (
          <div style={{
            padding: '40px',
            textAlign: 'center',
            color: '#6b7280'
          }}>
            <p style={{ fontSize: '16px', marginBottom: '8px' }}>
              Workspace visual em desenvolvimento para este modelo.
            </p>
            <p style={{ fontSize: '14px' }}>
              Continue conversando com a Helena para construir seu planejamento.
            </p>
          </div>
        );
    }
  };

  const renderChat = () => {
    const modelo = modeloSelecionado ? MODELOS[modeloSelecionado as keyof typeof MODELOS] : null;

    return (
      <div style={{
        maxWidth: workspaceVisivel ? '95vw' : '1000px',
        width: '100%',
        height: '100vh',
        display: 'flex',
        flexDirection: 'row',
        gap: '20px',
        zIndex: 1,
        padding: '20px',
        transition: 'max-width 0.3s ease'
      }}>
        {/* Coluna do Chat */}
        <div style={{
          flex: workspaceVisivel ? '0 0 450px' : 1,
          display: 'flex',
          flexDirection: 'column',
          transition: 'flex 0.3s ease'
        }}>
          {/* Header */}
          <div style={{
            padding: '20px',
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
            borderRadius: '16px 16px 0 0',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderBottom: 'none',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div style={{ fontSize: '48px' }}>{modelo?.icone || '🧭'}</div>
              <div>
                <h2 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>
                  {modelo?.nome || 'Planejamento Estratégico'}
                </h2>
                {sessionData && (
                  <div style={{ fontSize: '14px', opacity: 0.8, marginTop: '4px' }}>
                    Progresso: {sessionData.percentual_conclusao}%
                  </div>
                )}
              </div>
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <Button
                variant="secondary"
                onClick={() => setWorkspaceVisivel(!workspaceVisivel)}
                size="sm"
              >
                {workspaceVisivel ? '💬 Apenas Chat' : '📊 Ver Workspace'}
              </Button>
              <Button variant="outline" onClick={() => {
                // Limpa dados da sessão (useEffect cuida do estado de navegação)
                setMensagens([]);
                setDadosWorkspace(null);
                setSessionData(null);
                helenaPEService.resetar();
                sessionManager.clearSession();
                navigate('/planejamento-estrategico');
              }} size="sm">
                ← Nova Sessão
              </Button>
            </div>
          </div>

        {/* Área de Mensagens */}
        <div style={{
          flex: 1,
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderTop: 'none',
          borderBottom: 'none',
          padding: '24px',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px'
        }}>
          {mostrarCardIntro && modelo && (
            <PEChatIntro
              modelo={modelo}
              loading={loading}
              onIniciarAgente={iniciarAgente}
              onVerExemplos={verExemplos}
              onEntenderMetodo={entenderMetodo}
              onVoltar={() => navigate('/planejamento-estrategico/modelos')}
            />
          )}

          {mensagens.map((msg, idx) => (
            <div key={idx}>
              <MessageBubbleRich
                tipo={msg.tipo}
                texto={msg.texto}
              />

              {/* Botão de confirmação (aparece apenas na última mensagem quando aguardando) */}
              {msg.tipo === 'helena' && aguardandoConfirmacao && idx === mensagens.length - 1 && (
                <div style={{
                  display: 'flex',
                  gap: '12px',
                  marginTop: '12px'
                }}>
                  <Button
                    onClick={() => {
                      setAguardandoConfirmacao(false);
                      confirmarModeloSelecionado();
                    }}
                    style={{
                      background: 'linear-gradient(135deg, #1B4F72 0%, #2874A6 100%)',
                      color: '#fff',
                      padding: '10px 24px',
                      borderRadius: '8px',
                      border: 'none',
                      fontWeight: 600,
                      cursor: 'pointer'
                    }}
                  >
                    ✓ Confirmar
                  </Button>
                  <Button
                    onClick={() => navigate('/planejamento-estrategico/modelos')}
                    style={{
                      background: 'rgba(255, 255, 255, 0.2)',
                      color: '#2C3E50',
                      padding: '10px 24px',
                      borderRadius: '8px',
                      border: '1px solid rgba(27, 79, 114, 0.3)',
                      fontWeight: 600,
                      cursor: 'pointer'
                    }}
                  >
                    ← Voltar
                  </Button>
                </div>
              )}
            </div>
          ))}
          {loading && (
            <MessageBubbleRich
              tipo="helena"
              texto=""
              isLoading={true}
            />
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input */}
        <div style={{
          padding: '20px',
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(10px)',
          borderRadius: '0 0 16px 16px',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderTop: 'none',
          display: 'flex',
          gap: '12px'
        }}>
          <input
            type="text"
            value={inputTexto}
            onChange={(e) => setInputTexto(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && enviarMensagem()}
            placeholder="Digite sua mensagem..."
            disabled={loading}
            style={{
              flex: 1,
              padding: '12px 20px',
              borderRadius: '12px',
              border: '1px solid rgba(27, 79, 114, 0.3)',
              background: 'rgba(255, 255, 255, 0.95)',
              color: '#2C3E50',
              fontSize: '15px',
              outline: 'none'
            }}
          />
          <Button
            variant="primary"
            onClick={enviarMensagem}
            disabled={loading || !inputTexto.trim()}
            size="md"
          >
            Enviar
          </Button>
        </div>
        </div>

        {/* Coluna do Workspace */}
        {workspaceVisivel && (
          <div style={{
            flex: 1,
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '16px',
            border: '2px solid rgba(27, 79, 114, 0.2)',
            overflowY: 'auto',
            boxShadow: '0 8px 32px rgba(27, 79, 114, 0.15)'
          }}>
            {renderWorkspace()}
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={containerStyle}>
      <div style={fundoStyle} />
      {estado === 'inicial' && renderInicial()}
      {estado === 'painel' && renderPainel()}
      {estado === 'diagnostico' && renderDiagnostico()}
      {estado === 'modelos' && renderModelos()}
      {estado === 'chat' && renderChat()}

      {/* Modal de Informações de Modelos */}
      {modeloInfoAtual && (
        <ModeloInfoDrawer
          isOpen={modalInfoAberto}
          onClose={() => {
            setModalInfoAberto(false);
            setModeloInfoAtual(null);
          }}
          onIniciar={() => selecionarModelo(modeloInfoAtual)}
          modeloId={modeloInfoAtual}
        />
      )}

      {/* Modais dos Dashboards */}
      {dashboardAberto === 'areas' && (
        <DashboardAreas
          projetos={projetos}
          onAdicionarProjeto={adicionarProjeto}
          onAtualizarProjeto={atualizarProjeto}
          onFechar={() => setDashboardAberto(null)}
        />
      )}

      {dashboardAberto === 'diretor' && (
        <DashboardDiretor
          pedidos={pedidos}
          projetos={projetos}
          onFechar={() => setDashboardAberto(null)}
        />
      )}
    </div>
  );
};

export default HelenaPEModerna;
