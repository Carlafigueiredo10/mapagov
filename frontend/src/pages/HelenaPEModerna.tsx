/**
 * Helena PE Moderna - Versão Funcional COMPLETA (Fase 2)
 *
 * Interface moderna com gradiente roxo e glassmorphism
 * INTEGRAÇÃO COMPLETA com backend via API
 */

import React, { useState, useEffect, useRef, CSSProperties } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import helenaPEService from '../services/helenaPESimples';
import { WorkspaceSWOT } from '../components/Helena/workspaces/WorkspaceSWOT';
import { WorkspaceOKR } from '../components/Helena/workspaces/WorkspaceOKR';
import { WorkspaceBSC } from '../components/Helena/workspaces/WorkspaceBSC';
import { Workspace5W2H } from '../components/Helena/workspaces/Workspace5W2H';
import { ModeloInfoDrawer } from '../components/Helena/ModeloInfoDrawer';
import DashboardCard from '../components/Helena/DashboardCard';
import DashboardAreas from '../components/Helena/DashboardAreas';
import DashboardDiretor from '../components/Helena/DashboardDiretor';
import { useDashboard } from '../hooks/useDashboard';
import { sessionManager } from '../utils/sessionManager';
import type { EstadoFluxo, Mensagem, SessionData, ModeloPlanejamento, PerguntaDiagnostico } from '../types/planejamento';
import modelosData from '../data/modelosPlanejamento.json';
import perguntasData from '../data/perguntasDiagnostico.json';

// Importados de arquivos JSON externos
const PERGUNTAS_DIAGNOSTICO: PerguntaDiagnostico[] = perguntasData;
const MODELOS = modelosData as Record<string, ModeloPlanejamento>;

