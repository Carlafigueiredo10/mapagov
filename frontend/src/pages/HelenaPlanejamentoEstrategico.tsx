/**
 * Helena Planejamento Estratégico - Página Principal
 *
 * Interface completa com chat, workspaces e controles
 * Integração total com backend via useHelenaPE hook
 */

import React, { useState, useEffect } from 'react';
import './HelenaPlanejamentoEstrategico.css';
import { useHelenaPE } from '../hooks/useHelenaPE';
import { useDashboard } from '../hooks/useDashboard';
import ChatInterface from '../components/Helena/ChatInterface';
import ProgressBar from '../components/Helena/ProgressBar';
import DashboardCard from '../components/Helena/DashboardCard';
import DashboardAreas from '../components/Helena/DashboardAreas';
import DashboardDiretor from '../components/Helena/DashboardDiretor';

// Importar workspaces (criaremos em seguida)
// import WorkspaceSWOT from '../components/Helena/Workspaces/WorkspaceSWOT';
// import WorkspaceOKR from '../components/Helena/Workspaces/WorkspaceOKR';
// import WorkspaceTradicional from '../components/Helena/Workspaces/WorkspaceTradicional';

export const HelenaPlanejamentoEstrategico: React.FC = () => {
  const {
    sessionData,
    isInitialized,
    isLoading,
    planejamentoId,
    modelosDisponiveis,
    iniciarSessao,
    resetarSessao
  } = useHelenaPE();

  // Hook do Dashboard
  const {
    projetos,
    pedidos,
    estatisticas,
    adicionarProjeto,
    atualizarProjeto
  } = useDashboard();

  const [mostrarWorkspace, setMostrarWorkspace] = useState(false);
  const [layoutMode, setLayoutMode] = useState<'chat' | 'workspace' | 'split'>('chat');
  const [dashboardAberto, setDashboardAberto] = useState<'areas' | 'diretor' | null>(null);

  // ============================================================================
  // INICIALIZAÇÃO
  // ============================================================================

  useEffect(() => {
    if (!isInitialized && !isLoading) {
      iniciarSessao();
    }
  }, [isInitialized, isLoading, iniciarSessao]);

  // ============================================================================
  // CONTROLE DE LAYOUT
  // ============================================================================

  useEffect(() => {
    // Mostrar workspace quando modelo for selecionado e estiver em construção
    if (
      sessionData?.modelo_selecionado &&
      sessionData?.estado_atual === 'construcao_modelo'
    ) {
      setMostrarWorkspace(true);
      setLayoutMode('split'); // Modo split por padrão
    }
  }, [sessionData?.modelo_selecionado, sessionData?.estado_atual]);

  // ============================================================================
  // HANDLERS
  // ============================================================================

  const handleNovoPlano = () => {
    if (confirm('Deseja iniciar um novo planejamento? O progresso atual será perdido.')) {
      resetarSessao();
      iniciarSessao();
      setMostrarWorkspace(false);
      setLayoutMode('chat');
    }
  };

  const handleMudancaEstado = (novoEstado: string) => {
    // Podemos adicionar lógica específica por estado aqui
    console.log('Estado mudou para:', novoEstado);
  };

  // ============================================================================
  // RENDERIZAÇÃO DE WORKSPACE
  // ============================================================================

  const renderWorkspace = () => {
    if (!sessionData?.modelo_selecionado) return null;

    const modelo = sessionData.modelo_selecionado;

    // Por enquanto, placeholder - implementaremos os workspaces específicos depois
    return (
      <div className="workspace-placeholder">
        <div className="placeholder-icone">🎯</div>
        <h3>Workspace {modelo.toUpperCase()}</h3>
        <p>Visualização interativa em desenvolvimento</p>
        <div className="placeholder-dados">
          <pre>{JSON.stringify(sessionData.estrutura_planejamento, null, 2)}</pre>
        </div>
      </div>
    );

    /*
    // Implementação futura:
    switch (modelo) {
      case 'swot':
        return <WorkspaceSWOT estrutura={sessionData.estrutura_planejamento} />;
      case 'okr':
        return <WorkspaceOKR estrutura={sessionData.estrutura_planejamento} />;
      case 'tradicional':
        return <WorkspaceTradicional estrutura={sessionData.estrutura_planejamento} />;
      default:
        return <div>Workspace não disponível para {modelo}</div>;
    }
    */
  };

  // ============================================================================
  // RENDERIZAÇÃO PRINCIPAL
  // ============================================================================

  if (!isInitialized) {
    return (
      <div className="helena-pe-loading">
        <div className="loading-container">
          <img src="/helena_plano.png" alt="Helena" className="loading-avatar" />
          <div className="loading-spinner" />
          <p>Inicializando Helena Planejamento Estratégico...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="helena-pe-container">
      {/* Header Global */}
      <header className="helena-pe-header">
        <div className="header-left">
          <img src="/helena_plano.png" alt="Helena" className="header-logo" />
          <div className="header-info">
            <h1>Helena Planejamento Estratégico</h1>
            <p className="header-subtitulo">
              {sessionData?.modelo_selecionado
                ? `Modelo: ${sessionData.modelo_selecionado.toUpperCase()}`
                : 'Assistente inteligente para planejamento estratégico'}
            </p>
          </div>
        </div>

        <div className="header-actions">
          {/* Controles de layout (quando workspace ativo) */}
          {mostrarWorkspace && (
            <div className="layout-controls">
              <button
                className={`layout-btn ${layoutMode === 'chat' ? 'active' : ''}`}
                onClick={() => setLayoutMode('chat')}
                title="Apenas Chat"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z" />
                </svg>
              </button>
              <button
                className={`layout-btn ${layoutMode === 'split' ? 'active' : ''}`}
                onClick={() => setLayoutMode('split')}
                title="Dividir Tela"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M3 3h8v18H3V3zm10 0h8v18h-8V3z" />
                </svg>
              </button>
              <button
                className={`layout-btn ${layoutMode === 'workspace' ? 'active' : ''}`}
                onClick={() => setLayoutMode('workspace')}
                title="Apenas Workspace"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M4 4h16v16H4V4zm2 2v12h12V6H6z" />
                </svg>
              </button>
            </div>
          )}

          {/* Ações */}
          <button className="btn-secondary" onClick={handleNovoPlano}>
            Novo Plano
          </button>
          {planejamentoId && (
            <button className="btn-primary">
              Exportar
            </button>
          )}
        </div>
      </header>

      {/* Barra de Progresso Global */}
      {sessionData && sessionData.percentual_conclusao > 0 && (
        <div className="helena-pe-progresso-global">
          <ProgressBar
            percentual={sessionData.percentual_conclusao}
            altura={8}
            mostrarLabel={true}
            mostrarMarcos={true}
          />
        </div>
      )}

      {/* Área Principal */}
      <main className="helena-pe-main">
        {/* Layout: Chat Only */}
        {layoutMode === 'chat' && (
          <div className="layout-chat-only">
            {/* Dashboard Card - Sempre visível na tela inicial */}
            {!sessionData?.modelo_selecionado && (
              <div className="helena-pe-dashboard-section">
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
            )}

            <ChatInterface onMudancaEstado={handleMudancaEstado} />
          </div>
        )}

        {/* Layout: Split */}
        {layoutMode === 'split' && (
          <div className="layout-split">
            <div className="split-chat">
              <ChatInterface onMudancaEstado={handleMudancaEstado} />
            </div>
            <div className="split-workspace">
              {renderWorkspace()}
            </div>
          </div>
        )}

        {/* Layout: Workspace Only */}
        {layoutMode === 'workspace' && (
          <div className="layout-workspace-only">
            {renderWorkspace()}
          </div>
        )}
      </main>

      {/* Informações de Debug (apenas em desenvolvimento) */}
      {import.meta.env.DEV && (
        <div className="helena-pe-debug">
          <details>
            <summary>Debug Info</summary>
            <pre>{JSON.stringify(sessionData, null, 2)}</pre>
          </details>
        </div>
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
          onFechar={() => setDashboardAberto(null)}
        />
      )}
    </div>
  );
};

export default HelenaPlanejamentoEstrategico;
