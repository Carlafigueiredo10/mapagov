import React, { useState } from 'react';
import './Artefatos.css';

type EstrategiaTratamento = 'evitar' | 'reduzir' | 'transferir' | 'aceitar';
type StatusAcao = 'pendente' | 'em_andamento' | 'concluida' | 'atrasada';

interface TratamentoRisco {
  id: string;
  risco: string;
  estrategia: EstrategiaTratamento;
  acaoPreventiva: string;
  responsavel: string;
  prazo: string;
  status: StatusAcao;
  observacoes: string;
}

export const PlanoTratamentoRiscos: React.FC = () => {
  const [tratamentos, setTratamentos] = useState<TratamentoRisco[]>([
    {
      id: '1',
      risco: 'Corte orçamentário',
      estrategia: 'reduzir',
      acaoPreventiva: 'Revisar escopo e priorizar entregas essenciais',
      responsavel: 'Coordenação',
      prazo: '2025-06-30',
      status: 'em_andamento',
      observacoes: 'Plano de contingência em elaboração'
    },
    {
      id: '2',
      risco: 'Falha tecnológica crítica',
      estrategia: 'evitar',
      acaoPreventiva: 'Criar cópia de segurança semanal e testar restauração',
      responsavel: 'TI',
      prazo: '2025-12-31',
      status: 'concluida',
      observacoes: 'Backup automático implementado'
    },
    {
      id: '3',
      risco: 'Atraso de fornecedor externo',
      estrategia: 'transferir',
      acaoPreventiva: 'Incluir cláusula de penalidade no contrato',
      responsavel: 'Jurídico',
      prazo: '2025-05-15',
      status: 'pendente',
      observacoes: 'Aguardando análise jurídica'
    }
  ]);

  const [filtroStatus, setFiltroStatus] = useState<StatusAcao | 'todos'>('todos');

  const adicionarTratamento = () => {
    const novoTratamento: TratamentoRisco = {
      id: Date.now().toString(),
      risco: '',
      estrategia: 'reduzir',
      acaoPreventiva: '',
      responsavel: '',
      prazo: '',
      status: 'pendente',
      observacoes: ''
    };
    setTratamentos([...tratamentos, novoTratamento]);
  };

  const removerTratamento = (id: string) => {
    setTratamentos(tratamentos.filter(t => t.id !== id));
  };

  const atualizarTratamento = (id: string, campo: keyof TratamentoRisco, valor: any) => {
    setTratamentos(tratamentos.map(t => t.id === id ? { ...t, [campo]: valor } : t));
  };

  const getEstrategiaIcon = (estrategia: EstrategiaTratamento): string => {
    const icons = {
      evitar: '🚫',
      reduzir: '📉',
      transferir: '🔄',
      aceitar: '✅'
    };
    return icons[estrategia];
  };

  const getEstrategiaLabel = (estrategia: EstrategiaTratamento): string => {
    const labels = {
      evitar: 'Evitar',
      reduzir: 'Reduzir',
      transferir: 'Transferir',
      aceitar: 'Aceitar'
    };
    return labels[estrategia];
  };

  const getStatusColor = (status: StatusAcao): string => {
    const colors = {
      pendente: '#ffc107',
      em_andamento: '#0d6efd',
      concluida: '#198754',
      atrasada: '#dc3545'
    };
    return colors[status];
  };

  const getStatusLabel = (status: StatusAcao): string => {
    const labels = {
      pendente: '⏳ Pendente',
      em_andamento: '⚙️ Em andamento',
      concluida: '✅ Concluída',
      atrasada: '🔴 Atrasada'
    };
    return labels[status];
  };

  const verificarAtraso = (prazo: string, status: StatusAcao): boolean => {
    if (status === 'concluida') return false;
    if (!prazo) return false;
    return new Date(prazo) < new Date();
  };

  const exportarTxt = () => {
    let conteudo = '═══════════════════════════════════════════════════════════\n';
    conteudo += '  PLANO DE TRATAMENTO DE RISCOS\n';
    conteudo += '  Domínio 6 - Incerteza e Contexto\n';
    conteudo += '═══════════════════════════════════════════════════════════\n\n';

    conteudo += '🛡️ AÇÕES DE TRATAMENTO\n\n';

    tratamentos.forEach((tratamento, index) => {
      conteudo += `${index + 1}. ${tratamento.risco || '(não identificado)'}\n`;
      conteudo += `   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
      conteudo += `   📋 Estratégia:       ${getEstrategiaIcon(tratamento.estrategia)} ${getEstrategiaLabel(tratamento.estrategia)}\n`;
      conteudo += `   🎯 Ação Preventiva:  ${tratamento.acaoPreventiva || '—'}\n`;
      conteudo += `   👤 Responsável:      ${tratamento.responsavel || '—'}\n`;
      conteudo += `   📅 Prazo:            ${tratamento.prazo ? new Date(tratamento.prazo).toLocaleDateString('pt-BR') : '—'}\n`;
      conteudo += `   📊 Status:           ${getStatusLabel(tratamento.status)}\n`;
      conteudo += `   📝 Observações:      ${tratamento.observacoes || '—'}\n`;
      conteudo += '\n';
    });

    // Estatísticas
    const totalPendente = tratamentos.filter(t => t.status === 'pendente').length;
    const totalAndamento = tratamentos.filter(t => t.status === 'em_andamento').length;
    const totalConcluida = tratamentos.filter(t => t.status === 'concluida').length;
    const totalAtrasada = tratamentos.filter(t => verificarAtraso(t.prazo, t.status)).length;

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += '📊 ESTATÍSTICAS\n\n';
    conteudo += `Total de ações: ${tratamentos.length}\n`;
    conteudo += `Pendentes: ${totalPendente}\n`;
    conteudo += `Em andamento: ${totalAndamento}\n`;
    conteudo += `Concluídas: ${totalConcluida}\n`;
    conteudo += `Atrasadas: ${totalAtrasada}\n`;
    conteudo += '\n';

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += `Exportado em: ${new Date().toLocaleString('pt-BR')}\n`;

    const blob = new Blob([conteudo], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'plano_tratamento_riscos.txt';
    link.click();
    URL.revokeObjectURL(url);
  };

  const tratamentosFiltrados = filtroStatus === 'todos'
    ? tratamentos
    : tratamentos.filter(t => t.status === filtroStatus);

  const totalPendente = tratamentos.filter(t => t.status === 'pendente').length;
  const totalAndamento = tratamentos.filter(t => t.status === 'em_andamento').length;
  const totalConcluida = tratamentos.filter(t => t.status === 'concluida').length;
  const totalAtrasada = tratamentos.filter(t => verificarAtraso(t.prazo, t.status)).length;

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <div>
          <h2>🛡️ Plano de Tratamento de Riscos</h2>
          <p className="artefato-descricao">
            Definir ações preventivas e responsáveis para mitigar riscos prioritários.
          </p>
        </div>
        <button className="btn-exportar" onClick={exportarTxt}>
          📥 Exportar TXT
        </button>
      </div>

      {/* Estatísticas por Status */}
      <div className="estatisticas-stakeholders">
        <div className="stat-card stat-pendente">
          <div className="stat-icon">⏳</div>
          <div className="stat-info">
            <div className="stat-value">{totalPendente}</div>
            <div className="stat-label">Pendentes</div>
          </div>
        </div>
        <div className="stat-card stat-analise">
          <div className="stat-icon">⚙️</div>
          <div className="stat-info">
            <div className="stat-value">{totalAndamento}</div>
            <div className="stat-label">Em Andamento</div>
          </div>
        </div>
        <div className="stat-card stat-concluido">
          <div className="stat-icon">✅</div>
          <div className="stat-info">
            <div className="stat-value">{totalConcluida}</div>
            <div className="stat-label">Concluídas</div>
          </div>
        </div>
        <div className="stat-card stat-critico">
          <div className="stat-icon">🔴</div>
          <div className="stat-info">
            <div className="stat-value">{totalAtrasada}</div>
            <div className="stat-label">Atrasadas</div>
          </div>
        </div>
      </div>

      {/* Alerta de Ações Atrasadas */}
      {totalAtrasada > 0 && (
        <div className="alerta-pendencias" style={{ borderLeftColor: '#dc3545' }}>
          <span className="alerta-icon">⚠️</span>
          <strong>Atenção:</strong> {totalAtrasada} ação(ões) atrasada(s)! Revisar prazos.
        </div>
      )}

      <div className="artefato-controls">
        <button className="btn-adicionar" onClick={adicionarTratamento}>
          ➕ Adicionar Ação de Tratamento
        </button>

        <div className="filtro-status">
          <label>Filtrar por status:</label>
          <select
            value={filtroStatus}
            onChange={(e) => setFiltroStatus(e.target.value as StatusAcao | 'todos')}
          >
            <option value="todos">Todos</option>
            <option value="pendente">Pendente</option>
            <option value="em_andamento">Em andamento</option>
            <option value="concluida">Concluída</option>
            <option value="atrasada">Atrasada</option>
          </select>
        </div>
      </div>

      {/* Cards de Tratamento */}
      <div className="comunicacao-cards-grid">
        {tratamentosFiltrados.map((tratamento) => {
          const isAtrasado = verificarAtraso(tratamento.prazo, tratamento.status);
          return (
            <div key={tratamento.id} className="comunicacao-card" style={isAtrasado ? { borderLeft: '4px solid #dc3545' } : {}}>
              <div className="comunicacao-card-header">
                <div className="canal-badge" style={{ backgroundColor: isAtrasado ? '#dc3545' : '#0d6efd' }}>
                  {getEstrategiaIcon(tratamento.estrategia)} {getEstrategiaLabel(tratamento.estrategia)}
                </div>
                <button
                  className="btn-remover-card"
                  onClick={() => removerTratamento(tratamento.id)}
                  title="Remover"
                >
                  ✕
                </button>
              </div>

              <div className="comunicacao-form">
                <div className="form-group-comunicacao">
                  <label>⚠️ Risco</label>
                  <input
                    type="text"
                    value={tratamento.risco}
                    onChange={(e) => atualizarTratamento(tratamento.id, 'risco', e.target.value)}
                    placeholder="Descrição do risco a ser tratado"
                  />
                </div>

                <div className="form-group-comunicacao">
                  <label>📋 Estratégia de Tratamento</label>
                  <select
                    value={tratamento.estrategia}
                    onChange={(e) => atualizarTratamento(tratamento.id, 'estrategia', e.target.value)}
                  >
                    <option value="evitar">🚫 Evitar (eliminar a causa)</option>
                    <option value="reduzir">📉 Reduzir (mitigar impacto/probabilidade)</option>
                    <option value="transferir">🔄 Transferir (repassar a terceiros)</option>
                    <option value="aceitar">✅ Aceitar (monitorar sem ação)</option>
                  </select>
                </div>

                <div className="form-group-comunicacao">
                  <label>🎯 Ação Preventiva</label>
                  <textarea
                    value={tratamento.acaoPreventiva}
                    onChange={(e) => atualizarTratamento(tratamento.id, 'acaoPreventiva', e.target.value)}
                    placeholder="Descreva a ação preventiva que será tomada..."
                    rows={2}
                  />
                </div>

                <div className="form-row">
                  <div className="form-group-comunicacao">
                    <label>👤 Responsável</label>
                    <input
                      type="text"
                      value={tratamento.responsavel}
                      onChange={(e) => atualizarTratamento(tratamento.id, 'responsavel', e.target.value)}
                      placeholder="Quem executará?"
                    />
                  </div>

                  <div className="form-group-comunicacao">
                    <label>📅 Prazo</label>
                    <input
                      type="date"
                      value={tratamento.prazo}
                      onChange={(e) => atualizarTratamento(tratamento.id, 'prazo', e.target.value)}
                    />
                  </div>
                </div>

                <div className="form-group-comunicacao">
                  <label>📊 Status da Ação</label>
                  <select
                    value={tratamento.status}
                    onChange={(e) => atualizarTratamento(tratamento.id, 'status', e.target.value)}
                    style={{ backgroundColor: getStatusColor(tratamento.status), color: 'white' }}
                  >
                    <option value="pendente">⏳ Pendente</option>
                    <option value="em_andamento">⚙️ Em andamento</option>
                    <option value="concluida">✅ Concluída</option>
                    <option value="atrasada">🔴 Atrasada</option>
                  </select>
                </div>

                <div className="form-group-comunicacao">
                  <label>📝 Observações</label>
                  <textarea
                    value={tratamento.observacoes}
                    onChange={(e) => atualizarTratamento(tratamento.id, 'observacoes', e.target.value)}
                    placeholder="Notas adicionais sobre o tratamento..."
                    rows={2}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {tratamentosFiltrados.length === 0 && (
        <div className="empty-state">
          <p>Nenhuma ação de tratamento encontrada para o filtro selecionado.</p>
        </div>
      )}
    </div>
  );
};

export default PlanoTratamentoRiscos;
