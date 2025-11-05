/**
 * DashboardDiretor - Dashboard Executivo
 * Helena PE - Visão Consolidada de Pedidos da Direção
 */

import React, { useState, useMemo } from 'react';
import { ProjetoEstrategico, PedidoDiretorConsolidado } from '../../types/dashboard';
import {
  calcularStatusAlerta,
  getIconeAlerta,
  formatarDiasRestantes,
  calcularDiasRestantes,
  filtrarPedidos,
  calcularEstatisticas
} from '../../utils/dashboardSync';
import './DashboardDiretor.css';

export interface DashboardDiretorProps {
  pedidos: PedidoDiretorConsolidado[];
  projetos: ProjetoEstrategico[]; // Adicionado para acesso aos dados completos
  onFechar: () => void;
}

export const DashboardDiretor: React.FC<DashboardDiretorProps> = ({
  pedidos,
  projetos,
  onFechar
}) => {
  const [filtroStatus, setFiltroStatus] = useState<string>('Todos');
  const [filtroArea, setFiltroArea] = useState<string>('Todas');
  const [busca, setBusca] = useState('');
  const [projetoDetalhado, setProjetoDetalhado] = useState<ProjetoEstrategico | null>(null);

  // Estatísticas
  const stats = useMemo(() => calcularEstatisticas(pedidos), [pedidos]);

  // Pedidos filtrados
  const pedidosFiltrados = useMemo(() => {
    let resultado = [...pedidos];

    if (filtroStatus !== 'Todos') {
      resultado = resultado.filter(p => p.status_pedido === filtroStatus);
    }

    if (filtroArea !== 'Todas') {
      resultado = resultado.filter(p => p.area === filtroArea);
    }

    if (busca) {
      const termo = busca.toLowerCase();
      resultado = resultado.filter(p =>
        p.projeto.toLowerCase().includes(termo) ||
        p.descricao_pedido.toLowerCase().includes(termo) ||
        p.area.toLowerCase().includes(termo)
      );
    }

    // Ordenar por prioridade (atrasados primeiro)
    return resultado.sort((a, b) => {
      const alertaA = calcularStatusAlerta(a);
      const alertaB = calcularStatusAlerta(b);
      const prioridades = { vermelho: 0, amarelo: 1, neutro: 2, verde: 3 };
      return prioridades[alertaA] - prioridades[alertaB];
    });
  }, [pedidos, filtroStatus, filtroArea, busca]);

  // Áreas únicas
  const areas = useMemo(() => {
    return Array.from(new Set(pedidos.map(p => p.area))).sort();
  }, [pedidos]);

  return (
    <div className="dashboard-diretor-overlay">
      <div className="dashboard-diretor-container">
        {/* Header */}
        <header className="dashboard-header diretor">
          <div className="header-content">
            <h2>👔 Dashboard do Diretor</h2>
            <p>Visão Consolidada de Pedidos e Prazos</p>
          </div>
          <button className="btn-fechar" onClick={onFechar}>✕</button>
        </header>

        {/* Estatísticas */}
        <div className="dashboard-stats-panel">
          <div className="stat-card">
            <span className="stat-icon">📋</span>
            <div className="stat-info">
              <span className="stat-value">{stats.total}</span>
              <span className="stat-label">Total de Pedidos</span>
            </div>
          </div>
          <div className="stat-card success">
            <span className="stat-icon">✅</span>
            <div className="stat-info">
              <span className="stat-value">{stats.atendidos}</span>
              <span className="stat-label">Atendidos</span>
            </div>
          </div>
          <div className="stat-card warning">
            <span className="stat-icon">🟡</span>
            <div className="stat-info">
              <span className="stat-value">{stats.em_andamento}</span>
              <span className="stat-label">Em Andamento</span>
            </div>
          </div>
          <div className="stat-card danger">
            <span className="stat-icon">🔴</span>
            <div className="stat-info">
              <span className="stat-value">{stats.atrasados}</span>
              <span className="stat-label">Atrasados</span>
            </div>
          </div>
        </div>

        {/* Filtros */}
        <div className="dashboard-filters">
          <div className="filter-group">
            <input
              type="text"
              placeholder="🔍 Buscar por projeto, descrição ou área..."
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              className="search-input"
            />
          </div>

          <div className="filter-row">
            <select
              value={filtroStatus}
              onChange={(e) => setFiltroStatus(e.target.value)}
              className="filter-select"
            >
              <option value="Todos">Todos os Status</option>
              <option value="Em andamento">Em andamento</option>
              <option value="Pendente">Pendente</option>
              <option value="Aguardando resposta">Aguardando resposta</option>
              <option value="Atendido integralmente">Atendido integralmente</option>
              <option value="Atendido parcialmente">Atendido parcialmente</option>
              <option value="Não atendido">Não atendido</option>
            </select>

            <select
              value={filtroArea}
              onChange={(e) => setFiltroArea(e.target.value)}
              className="filter-select"
            >
              <option value="Todas">Todas as Áreas</option>
              {areas.map(area => (
                <option key={area} value={area}>{area}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Lista de Pedidos */}
        <div className="pedidos-lista">
          {pedidosFiltrados.length === 0 ? (
            <div className="empty-state">
              <span className="empty-icon">📭</span>
              <h3>Nenhum pedido encontrado</h3>
              <p>Ajuste os filtros para ver mais resultados</p>
            </div>
          ) : (
            pedidosFiltrados.map(pedido => {
              // Encontrar projeto correspondente
              const projeto = projetos.find(p =>
                `pedido_${p.area.toLowerCase()}_${p.id_projeto}` === pedido.id_pedido
              );
              return (
                <PedidoCard
                  key={pedido.id_pedido}
                  pedido={pedido}
                  onDetalhar={() => projeto && setProjetoDetalhado(projeto)}
                />
              );
            })
          )}
        </div>

        {/* Modal de Detalhamento */}
        {projetoDetalhado && (
          <ModalDetalhamentoPedido
            projeto={projetoDetalhado}
            onFechar={() => setProjetoDetalhado(null)}
          />
        )}
      </div>
    </div>
  );
};

// ============================================================================
// COMPONENTE: Card do Pedido
// ============================================================================

interface PedidoCardProps {
  pedido: PedidoDiretorConsolidado;
  onDetalhar: () => void;
}

const PedidoCard: React.FC<PedidoCardProps> = ({ pedido, onDetalhar }) => {
  const alerta = calcularStatusAlerta(pedido);
  const icone = getIconeAlerta(alerta);
  const diasRestantes = calcularDiasRestantes(pedido.prazo_retorno);
  const textoRestante = formatarDiasRestantes(diasRestantes);

  return (
    <div className={`pedido-card alerta-${alerta}`}>
      <div className="pedido-header">
        <div className="pedido-meta">
          <span className="pedido-area">{pedido.area}</span>
          <span className="pedido-data">Pedido em {pedido.data_pedido}</span>
        </div>
        <span className="pedido-alerta" title={textoRestante}>
          {icone}
        </span>
      </div>

      <h4 className="pedido-projeto">{pedido.projeto}</h4>
      <p className="pedido-descricao">{pedido.descricao_pedido}</p>

      <div className="pedido-info-grid">
        <div className="info-item">
          <span className="info-label">Canal:</span>
          <span className="info-value">{pedido.canal}</span>
        </div>
        <div className="info-item">
          <span className="info-label">Prazo:</span>
          <span className="info-value">{pedido.prazo_retorno}</span>
        </div>
        <div className="info-item">
          <span className="info-label">Status:</span>
          <span className={`status-badge status-${pedido.status_pedido.toLowerCase().replace(' ', '-')}`}>
            {pedido.status_pedido}
          </span>
        </div>
        <div className="info-item">
          <span className="info-label">Responsável:</span>
          <span className="info-value">👤 {pedido.responsavel_area}</span>
        </div>
      </div>

      {pedido.comentarios_area && (
        <div className="pedido-comentarios">
          <strong>💬 Área:</strong> {pedido.comentarios_area}
        </div>
      )}

      <div className="pedido-footer">
        <div className="pedido-prazo-destaque">
          <span className="prazo-texto">{textoRestante}</span>
        </div>
        <button className="btn-detalhar" onClick={onDetalhar}>
          📋 Detalhar
        </button>
      </div>
    </div>
  );
};

// ============================================================================
// COMPONENTE: Modal de Detalhamento
// ============================================================================

interface ModalDetalhamentoPedidoProps {
  projeto: ProjetoEstrategico;
  onFechar: () => void;
}

const ModalDetalhamentoPedido: React.FC<ModalDetalhamentoPedidoProps> = ({ projeto, onFechar }) => {
  const pedido = projeto.pedido_diretor;

  // Formatar data
  const formatarData = (data?: string) => {
    if (!data) return 'Não informado';
    const d = new Date(data);
    return d.toLocaleDateString('pt-BR');
  };

  // Status com cor
  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'Em andamento':
        return '#3b82f6'; // blue
      case 'Aguardando resposta':
        return '#f59e0b'; // yellow
      case 'Atendido integralmente':
      case 'Atendido parcialmente':
        return '#10b981'; // green
      case 'Não atendido':
        return '#ef4444'; // red
      default:
        return '#6b7280'; // gray
    }
  };

  return (
    <div className="modal-overlay" onClick={onFechar}>
      <div className="modal-detalhamento" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div>
            <h2>📋 Detalhamento do Pedido</h2>
            <p className="modal-area-projeto">
              <span className="badge-area">{projeto.area}</span>
              <span className="projeto-nome">{projeto.nome_projeto}</span>
            </p>
          </div>
          <button className="btn-fechar-modal" onClick={onFechar}>✕</button>
        </div>

        {/* Corpo do Modal */}
        <div className="modal-body">
          {/* Informações Básicas */}
          <section className="detail-section">
            <h3>📌 Informações Básicas</h3>
            <div className="detail-grid">
              <div className="detail-item">
                <label>Data do Pedido:</label>
                <span>{formatarData(pedido.data_pedido)}</span>
              </div>
              <div className="detail-item">
                <label>Canal:</label>
                <span>{pedido.canal || 'Não informado'}</span>
              </div>
              <div className="detail-item full-width">
                <label>Descrição do Pedido:</label>
                <p className="detail-description">{pedido.descricao_pedido || 'Não informado'}</p>
              </div>
              <div className="detail-item full-width">
                <label>Retorno Esperado:</label>
                <p className="detail-description">{pedido.retorno_esperado || 'Não informado'}</p>
              </div>
              <div className="detail-item">
                <label>Prazo de Retorno:</label>
                <span>{formatarData(pedido.prazo_retorno)}</span>
              </div>
            </div>
          </section>

          {/* Status do Pedido */}
          <section className="detail-section">
            <h3>🎯 Status Atual</h3>
            <div className="status-box" style={{
              borderLeft: `4px solid ${getStatusColor(pedido.status_pedido)}`,
              backgroundColor: `${getStatusColor(pedido.status_pedido)}15`
            }}>
              <div className="status-header">
                <span className="status-label">Status:</span>
                <span className="status-value" style={{ color: getStatusColor(pedido.status_pedido) }}>
                  {pedido.status_pedido || 'Pendente'}
                </span>
              </div>

              {/* Detalhes específicos por status */}
              {pedido.status_pedido === 'Em andamento' && (
                <div className="status-details">
                  <div className="detail-item">
                    <label>📅 Data de Início do Andamento:</label>
                    <span>{formatarData(pedido.data_andamento)}</span>
                  </div>
                  <div className="detail-item full-width">
                    <label>🔄 O que está sendo feito:</label>
                    <p className="detail-description">{pedido.descricao_andamento || 'Não informado'}</p>
                  </div>
                </div>
              )}

              {pedido.status_pedido === 'Aguardando resposta' && (
                <div className="status-details">
                  <div className="detail-item">
                    <label>🏢 Setor Aguardando:</label>
                    <span>{pedido.setor_aguardando || 'Não informado'}</span>
                  </div>
                  <div className="detail-item">
                    <label>📅 Data da Solicitação:</label>
                    <span>{formatarData(pedido.data_solicitacao_setor)}</span>
                  </div>
                  <div className="detail-item">
                    <label>⏰ Prazo de Resposta do Setor:</label>
                    <span>{formatarData(pedido.prazo_resposta_setor)}</span>
                  </div>
                </div>
              )}

              {(pedido.status_pedido === 'Atendido integralmente' ||
                pedido.status_pedido === 'Atendido parcialmente' ||
                pedido.status_pedido === 'Não atendido') && (
                <div className="status-details">
                  <div className="detail-item">
                    <label>📅 Data do Atendimento:</label>
                    <span>{formatarData(pedido.data_atendimento)}</span>
                  </div>
                  <div className="detail-item full-width">
                    <label>📝 Como foi atendido:</label>
                    <p className="detail-description">{pedido.descricao_atendimento || 'Não informado'}</p>
                  </div>
                </div>
              )}
            </div>
          </section>

          {/* Contexto do Projeto */}
          <section className="detail-section">
            <h3>🎯 Contexto do Projeto</h3>
            <div className="detail-grid">
              <div className="detail-item full-width">
                <label>Resultado Esperado do Projeto:</label>
                <p className="detail-description">{projeto.resultado_esperado}</p>
              </div>
              <div className="detail-item">
                <label>Fase Atual:</label>
                <span>{projeto.fase_atual}</span>
              </div>
              <div className="detail-item">
                <label>Andamento:</label>
                <span>{projeto.andamento}%</span>
              </div>
              <div className="detail-item full-width">
                <label>Próximos Encaminhamentos:</label>
                <p className="detail-description">{projeto.proximos_encaminhamentos}</p>
              </div>
              {projeto.dependencia && (
                <div className="detail-item full-width">
                  <label>Dependências:</label>
                  <p className="detail-description">{projeto.dependencia}</p>
                </div>
              )}
            </div>
          </section>

          {/* Última Atualização */}
          <section className="detail-section">
            <h3>🕐 Última Atualização</h3>
            <div className="detail-grid">
              <div className="detail-item">
                <label>Data:</label>
                <span>{formatarData(projeto.ultima_atualizacao.data)}</span>
              </div>
              <div className="detail-item">
                <label>Responsável:</label>
                <span>👤 {projeto.ultima_atualizacao.responsavel}</span>
              </div>
            </div>
          </section>
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button className="btn-fechar-completo" onClick={onFechar}>
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
};

export default DashboardDiretor;