export const HelenaPEModerna: React.FC = () => {
  const [estado, setEstado] = useState<EstadoFluxo>('inicial');
  const [hover, setHover] = useState<string | null>(null);
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
  const chatEndRef = useRef<HTMLDivElement>(null);

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

  // Adiciona mensagem ao histórico
  const adicionarMensagem = (tipo: 'user' | 'helena', texto: string) => {
    setMensagens((prev) => [...prev, { tipo, texto }]);
  };

  // Inicia diagnóstico
  const iniciarDiagnostico = () => {
    setPerguntaAtual(0);
    setRespostasDiagnostico({});
    setEstado('diagnostico');
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
    try {
      setLoading(true);
      setModeloSelecionado(modeloId);

      // Inicia sessão no backend
      const response = await helenaPEService.iniciarSessao();
      setSessionData(response.session_data);

      // Envia seleção do modelo
      const modeloNome = MODELOS[modeloId as keyof typeof MODELOS].nome;
      adicionarMensagem('helena', response.resposta);

      // Envia modelo escolhido
      const respostaModelo = await helenaPEService.enviarMensagem(`Quero usar o modelo ${modeloNome}`);
      setSessionData(respostaModelo.session_data);
      adicionarMensagem('helena', respostaModelo.resposta);

      setEstado('chat');
    } catch (error) {
      console.error('Erro ao selecionar modelo:', error);
      adicionarMensagem('helena', '⚠️ Não consegui me conectar agora. Verifique se o servidor está rodando e tente novamente.');
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
      const response = await helenaPEService.enviarMensagem(texto);
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
    background: 'linear-gradient(135deg, #f8fbff 0%, #e8f4fd 100%)',
    color: '#2C3E50',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '40px 20px',
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
    <div style={{ maxWidth: '1200px', width: '100%', zIndex: 1 }}>
      {/* Header com Helena ao lado */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '48px',
        marginBottom: '64px',
        justifyContent: 'center'
      }}>
        <img
          src="/helena_plano.png"
          alt="Helena Planejamento Estratégico"
          style={{
            width: '280px',
            height: 'auto',
            filter: 'drop-shadow(0 10px 30px rgba(27, 79, 114, 0.2))'
          }}
        />
        <div style={{ textAlign: 'left', maxWidth: '600px' }}>
          <h1 style={{ fontSize: '48px', fontWeight: 'bold', marginBottom: '16px', lineHeight: 1.2 }}>
            Helena Planejamento Estratégico
          </h1>
          <p style={{ fontSize: '20px', opacity: 0.9, lineHeight: 1.6 }}>
            Assistente inteligente para planejamento estratégico no setor público.
            <br />
            <strong>Baseada em DECIPEX, MGI e MMIP/CGU.</strong>
          </p>
        </div>
      </div>

      {/* Dashboard Card */}
      <div style={{ marginBottom: '48px' }}>
        <DashboardCard
          onAbrirDashboardAreas={() => setDashboardAberto('areas')}
          onAbrirDashboardDiretor={() => setDashboardAberto('diretor')}
          estatisticas={estatisticas ? {
            total_projetos: estatisticas.total_projetos,
            total_pedidos: estatisticas.total_pedidos,
            pedidos_atrasados: estatisticas.pedidos_atrasados
          } : undefined}
        />
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '32px'
      }}>
        {['diagnostico', 'explorar', 'direto'].map((modo) => (
          <Card
            key={modo}
            variant="glass"
            onClick={() => {
              if (modo === 'diagnostico') {
                iniciarDiagnostico();
              } else {
                setEstado('modelos');
              }
            }}
            style={{
              cursor: 'pointer',
              transform: hover === modo ? 'scale(1.08)' : 'scale(1)',
              transition: 'all 0.3s ease',
              boxShadow: hover === modo ? '0 20px 40px rgba(0,0,0,0.3)' : '0 8px 16px rgba(0,0,0,0.2)'
            }}
            onMouseEnter={() => setHover(modo)}
            onMouseLeave={() => setHover(null)}
          >
            <div style={{ fontSize: '56px', marginBottom: '20px' }}>
              {modo === 'diagnostico' ? '🩺' : modo === 'explorar' ? '📚' : '⚡'}
            </div>
            <h3 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '12px' }}>
              {modo === 'diagnostico' ? 'Diagnóstico Guiado' : modo === 'explorar' ? 'Explorar Modelos' : 'Escolha Direta'}
            </h3>
            <p style={{ fontSize: '15px', opacity: 0.85 }}>
              {modo === 'diagnostico'
                ? 'Responda 5 perguntas e receba recomendação'
                : modo === 'explorar'
                ? 'Veja todos os 6 modelos disponíveis'
                : 'Já sabe qual modelo quer? Comece agora'}
            </p>
          </Card>
        ))}
      </div>
    </div>
  );

  const renderDiagnostico = () => {
    const pergunta = PERGUNTAS_DIAGNOSTICO[perguntaAtual];

    return (
      <div style={{ maxWidth: '800px', width: '100%', zIndex: 1 }}>
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <div style={{ fontSize: '64px', marginBottom: '24px' }}>🩺</div>
          <h1 style={{ fontSize: '36px', fontWeight: 'bold', marginBottom: '16px' }}>
            Diagnóstico Guiado
          </h1>
          <p style={{ fontSize: '18px', opacity: 0.9 }}>
            Pergunta {perguntaAtual + 1} de {PERGUNTAS_DIAGNOSTICO.length}
          </p>
        </div>

        <Card variant="glass" style={{ marginBottom: '32px', textAlign: 'center' }}>
          <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '32px', lineHeight: 1.5 }}>
            {pergunta.texto}
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {pergunta.opcoes.map((opcao) => (
              <Button
                key={opcao.valor}
                variant="outline"
                onClick={() => responderPerguntaDiagnostico(opcao.valor)}
                disabled={loading}
                size="lg"
                style={{
                  fontSize: '16px',
                  padding: '20px 24px',
                  textAlign: 'left',
                  justifyContent: 'flex-start',
                  opacity: loading ? 0.6 : 1
                }}
              >
                {opcao.texto}
              </Button>
            ))}
          </div>
        </Card>

        {loading && (
          <div style={{ textAlign: 'center', fontSize: '18px', marginBottom: '24px' }}>
            ⏳ Processando diagnóstico...
          </div>
        )}

        {/* Barra de Progresso */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '12px',
          height: '8px',
          overflow: 'hidden',
          marginBottom: '24px'
        }}>
          <div style={{
            background: 'linear-gradient(90deg, #3498DB, #27AE60)',
            height: '100%',
            width: `${((perguntaAtual + 1) / PERGUNTAS_DIAGNOSTICO.length) * 100}%`,
            transition: 'width 0.3s ease'
          }} />
        </div>

        <div style={{ textAlign: 'center' }}>
          <Button
            variant="outline"
            onClick={() => {
              setEstado('inicial');
              setPerguntaAtual(0);
              setRespostasDiagnostico({});
            }}
            size="md"
            disabled={loading}
          >
            ← Cancelar
          </Button>
        </div>
      </div>
    );
  };

  const renderModelos = () => (
    <div style={{ maxWidth: '1400px', width: '100%', zIndex: 1 }}>
      <h1 style={{ fontSize: '42px', fontWeight: 'bold', marginBottom: '20px', textAlign: 'center' }}>
        Escolha seu modelo de planejamento
      </h1>
      <p style={{ fontSize: '20px', opacity: 0.95, marginBottom: '56px', textAlign: 'center' }}>
        Cada modelo foi criado para um tipo diferente de desafio.
      </p>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '36px',
        marginBottom: '48px'
      }}>
        {Object.values(MODELOS).map((modelo) => (
          <div key={modelo.id} style={{ position: 'relative' }}>
            <Card
              variant="glass"
              onClick={() => selecionarModelo(modelo.id)}
              style={{
                cursor: loading ? 'wait' : 'pointer',
                transform: hover === modelo.id ? 'scale(1.06) translateY(-8px)' : 'scale(1)',
                transition: 'all 0.35s ease',
                boxShadow: hover === modelo.id ? '0 24px 48px rgba(0,0,0,0.35)' : '0 10px 20px rgba(0,0,0,0.25)',
                minHeight: '280px',
                opacity: loading ? 0.6 : 1
              }}
              onMouseEnter={() => !loading && setHover(modelo.id)}
              onMouseLeave={() => setHover(null)}
            >
              {/* Botão de Info - disponível para modelos com conteúdo */}
              {(modelo.id === 'okr' || modelo.id === 'swot' || modelo.id === 'bsc' ||
                modelo.id === 'tradicional' || modelo.id === 'cenarios' || modelo.id === '5w2h') && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setModeloInfoAtual(modelo.id);
                    setModalInfoAberto(true);
                  }}
                  style={{
                    position: 'absolute',
                    top: '16px',
                    right: '16px',
                    background: 'rgba(52, 152, 219, 0.9)',
                    border: 'none',
                    borderRadius: '50%',
                    width: '36px',
                    height: '36px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    fontSize: '18px',
                    color: '#ffffff',
                    boxShadow: '0 4px 12px rgba(52, 152, 219, 0.4)',
                    transition: 'all 0.2s ease',
                    zIndex: 10
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'scale(1.1)';
                    e.currentTarget.style.background = 'rgba(52, 152, 219, 1)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'scale(1)';
                    e.currentTarget.style.background = 'rgba(52, 152, 219, 0.9)';
                  }}
                  title={`Saiba mais sobre ${modelo.nome}`}
                >
                  ℹ️
                </button>
              )}

              <div style={{ fontSize: '64px', marginBottom: '20px' }}>{modelo.icone}</div>
              <h3 style={{ fontSize: '26px', fontWeight: 'bold', marginBottom: '12px' }}>
                {modelo.nome}
              </h3>
              <p style={{ fontSize: '15px', opacity: 0.9, marginBottom: '20px', minHeight: '70px' }}>
                {modelo.descricao}
              </p>
              <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '16px' }}>
                {modelo.tags.map((tag) => (
                  <Badge key={tag} variant="outline">{tag}</Badge>
                ))}
              </div>
              <div style={{ fontSize: '13px', opacity: 0.75, borderTop: '1px solid rgba(255,255,255,0.2)', paddingTop: '12px' }}>
                📊 {modelo.complexidade} | ⏱️ {modelo.prazo}
              </div>
            </Card>
          </div>
        ))}
      </div>

      {loading && (
        <div style={{ textAlign: 'center', marginBottom: '24px', fontSize: '18px' }}>
          ⏳ Iniciando sessão com Helena...
        </div>
      )}

      <div style={{ textAlign: 'center' }}>
        <Button variant="outline" onClick={() => setEstado('inicial')} size="lg" disabled={loading}>
          ← Voltar
        </Button>
      </div>
    </div>
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
                setEstado('inicial');
                setMensagens([]);
                setModeloSelecionado(null);
                setWorkspaceVisivel(false);
                setDadosWorkspace(null);
                helenaPEService.resetar();
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
          {mensagens.map((msg, idx) => (
            <div
              key={idx}
              style={{
                alignSelf: msg.tipo === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '75%'
              }}
            >
              <div style={{
                padding: '16px 20px',
                borderRadius: '16px',
                background: msg.tipo === 'user'
                  ? '#1B4F72'
                  : 'rgba(255, 255, 255, 0.9)',
                backdropFilter: 'blur(10px)',
                border: msg.tipo === 'user' ? 'none' : '1px solid rgba(27, 79, 114, 0.2)',
                boxShadow: '0 4px 12px rgba(27, 79, 114, 0.1)',
                fontSize: '15px',
                lineHeight: 1.6,
                whiteSpace: 'pre-wrap',
                color: msg.tipo === 'user' ? '#ffffff' : '#2C3E50'
              }}>
                {msg.texto}
              </div>
            </div>
          ))}
          {loading && (
            <div style={{ alignSelf: 'flex-start', maxWidth: '75%' }}>
              <div style={{
                padding: '16px 20px',
                borderRadius: '16px',
                background: 'rgba(255, 255, 255, 0.15)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                fontSize: '15px'
              }}>
                ⏳ Helena está pensando...
              </div>
            </div>
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
              border: '1px solid rgba(255, 255, 255, 0.3)',
              background: 'rgba(255, 255, 255, 0.1)',
              color: '#ffffff',
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
