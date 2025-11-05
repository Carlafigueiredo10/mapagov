import React, { useState } from 'react';
import './Artefatos.css';

type PotencialReplicacao = 'alta' | 'media' | 'baixa';
type StatusContinuidade = 'garantida' | 'em_planejamento' | 'em_risco' | 'descontinuada';

interface ItemSustentabilidade {
  id: string;
  resultado: string;
  recursoManutencao: string;
  responsavel: string;
  potencialReplicacao: PotencialReplicacao;
  statusContinuidade: StatusContinuidade;
  justificativa: string;
  planoExpansao: string;
}

export const MatrizSustentabilidade: React.FC = () => {
  const [itens, setItens] = useState<ItemSustentabilidade[]>([
    {
      id: '1',
      resultado: 'Capacitação de servidores',
      recursoManutencao: 'Plataforma EAD institucional',
      responsavel: 'Escola de Governo',
      potencialReplicacao: 'alta',
      statusContinuidade: 'garantida',
      justificativa: 'Conteúdo incorporado ao catálogo permanente de cursos',
      planoExpansao: 'Expandir para outros órgãos do mesmo setor'
    },
    {
      id: '2',
      resultado: 'Dashboard de indicadores',
      recursoManutencao: 'Equipe TI dedicada + servidor cloud',
      responsavel: 'CGRIS',
      potencialReplicacao: 'media',
      statusContinuidade: 'em_planejamento',
      justificativa: 'Dependente de aprovação orçamentária para servidor',
      planoExpansao: 'Replicar para outras coordenações após validação'
    },
    {
      id: '3',
      resultado: 'Processo padronizado de atendimento',
      recursoManutencao: 'Manual e checklist incorporados ao SEI',
      responsavel: 'Coordenação de Atendimento',
      potencialReplicacao: 'alta',
      statusContinuidade: 'garantida',
      justificativa: 'Formalizado em portaria interna',
      planoExpansao: 'Benchmark para outras áreas de atendimento'
    }
  ]);

  const [filtroReplicacao, setFiltroReplicacao] = useState<PotencialReplicacao | 'todos'>('todos');
  const [filtroStatus, setFiltroStatus] = useState<StatusContinuidade | 'todos'>('todos');

  const adicionarItem = () => {
    const novoItem: ItemSustentabilidade = {
      id: Date.now().toString(),
      resultado: '',
      recursoManutencao: '',
      responsavel: '',
      potencialReplicacao: 'media',
      statusContinuidade: 'em_planejamento',
      justificativa: '',
      planoExpansao: ''
    };
    setItens([...itens, novoItem]);
  };

  const removerItem = (id: string) => {
    setItens(itens.filter(i => i.id !== id));
  };

  const atualizarItem = (id: string, campo: keyof ItemSustentabilidade, valor: any) => {
    setItens(itens.map(i => i.id === id ? { ...i, [campo]: valor } : i));
  };

  const getPotencialColor = (potencial: PotencialReplicacao): string => {
    const colors = {
      alta: '#198754',
      media: '#ffc107',
      baixa: '#dc3545'
    };
    return colors[potencial];
  };

  const getPotencialLabel = (potencial: PotencialReplicacao): string => {
    const labels = {
      alta: '🟢 Alta',
      media: '🟡 Média',
      baixa: '🔴 Baixa'
    };
    return labels[potencial];
  };

  const getStatusColor = (status: StatusContinuidade): string => {
    const colors = {
      garantida: '#198754',
      em_planejamento: '#0d6efd',
      em_risco: '#ffc107',
      descontinuada: '#6c757d'
    };
    return colors[status];
  };

  const getStatusLabel = (status: StatusContinuidade): string => {
    const labels = {
      garantida: '✅ Garantida',
      em_planejamento: '📋 Em Planejamento',
      em_risco: '⚠️ Em Risco',
      descontinuada: '❌ Descontinuada'
    };
    return labels[status];
  };

  const exportarTxt = () => {
    let conteudo = '═══════════════════════════════════════════════════════════\n';
    conteudo += '  MATRIZ DE SUSTENTABILIDADE E REPLICABILIDADE\n';
    conteudo += '  Domínio 7 - Impacto e Aprendizado\n';
    conteudo += '═══════════════════════════════════════════════════════════\n\n';

    conteudo += '♻️ PLANO DE CONTINUIDADE E EXPANSÃO\n\n';

    itens.forEach((item, index) => {
      conteudo += `${index + 1}. ${item.resultado || '(não identificado)'}\n`;
      conteudo += `   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
      conteudo += `   🔧 Recurso para Manter:     ${item.recursoManutencao || '—'}\n`;
      conteudo += `   👤 Responsável:             ${item.responsavel || '—'}\n`;
      conteudo += `   📊 Potencial de Replicação: ${getPotencialLabel(item.potencialReplicacao)}\n`;
      conteudo += `   ✅ Status Continuidade:     ${getStatusLabel(item.statusContinuidade)}\n`;
      conteudo += `   📝 Justificativa:\n`;
      conteudo += `      ${item.justificativa || '—'}\n`;
      conteudo += `   🚀 Plano de Expansão:\n`;
      conteudo += `      ${item.planoExpansao || '—'}\n`;
      conteudo += '\n';
    });

    // Estatísticas
    const totalAlta = itens.filter(i => i.potencialReplicacao === 'alta').length;
    const totalMedia = itens.filter(i => i.potencialReplicacao === 'media').length;
    const totalBaixa = itens.filter(i => i.potencialReplicacao === 'baixa').length;
    const totalGarantida = itens.filter(i => i.statusContinuidade === 'garantida').length;
    const totalRisco = itens.filter(i => i.statusContinuidade === 'em_risco').length;

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += '📊 ESTATÍSTICAS\n\n';
    conteudo += `Total de resultados: ${itens.length}\n\n`;
    conteudo += `Potencial de Replicação:\n`;
    conteudo += `  Alta: ${totalAlta}\n`;
    conteudo += `  Média: ${totalMedia}\n`;
    conteudo += `  Baixa: ${totalBaixa}\n\n`;
    conteudo += `Continuidade:\n`;
    conteudo += `  Garantida: ${totalGarantida}\n`;
    conteudo += `  Em Risco: ${totalRisco}\n`;
    conteudo += '\n';

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += '📄 Recomendações de políticas públicas\n';
    conteudo += `Exportado em: ${new Date().toLocaleString('pt-BR')}\n`;

    const blob = new Blob([conteudo], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'matriz_sustentabilidade.txt';
    link.click();
    URL.revokeObjectURL(url);
  };

  const itensFiltrados = itens.filter(i => {
    const replicacaoMatch = filtroReplicacao === 'todos' || i.potencialReplicacao === filtroReplicacao;
    const statusMatch = filtroStatus === 'todos' || i.statusContinuidade === filtroStatus;
    return replicacaoMatch && statusMatch;
  });

  const totalAlta = itens.filter(i => i.potencialReplicacao === 'alta').length;
  const totalMedia = itens.filter(i => i.potencialReplicacao === 'media').length;
  const totalBaixa = itens.filter(i => i.potencialReplicacao === 'baixa').length;
  const totalGarantida = itens.filter(i => i.statusContinuidade === 'garantida').length;
  const totalRisco = itens.filter(i => i.statusContinuidade === 'em_risco').length;

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <div>
          <h2>♻️ Matriz de Sustentabilidade e Replicabilidade</h2>
          <p className="artefato-descricao">
            Planejar a continuidade e disseminação das práticas bem-sucedidas.
          </p>
        </div>
        <button className="btn-exportar" onClick={exportarTxt}>
          📥 Exportar TXT
        </button>
      </div>

      {/* Estatísticas */}
      <div className="estatisticas-stakeholders">
        <div className="stat-card stat-concluido">
          <div className="stat-icon">🟢</div>
          <div className="stat-info">
            <div className="stat-value">{totalAlta}</div>
            <div className="stat-label">Alta Replicação</div>
          </div>
        </div>
        <div className="stat-card stat-analise">
          <div className="stat-icon">🟡</div>
          <div className="stat-info">
            <div className="stat-value">{totalMedia}</div>
            <div className="stat-label">Média Replicação</div>
          </div>
        </div>
        <div className="stat-card stat-critico">
          <div className="stat-icon">🔴</div>
          <div className="stat-info">
            <div className="stat-value">{totalBaixa}</div>
            <div className="stat-label">Baixa Replicação</div>
          </div>
        </div>
        <div className="stat-card stat-concluido">
          <div className="stat-icon">✅</div>
          <div className="stat-info">
            <div className="stat-value">{totalGarantida}</div>
            <div className="stat-label">Continuidade Garantida</div>
          </div>
        </div>
      </div>

      {/* Alertas */}
      {totalRisco > 0 && (
        <div className="alerta-pendencias" style={{ borderLeftColor: '#ffc107' }}>
          <span className="alerta-icon">⚠️</span>
          <strong>Atenção:</strong> {totalRisco} resultado(s) com continuidade em risco. Revisar planos.
        </div>
      )}

      <div className="artefato-controls">
        <button className="btn-adicionar" onClick={adicionarItem}>
          ➕ Adicionar Resultado
        </button>

        <div className="filtros-container" style={{ display: 'flex', gap: '1rem', marginLeft: 'auto' }}>
          <div className="filtro-status">
            <label>Replicação:</label>
            <select
              value={filtroReplicacao}
              onChange={(e) => setFiltroReplicacao(e.target.value as PotencialReplicacao | 'todos')}
            >
              <option value="todos">Todas</option>
              <option value="alta">🟢 Alta</option>
              <option value="media">🟡 Média</option>
              <option value="baixa">🔴 Baixa</option>
            </select>
          </div>

          <div className="filtro-status">
            <label>Status:</label>
            <select
              value={filtroStatus}
              onChange={(e) => setFiltroStatus(e.target.value as StatusContinuidade | 'todos')}
            >
              <option value="todos">Todos</option>
              <option value="garantida">✅ Garantida</option>
              <option value="em_planejamento">📋 Em Planejamento</option>
              <option value="em_risco">⚠️ Em Risco</option>
              <option value="descontinuada">❌ Descontinuada</option>
            </select>
          </div>
        </div>
      </div>

      {/* Cards de Sustentabilidade */}
      <div className="comunicacao-cards-grid">
        {itensFiltrados.map((item) => (
          <div
            key={item.id}
            className="comunicacao-card"
            style={{ borderLeft: `4px solid ${getPotencialColor(item.potencialReplicacao)}` }}
          >
            <div className="comunicacao-card-header">
              <div className="canal-badge" style={{ backgroundColor: getPotencialColor(item.potencialReplicacao) }}>
                {getPotencialLabel(item.potencialReplicacao)}
              </div>
              <div className="canal-badge" style={{ backgroundColor: getStatusColor(item.statusContinuidade) }}>
                {getStatusLabel(item.statusContinuidade)}
              </div>
              <button
                className="btn-remover-card"
                onClick={() => removerItem(item.id)}
                title="Remover"
              >
                ✕
              </button>
            </div>

            <div className="comunicacao-form">
              <div className="form-group-comunicacao">
                <label>🎯 Resultado Alcançado</label>
                <input
                  type="text"
                  value={item.resultado}
                  onChange={(e) => atualizarItem(item.id, 'resultado', e.target.value)}
                  placeholder="Ex: Capacitação de servidores, Dashboard de indicadores..."
                />
              </div>

              <div className="form-group-comunicacao">
                <label>🔧 Recurso para Manutenção</label>
                <textarea
                  value={item.recursoManutencao}
                  onChange={(e) => atualizarItem(item.id, 'recursoManutencao', e.target.value)}
                  placeholder="Que recursos (equipe, orçamento, tecnologia) são necessários para manter?"
                  rows={2}
                />
              </div>

              <div className="form-row">
                <div className="form-group-comunicacao">
                  <label>👤 Responsável</label>
                  <input
                    type="text"
                    value={item.responsavel}
                    onChange={(e) => atualizarItem(item.id, 'responsavel', e.target.value)}
                    placeholder="Área ou pessoa"
                  />
                </div>

                <div className="form-group-comunicacao">
                  <label>📊 Potencial de Replicação</label>
                  <select
                    value={item.potencialReplicacao}
                    onChange={(e) => atualizarItem(item.id, 'potencialReplicacao', e.target.value)}
                    style={{ backgroundColor: getPotencialColor(item.potencialReplicacao), color: 'white' }}
                  >
                    <option value="alta">🟢 Alta</option>
                    <option value="media">🟡 Média</option>
                    <option value="baixa">🔴 Baixa</option>
                  </select>
                </div>
              </div>

              <div className="form-group-comunicacao">
                <label>✅ Status de Continuidade</label>
                <select
                  value={item.statusContinuidade}
                  onChange={(e) => atualizarItem(item.id, 'statusContinuidade', e.target.value)}
                  style={{ backgroundColor: getStatusColor(item.statusContinuidade), color: 'white' }}
                >
                  <option value="garantida">✅ Garantida</option>
                  <option value="em_planejamento">📋 Em Planejamento</option>
                  <option value="em_risco">⚠️ Em Risco</option>
                  <option value="descontinuada">❌ Descontinuada</option>
                </select>
              </div>

              <div className="form-group-comunicacao">
                <label>📝 Justificativa</label>
                <textarea
                  value={item.justificativa}
                  onChange={(e) => atualizarItem(item.id, 'justificativa', e.target.value)}
                  placeholder="Por que a continuidade está neste status?"
                  rows={2}
                />
              </div>

              <div className="form-group-comunicacao">
                <label>🚀 Plano de Expansão/Replicação</label>
                <textarea
                  value={item.planoExpansao}
                  onChange={(e) => atualizarItem(item.id, 'planoExpansao', e.target.value)}
                  placeholder="Como e onde essa prática pode ser replicada?"
                  rows={2}
                  style={{ backgroundColor: '#e6f3ff' }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      {itensFiltrados.length === 0 && (
        <div className="empty-state">
          <p>Nenhum resultado encontrado para os filtros selecionados.</p>
        </div>
      )}
    </div>
  );
};

export default MatrizSustentabilidade;
