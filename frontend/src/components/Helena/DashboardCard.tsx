/**
 * DashboardCard - Card de Acesso aos Dashboards
 * Helena PE - Página Inicial
 *
 * Fornece acesso rápido aos dois dashboards:
 * - Dashboard das Áreas (operacional)
 * - Dashboard do Diretor (executivo)
 */

import React from 'react';
import { NavigateFunction } from 'react-router-dom';
import './DashboardCard.css';

export interface DashboardCardProps {
  onAbrirDashboardAreas: () => void;
  onAbrirDashboardDiretor: () => void;
  onIniciarDiagnostico?: () => void;
  onExplorarModelos?: () => void;
  onEscolhaDireta?: () => void;
  navigate?: NavigateFunction;
  estatisticas?: {
    total_projetos: number;
    total_pedidos: number;
    pedidos_atrasados: number;
  };
}

export const DashboardCard: React.FC<DashboardCardProps> = ({
  onAbrirDashboardAreas,
  onAbrirDashboardDiretor,
  onIniciarDiagnostico,
  onExplorarModelos,
  onEscolhaDireta,
  navigate,
  estatisticas
}) => {
  // Função auxiliar para navegação segura
  const navegar = (rota: string) => {
    if (navigate) {
      navigate(rota);
    } else {
      window.location.href = rota;
    }
  };
  const [dominioExpandido, setDominioExpandido] = React.useState<number | null>(null);

  const toggleDominio = (numero: number) => {
    console.log('Toggle domínio:', numero, 'Atual:', dominioExpandido);
    setDominioExpandido(dominioExpandido === numero ? null : numero);
  };

  return (
    <div className="dashboard-card-container-full-width">
      {/* Barra de Domínios MGI */}
      <div className="mgi-dominios-bar">
        <button className="dominio-tab dominio-mapa">
          <span className="dominio-text">Mapa de<br />Artefatos</span>
        </button>
        <button
          className="dominio-tab dominio-1"
          onClick={() => toggleDominio(1)}
        >
          <span className="dominio-text">Abordagens e<br />fundamentos de gestão</span>
          <span className={`chevron ${dominioExpandido === 1 ? 'expanded' : ''}`}>▼</span>
        </button>
        <button
          className="dominio-tab dominio-2"
          onClick={() => toggleDominio(2)}
        >
          <span className="dominio-text">Escopo e<br />valor</span>
          <span className={`chevron ${dominioExpandido === 2 ? 'expanded' : ''}`}>▼</span>
        </button>
        <button
          className="dominio-tab dominio-3"
          onClick={() => toggleDominio(3)}
        >
          <span className="dominio-text">Equipe e<br />responsabilidades</span>
          <span className={`chevron ${dominioExpandido === 3 ? 'expanded' : ''}`}>▼</span>
        </button>
        <button
          className="dominio-tab dominio-4"
          onClick={() => toggleDominio(4)}
        >
          <span className="dominio-text">Capacidades e<br />atividades</span>
          <span className={`chevron ${dominioExpandido === 4 ? 'expanded' : ''}`}>▼</span>
        </button>
        <button
          className="dominio-tab dominio-5"
          onClick={() => toggleDominio(5)}
        >
          <span className="dominio-text">Partes interessadas<br />e comunicação</span>
          <span className={`chevron ${dominioExpandido === 5 ? 'expanded' : ''}`}>▼</span>
        </button>
        <button
          className="dominio-tab dominio-6"
          onClick={() => toggleDominio(6)}
        >
          <span className="dominio-text">Incerteza e<br />contexto</span>
          <span className={`chevron ${dominioExpandido === 6 ? 'expanded' : ''}`}>▼</span>
        </button>
        <button
          className="dominio-tab dominio-7"
          onClick={() => toggleDominio(7)}
        >
          <span className="dominio-text">Impacto e<br />aprendizado</span>
          <span className={`chevron ${dominioExpandido === 7 ? 'expanded' : ''}`}>▼</span>
        </button>
      </div>

      {/* Card de Expansão do Domínio 1 */}
      {dominioExpandido === 1 && (
        <div className="dominio-expansion-card dominio-1-expansion">
          <div className="expansion-header">
            <h3>🟦 Domínio 1 — Abordagens e Fundamentos de Gestão</h3>
            <button
              className="expansion-close"
              onClick={() => setDominioExpandido(null)}
              aria-label="Fechar"
            >
              ✕
            </button>
          </div>

          <div className="expansion-content">
            <div className="expansion-section">
              <h4>📘 Conceito</h4>
              <p>
                Estabelece a base do planejamento — define propósito,
                valor público e abordagem de gestão (tradicional, ágil ou híbrida).
              </p>
            </div>

            <div className="expansion-section">
              <h4>🧰 Artefatos</h4>
              <ul className="artefatos-list">
                <li onClick={() => navegar('/dominio1/canvas')}>
                  <span className="artefato-icone">📋</span>
                  <span>Canvas de Projeto Público</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/dominio1/linha-tempo')}>
                  <span className="artefato-icone">📅</span>
                  <span>Linha do Tempo Inicial</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/dominio1/checklist')}>
                  <span className="artefato-icone">✓</span>
                  <span>Checklist de Governança</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/chat')}>
                  <span className="artefato-icone">📊</span>
                  <span>Matriz 5W2H (Helena)</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/planejamento-estrategico')}>
                  <span className="artefato-icone">🎯</span>
                  <span>OKR (Helena PE)</span>
                  <span className="artefato-arrow">→</span>
                </li>
              </ul>
            </div>

            <div className="expansion-footer">
              <button
                className="btn-saiba-mais"
                onClick={() => navegar('/dominio1')}
              >
                Saiba mais sobre este domínio →
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Card de Expansão do Domínio 2 */}
      {dominioExpandido === 2 && (
        <div className="dominio-expansion-card dominio-2-expansion">
          <div className="expansion-header">
            <h3>🟦 Domínio 2 — Escopo e Valor</h3>
            <button
              className="expansion-close"
              onClick={() => setDominioExpandido(null)}
              aria-label="Fechar"
            >
              ✕
            </button>
          </div>

          <div className="expansion-content">
            <div className="expansion-section">
              <h4>📘 Conceito</h4>
              <p>
                Delimita o que o projeto vai entregar e que valor público ele pretende gerar.
                Define produtos, metas, limites, resultados esperados e critérios de sucesso.
              </p>
            </div>

            <div className="expansion-section">
              <h4>🧰 Artefatos</h4>
              <ul className="artefatos-list">
                <li onClick={() => navegar('/dominio2/canvas-escopo')}>
                  <span className="artefato-icone">📋</span>
                  <span>Canvas de Escopo e Valor</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/dominio2/matriz-raci')}>
                  <span className="artefato-icone">👥</span>
                  <span>Matriz de Entregas e Responsáveis (RACI)</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/dominio2/indicadores')}>
                  <span className="artefato-icone">📊</span>
                  <span>Painel de Indicadores de Valor Público</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/dominio2/exclusoes')}>
                  <span className="artefato-icone">🚫</span>
                  <span>Mapa de Exclusões e Restrições</span>
                  <span className="artefato-arrow">→</span>
                </li>
              </ul>
            </div>

            <div className="expansion-footer">
              <button
                className="btn-saiba-mais"
                onClick={() => navegar('/dominio2')}
              >
                Saiba mais sobre este domínio →
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Card de Expansão do Domínio 3 */}
      {dominioExpandido === 3 && (
        <div className="dominio-expansion-card dominio-3-expansion">
          <div className="expansion-header">
            <h3>🟩 Domínio 3 — Equipe e Responsabilidades</h3>
            <button
              className="expansion-close"
              onClick={() => setDominioExpandido(null)}
              aria-label="Fechar"
            >
              ✕
            </button>
          </div>

          <div className="expansion-content">
            <div className="expansion-section">
              <h4>📘 Conceito</h4>
              <p>
                Define papéis, responsabilidades e instâncias de decisão do projeto,
                garantindo clareza, colaboração e governança.
              </p>
            </div>

            <div className="expansion-section">
              <h4>🧰 Artefatos</h4>
              <ul className="artefatos-list">
                <li onClick={() => navegar('/dominio3/mapa-papeis')}>
                  <span className="artefato-icone">👥</span>
                  <span>Mapa de Papéis e Responsabilidades</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/dominio3/organograma')}>
                  <span className="artefato-icone">🏢</span>
                  <span>Organograma de Governança</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/dominio3/acordo-trabalho')}>
                  <span className="artefato-icone">📜</span>
                  <span>Acordo de Trabalho da Equipe</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/dominio3/mapa-competencias')}>
                  <span className="artefato-icone">🎯</span>
                  <span>Mapa de Competências do Projeto</span>
                  <span className="artefato-arrow">→</span>
                </li>
              </ul>
            </div>

            <div className="expansion-footer">
              <button
                className="btn-saiba-mais"
                onClick={() => navegar('/dominio3')}
              >
                Saiba mais sobre este domínio →
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Card de Expansão do Domínio 4 */}
      {dominioExpandido === 4 && (
        <div className="dominio-expansion-card dominio-4-expansion">
          <div className="expansion-header">
            <h3>🟦 Domínio 4 — Capacidades e Atividades</h3>
            <button
              className="expansion-close"
              onClick={() => setDominioExpandido(null)}
              aria-label="Fechar"
            >
              ✕
            </button>
          </div>

          <div className="expansion-content">
            <div className="expansion-section">
              <h4>📘 Conceito</h4>
              <p>
                Organiza atividades, recursos e prazos para transformar o plano em execução,
                assegurando controle e eficiência operacional.
              </p>
            </div>

            <div className="expansion-section">
              <h4>🧰 Artefatos</h4>
              <ul className="artefatos-list">
                <li onClick={() => navegar('/dominio4/plano-atividades')}>
                  <span className="artefato-icone">📋</span>
                  <span>Plano de Atividades e Recursos (5W2H expandido)</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/dominio4/cronograma')}>
                  <span className="artefato-icone">📅</span>
                  <span>Cronograma Simplificado / Timeline Dinâmica</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/dominio4/mapa-gargalos')}>
                  <span className="artefato-icone">⚠️</span>
                  <span>Mapa de Gargalos e Capacidades Críticas</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/dominio4/painel-progresso')}>
                  <span className="artefato-icone">📊</span>
                  <span>Painel de Progresso Operacional</span>
                  <span className="artefato-arrow">→</span>
                </li>
              </ul>
            </div>

            <div className="expansion-footer">
              <button
                className="btn-saiba-mais"
                onClick={() => navegar('/dominio4')}
              >
                Saiba mais sobre este domínio →
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Card de Expansão do Domínio 5 */}
      {dominioExpandido === 5 && (
        <div className="dominio-expansion-card dominio-5-expansion">
          <div className="expansion-header">
            <h3>🟠 Domínio 5 — Partes Interessadas e Comunicação</h3>
            <button
              className="expansion-close"
              onClick={() => setDominioExpandido(null)}
              aria-label="Fechar"
            >
              ✕
            </button>
          </div>

          <div className="expansion-content">
            <div className="expansion-section">
              <h4>📘 Conceito</h4>
              <p>
                Mapeia e engaja atores internos e externos, garantindo comunicação clara,
                transparente e contínua durante todo o projeto.
              </p>
            </div>

            <div className="expansion-section">
              <h4>🧰 Artefatos</h4>
              <ul className="artefatos-list">
                <li onClick={() => navegar('/dominio5/mapa-stakeholders')}>
                  <span className="artefato-icone">👥</span>
                  <span>Mapa de Partes Interessadas</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/dominio5/matriz-engajamento')}>
                  <span className="artefato-icone">📊</span>
                  <span>Matriz de Engajamento (Influência x Interesse)</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/dominio5/plano-comunicacao')}>
                  <span className="artefato-icone">📢</span>
                  <span>Plano de Comunicação Institucional</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/dominio5/registro-feedbacks')}>
                  <span className="artefato-icone">📝</span>
                  <span>Registro de Interações e Feedbacks</span>
                  <span className="artefato-arrow">→</span>
                </li>
              </ul>
            </div>

            <div className="expansion-footer">
              <button
                className="btn-saiba-mais"
                onClick={() => navegar('/dominio5')}
              >
                Saiba mais sobre este domínio →
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Card de Expansão do Domínio 6 */}
      {dominioExpandido === 6 && (
        <div className="dominio-expansion-card dominio-6-expansion">
          <div className="expansion-header">
            <h3>🔴 Domínio 6 — Incerteza e Contexto</h3>
            <button
              className="expansion-close"
              onClick={() => setDominioExpandido(null)}
              aria-label="Fechar"
            >
              ✕
            </button>
          </div>

          <div className="expansion-content">
            <div className="expansion-section">
              <h4>📘 Conceito</h4>
              <p>
                Antecipar e gerenciar riscos que possam afetar o projeto,
                avaliando contexto, controles e respostas para garantir resiliência.
              </p>
            </div>

            <div className="expansion-section">
              <h4>🧰 Artefatos</h4>
              <ul className="artefatos-list">
                <li onClick={() => navegar('/dominio6/mapa-contexto')}>
                  <span className="artefato-icone">🌍</span>
                  <span>Mapa de Contexto e Fatores Externos</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/dominio6/matriz-riscos')}>
                  <span className="artefato-icone">⚠️</span>
                  <span>Matriz de Riscos e Controles</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/dominio6/plano-tratamento')}>
                  <span className="artefato-icone">🛡️</span>
                  <span>Plano de Tratamento de Riscos</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/dominio6/registro-licoes')}>
                  <span className="artefato-icone">📚</span>
                  <span>Registro de Ocorrências e Lições Aprendidas</span>
                  <span className="artefato-arrow">→</span>
                </li>
              </ul>
            </div>

            <div className="expansion-footer">
              <button
                className="btn-saiba-mais"
                onClick={() => navegar('/dominio6')}
              >
                Saiba mais sobre este domínio →
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Card de Expansão do Domínio 7 */}
      {dominioExpandido === 7 && (
        <div className="dominio-expansion-card dominio-7-expansion">
          <div className="expansion-header">
            <h3>🟦 Domínio 7 — Impacto e Aprendizado</h3>
            <button
              className="expansion-close"
              onClick={() => setDominioExpandido(null)}
              aria-label="Fechar"
            >
              ✕
            </button>
          </div>

          <div className="expansion-content">
            <div className="expansion-section">
              <h4>📘 Conceito</h4>
              <p>
                Avalia resultados, consolida aprendizados e garante a sustentabilidade
                dos ganhos institucionais, transformando o projeto em conhecimento coletivo.
              </p>
            </div>

            <div className="expansion-section">
              <h4>🧰 Artefatos</h4>
              <ul className="artefatos-list">
                <li onClick={() => navegar('/dominio7/painel-resultados')}>
                  <span className="artefato-icone">📊</span>
                  <span>Painel de Resultados e Impacto</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/dominio7/relatorio-licoes')}>
                  <span className="artefato-icone">📝</span>
                  <span>Relatório de Lições Aprendidas</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/dominio7/matriz-sustentabilidade')}>
                  <span className="artefato-icone">♻️</span>
                  <span>Matriz de Sustentabilidade e Replicabilidade</span>
                  <span className="artefato-arrow">→</span>
                </li>
                <li onClick={() => navegar('/dominio7/avaliacao-satisfacao')}>
                  <span className="artefato-icone">⭐</span>
                  <span>Avaliação de Satisfação e Valor Público Percebido</span>
                  <span className="artefato-arrow">→</span>
                </li>
              </ul>
            </div>

            <div className="expansion-footer">
              <button
                className="btn-saiba-mais"
                onClick={() => navegar('/dominio7')}
              >
                Saiba mais sobre este domínio →
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Layout em 2 Colunas */}
      <div className="dashboard-two-columns">
        {/* COLUNA ESQUERDA - Dashboards */}
        <div className="dashboard-left-column">
          <div className="dashboard-card">
            <div className="dashboard-card-header">
              <h4>Dashboards de Governança</h4>
              <p>Acompanhamento de projetos estratégicos e pedidos da Direção</p>
            </div>

            {estatisticas && (
              <div className="dashboard-stats">
                <div className="stat-item">
                  <span className="stat-icon">📁</span>
                  <div className="stat-content">
                    <span className="stat-value">{estatisticas.total_projetos}</span>
                    <span className="stat-label">Projetos ativos</span>
                  </div>
                </div>
                <div className="stat-item">
                  <span className="stat-icon">📋</span>
                  <div className="stat-content">
                    <span className="stat-value">{estatisticas.total_pedidos}</span>
                    <span className="stat-label">Pedidos da Direção</span>
                  </div>
                </div>
              </div>
            )}

            <div className="dashboard-actions">
              <button
                className="dashboard-btn dashboard-btn-areas"
                onClick={onAbrirDashboardAreas}
                aria-label="Abrir Dashboard das Áreas"
              >
                <span className="btn-icon">🏢</span>
                <div className="btn-content">
                  <span className="btn-title">Dashboard das Áreas</span>
                  <span className="btn-description">
                    Gerencie projetos estratégicos da sua coordenação
                  </span>
                </div>
                <span className="btn-arrow">→</span>
              </button>

              <button
                className="dashboard-btn dashboard-btn-diretor"
                onClick={onAbrirDashboardDiretor}
                aria-label="Abrir Dashboard do Diretor"
              >
                <span className="btn-icon">👔</span>
                <div className="btn-content">
                  <span className="btn-title">Dashboard do Diretor</span>
                  <span className="btn-description">
                    Visão consolidada de todos os pedidos e prazos
                  </span>
                </div>
                <span className="btn-arrow">→</span>
              </button>
            </div>

            <div className="dashboard-card-footer">
              <p className="footer-text">
                💡 <strong>Dica:</strong> Use o Dashboard das Áreas para registrar e acompanhar seus projetos.
                Pedidos do diretor são sincronizados automaticamente.
              </p>
            </div>
          </div>
        </div>

        {/* COLUNA DIREITA - Ações Rápidas */}
        <div className="dashboard-right-column">
          <button
            className="action-card action-card-diagnostico"
            onClick={onIniciarDiagnostico}
            aria-label="Iniciar diagnóstico guiado"
          >
            <span className="action-icon">🩺</span>
            <div className="action-content">
              <h5>Diagnóstico Guiado</h5>
              <p>Responda 5 perguntas e receba recomendação</p>
            </div>
          </button>

          <button
            className="action-card action-card-modelos"
            onClick={onExplorarModelos}
            aria-label="Explorar modelos disponíveis"
          >
            <span className="action-icon">📚</span>
            <div className="action-content">
              <h5>Explorar Modelos</h5>
              <p>Veja todos os 6 modelos disponíveis</p>
            </div>
          </button>

          <button
            className="action-card action-card-direta"
            onClick={onEscolhaDireta}
            aria-label="Escolha direta de modelo"
          >
            <span className="action-icon">⚡</span>
            <div className="action-content">
              <h5>Escolha Direta</h5>
              <p>Já sabe qual modelo quer? Comece agora</p>
            </div>
          </button>

          <button
            className="action-card action-card-ferramentas"
            onClick={() => navegar('/ferramentas-apoio')}
            aria-label="Ferramentas de apoio"
          >
            <span className="action-icon">🧰</span>
            <div className="action-content">
              <h5>Ferramentas de Apoio</h5>
              <p>Acesse ferramentas práticas pra usar no seu projeto</p>
            </div>
          </button>

          <button
            className="action-card action-card-metodos"
            onClick={() => navegar('/metodos')}
            aria-label="Métodos de gestão"
          >
            <span className="action-icon">🎯</span>
            <div className="action-content">
              <h5>Métodos de Gestão e Execução Estratégica</h5>
              <p>Ferramentas práticas para aplicar, acompanhar e melhorar a execução do seu plano.</p>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default DashboardCard;
