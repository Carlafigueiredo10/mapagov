import React, { useState } from 'react';
import './Artefatos.css';

type StatusEtapa = 'planejada' | 'em_andamento' | 'concluida' | 'atrasada';

interface EtapaProjeto {
  id: string;
  etapa: string;
  inicio: string;
  fim: string;
  responsavel: string;
  status: StatusEtapa;
  progresso: number; // 0 a 100
}

export const CronogramaTimeline: React.FC = () => {
  const [etapas, setEtapas] = useState<EtapaProjeto[]>([
    {
      id: '1',
      etapa: 'Diagnóstico',
      inicio: '2025-03-01',
      fim: '2025-03-30',
      responsavel: 'Equipe A',
      status: 'concluida',
      progresso: 100
    },
    {
      id: '2',
      etapa: 'Execução piloto',
      inicio: '2025-04-01',
      fim: '2025-05-31',
      responsavel: 'Coordenação',
      status: 'em_andamento',
      progresso: 60
    },
    {
      id: '3',
      etapa: 'Avaliação e relatório',
      inicio: '2025-06-01',
      fim: '2025-06-15',
      responsavel: 'CGRIS',
      status: 'planejada',
      progresso: 0
    }
  ]);

  const adicionarEtapa = () => {
    const novaEtapa: EtapaProjeto = {
      id: Date.now().toString(),
      etapa: '',
      inicio: '',
      fim: '',
      responsavel: '',
      status: 'planejada',
      progresso: 0
    };
    setEtapas([...etapas, novaEtapa]);
  };

  const removerEtapa = (id: string) => {
    setEtapas(etapas.filter(e => e.id !== id));
  };

  const atualizarEtapa = (id: string, campo: keyof EtapaProjeto, valor: string | number | StatusEtapa) => {
    setEtapas(etapas.map(e =>
      e.id === id ? { ...e, [campo]: valor } : e
    ));
  };

  const exportarTxt = () => {
    let conteudo = '═══════════════════════════════════════════════════════════\n';
    conteudo += '  CRONOGRAMA SIMPLIFICADO / TIMELINE DINÂMICA\n';
    conteudo += '  Domínio 4 - Capacidades e Atividades\n';
    conteudo += '═══════════════════════════════════════════════════════════\n\n';

    etapas.forEach((etapa, index) => {
      conteudo += `${index + 1}. ${etapa.etapa || '(sem título)'}\n`;
      conteudo += `   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
      conteudo += `   📅 Início:       ${etapa.inicio || '—'}\n`;
      conteudo += `   📅 Fim:          ${etapa.fim || '—'}\n`;
      conteudo += `   👤 Responsável:  ${etapa.responsavel || '—'}\n`;
      conteudo += `   📊 Status:       ${getStatusIcon(etapa.status)} ${getStatusLabel(etapa.status)}\n`;
      conteudo += `   📈 Progresso:    ${etapa.progresso}%\n`;
      conteudo += '\n';
    });

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += `Exportado em: ${new Date().toLocaleString('pt-BR')}\n`;

    const blob = new Blob([conteudo], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'cronograma_timeline.txt';
    link.click();
    URL.revokeObjectURL(url);
  };

  const getStatusIcon = (status: StatusEtapa): string => {
    const icons = {
      planejada: '⚙️',
      em_andamento: '⏳',
      concluida: '✅',
      atrasada: '🔴'
    };
    return icons[status];
  };

  const getStatusLabel = (status: StatusEtapa): string => {
    const labels = {
      planejada: 'Planejada',
      em_andamento: 'Em andamento',
      concluida: 'Concluída',
      atrasada: 'Atrasada'
    };
    return labels[status];
  };

  const getStatusColor = (status: StatusEtapa): string => {
    const colors = {
      planejada: '#6c757d',
      em_andamento: '#0d6efd',
      concluida: '#198754',
      atrasada: '#dc3545'
    };
    return colors[status];
  };

  const getProgressColor = (progresso: number): string => {
    if (progresso === 100) return '#198754';
    if (progresso >= 50) return '#0d6efd';
    if (progresso > 0) return '#ffc107';
    return '#e9ecef';
  };

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <div>
          <h2>📅 Cronograma Simplificado / Timeline Dinâmica</h2>
          <p className="artefato-descricao">
            Visualizar o andamento e dependências das atividades ao longo do tempo.
          </p>
        </div>
        <button className="btn-exportar" onClick={exportarTxt}>
          📥 Exportar TXT
        </button>
      </div>

      <div className="artefato-controls">
        <button className="btn-adicionar" onClick={adicionarEtapa}>
          ➕ Adicionar Etapa
        </button>
      </div>

      <div className="timeline-container">
        <div className="timeline-table">
          <table>
            <thead>
              <tr>
                <th style={{ width: '25%' }}>Etapa</th>
                <th style={{ width: '12%' }}>Início</th>
                <th style={{ width: '12%' }}>Fim</th>
                <th style={{ width: '18%' }}>Responsável</th>
                <th style={{ width: '15%' }}>Status</th>
                <th style={{ width: '15%' }}>Progresso</th>
                <th style={{ width: '3%' }}></th>
              </tr>
            </thead>
            <tbody>
              {etapas.map((etapa) => (
                <tr key={etapa.id}>
                  <td>
                    <input
                      type="text"
                      value={etapa.etapa}
                      onChange={(e) => atualizarEtapa(etapa.id, 'etapa', e.target.value)}
                      placeholder="Nome da etapa"
                      className="input-inline"
                    />
                  </td>
                  <td>
                    <input
                      type="date"
                      value={etapa.inicio}
                      onChange={(e) => atualizarEtapa(etapa.id, 'inicio', e.target.value)}
                      className="input-inline input-date"
                    />
                  </td>
                  <td>
                    <input
                      type="date"
                      value={etapa.fim}
                      onChange={(e) => atualizarEtapa(etapa.id, 'fim', e.target.value)}
                      className="input-inline input-date"
                    />
                  </td>
                  <td>
                    <input
                      type="text"
                      value={etapa.responsavel}
                      onChange={(e) => atualizarEtapa(etapa.id, 'responsavel', e.target.value)}
                      placeholder="Responsável"
                      className="input-inline"
                    />
                  </td>
                  <td>
                    <select
                      value={etapa.status}
                      onChange={(e) => atualizarEtapa(etapa.id, 'status', e.target.value as StatusEtapa)}
                      className="select-inline"
                      style={{ backgroundColor: getStatusColor(etapa.status), color: 'white' }}
                    >
                      <option value="planejada">⚙️ Planejada</option>
                      <option value="em_andamento">⏳ Em andamento</option>
                      <option value="concluida">✅ Concluída</option>
                      <option value="atrasada">🔴 Atrasada</option>
                    </select>
                  </td>
                  <td>
                    <div className="progress-cell">
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={etapa.progresso}
                        onChange={(e) => atualizarEtapa(etapa.id, 'progresso', parseInt(e.target.value))}
                        className="progress-slider"
                      />
                      <span className="progress-label">{etapa.progresso}%</span>
                    </div>
                  </td>
                  <td>
                    <button
                      className="btn-remover-table"
                      onClick={() => removerEtapa(etapa.id)}
                      title="Remover etapa"
                    >
                      ✕
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Timeline Visual (Gantt simplificado) */}
        <div className="timeline-visual">
          <h3>📊 Visualização Timeline</h3>
          <div className="gantt-container">
            {etapas.map((etapa) => (
              <div key={etapa.id} className="gantt-row">
                <div className="gantt-label">
                  {etapa.etapa || '(sem título)'}
                  <span className="gantt-dates">
                    {etapa.inicio && etapa.fim
                      ? `${new Date(etapa.inicio).toLocaleDateString('pt-BR')} - ${new Date(etapa.fim).toLocaleDateString('pt-BR')}`
                      : '—'}
                  </span>
                </div>
                <div className="gantt-bar-container">
                  <div
                    className="gantt-bar"
                    style={{
                      backgroundColor: getStatusColor(etapa.status),
                      width: `${etapa.progresso}%`
                    }}
                  >
                    <span className="gantt-bar-text">{etapa.progresso}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {etapas.length === 0 && (
        <div className="empty-state">
          <p>Nenhuma etapa cadastrada. Clique em "Adicionar Etapa" para começar.</p>
        </div>
      )}

      <style>{`
        .timeline-container {
          display: flex;
          flex-direction: column;
          gap: 30px;
          margin-top: 20px;
        }

        .timeline-table table {
          width: 100%;
          border-collapse: collapse;
          background: white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.05);
          border-radius: 8px;
          overflow: hidden;
        }

        .timeline-table th {
          background: #f8f9fa;
          padding: 12px;
          text-align: left;
          font-weight: 600;
          border-bottom: 2px solid #dee2e6;
          font-size: 14px;
        }

        .timeline-table td {
          padding: 10px;
          border-bottom: 1px solid #dee2e6;
        }

        .input-inline {
          width: 100%;
          padding: 6px 8px;
          border: 1px solid #ced4da;
          border-radius: 4px;
          font-size: 14px;
        }

        .input-date {
          font-family: inherit;
        }

        .select-inline {
          width: 100%;
          padding: 6px 8px;
          border: 1px solid #ced4da;
          border-radius: 4px;
          font-size: 13px;
          font-weight: 500;
        }

        .progress-cell {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .progress-slider {
          flex: 1;
          height: 6px;
          -webkit-appearance: none;
          appearance: none;
          background: #e9ecef;
          border-radius: 3px;
          outline: none;
        }

        .progress-slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 16px;
          height: 16px;
          background: #0d6efd;
          border-radius: 50%;
          cursor: pointer;
        }

        .progress-slider::-moz-range-thumb {
          width: 16px;
          height: 16px;
          background: #0d6efd;
          border-radius: 50%;
          cursor: pointer;
          border: none;
        }

        .progress-label {
          font-weight: 600;
          font-size: 13px;
          min-width: 40px;
          text-align: right;
        }

        .btn-remover-table {
          background: #dc3545;
          color: white;
          border: none;
          border-radius: 50%;
          width: 24px;
          height: 24px;
          cursor: pointer;
          font-size: 14px;
          transition: all 0.2s;
        }

        .btn-remover-table:hover {
          background: #bb2d3b;
          transform: scale(1.1);
        }

        .timeline-visual {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .timeline-visual h3 {
          margin-bottom: 20px;
          font-size: 18px;
          color: #212529;
        }

        .gantt-container {
          display: flex;
          flex-direction: column;
          gap: 15px;
        }

        .gantt-row {
          display: grid;
          grid-template-columns: 250px 1fr;
          gap: 15px;
          align-items: center;
        }

        .gantt-label {
          display: flex;
          flex-direction: column;
          gap: 4px;
          font-weight: 500;
          font-size: 14px;
        }

        .gantt-dates {
          font-size: 12px;
          color: #6c757d;
          font-weight: 400;
        }

        .gantt-bar-container {
          background: #e9ecef;
          height: 32px;
          border-radius: 6px;
          overflow: hidden;
          position: relative;
        }

        .gantt-bar {
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: flex-end;
          padding-right: 10px;
          transition: width 0.3s ease;
          position: relative;
        }

        .gantt-bar-text {
          color: white;
          font-size: 12px;
          font-weight: 600;
        }

        @media (max-width: 768px) {
          .timeline-table {
            overflow-x: auto;
          }

          .gantt-row {
            grid-template-columns: 1fr;
            gap: 10px;
          }
        }
      `}</style>
    </div>
  );
};

export default CronogramaTimeline;
