import React, { useState } from 'react';
import './Artefatos.css';

type StatusAtividade = 'planejada' | 'em_execucao' | 'concluida' | 'bloqueada';

interface AtividadeProgresso {
  id: string;
  atividade: string;
  status: StatusAtividade;
  percentual: number; // 0 a 100
  ultimaAtualizacao: string;
  observacoes: string;
}

export const PainelProgressoOperacional: React.FC = () => {
  const [atividades, setAtividades] = useState<AtividadeProgresso[]>([
    {
      id: '1',
      atividade: 'Diagnóstico concluído',
      status: 'concluida',
      percentual: 100,
      ultimaAtualizacao: '2025-03-12',
      observacoes: 'Entregue no prazo'
    },
    {
      id: '2',
      atividade: 'Treinamento da equipe',
      status: 'em_execucao',
      percentual: 70,
      ultimaAtualizacao: '2025-04-20',
      observacoes: 'Aguardando feedback'
    },
    {
      id: '3',
      atividade: 'Avaliação final',
      status: 'planejada',
      percentual: 0,
      ultimaAtualizacao: '',
      observacoes: 'Previsto para junho'
    }
  ]);

  const adicionarAtividade = () => {
    const novaAtividade: AtividadeProgresso = {
      id: Date.now().toString(),
      atividade: '',
      status: 'planejada',
      percentual: 0,
      ultimaAtualizacao: new Date().toISOString().split('T')[0],
      observacoes: ''
    };
    setAtividades([...atividades, novaAtividade]);
  };

  const removerAtividade = (id: string) => {
    setAtividades(atividades.filter(a => a.id !== id));
  };

  const atualizarAtividade = (id: string, campo: keyof AtividadeProgresso, valor: string | number | StatusAtividade) => {
    setAtividades(atividades.map(a =>
      a.id === id ? { ...a, [campo]: valor } : a
    ));
  };

  const exportarTxt = () => {
    let conteudo = '═══════════════════════════════════════════════════════════\n';
    conteudo += '  PAINEL DE PROGRESSO OPERACIONAL\n';
    conteudo += '  Domínio 4 - Capacidades e Atividades\n';
    conteudo += '═══════════════════════════════════════════════════════════\n\n';

    conteudo += '📊 STATUS GERAL DO PROJETO\n\n';

    const progressoGeral = atividades.length > 0
      ? Math.round(atividades.reduce((acc, a) => acc + a.percentual, 0) / atividades.length)
      : 0;

    conteudo += `Progresso Geral: ${progressoGeral}%\n`;
    conteudo += `Total de atividades: ${atividades.length}\n`;
    conteudo += `Concluídas: ${atividades.filter(a => a.status === 'concluida').length}\n`;
    conteudo += `Em execução: ${atividades.filter(a => a.status === 'em_execucao').length}\n`;
    conteudo += `Planejadas: ${atividades.filter(a => a.status === 'planejada').length}\n`;
    conteudo += `Bloqueadas: ${atividades.filter(a => a.status === 'bloqueada').length}\n\n`;

    conteudo += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n';

    atividades.forEach((atividade, index) => {
      conteudo += `${index + 1}. ${atividade.atividade || '(sem título)'}\n`;
      conteudo += `   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
      conteudo += `   📊 Status:            ${getStatusIcon(atividade.status)} ${getStatusLabel(atividade.status)}\n`;
      conteudo += `   📈 Percentual:        ${atividade.percentual}%\n`;
      conteudo += `   📅 Última atualização: ${atividade.ultimaAtualizacao || '—'}\n`;
      conteudo += `   📝 Observações:       ${atividade.observacoes || '—'}\n`;
      conteudo += '\n';
    });

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += `Exportado em: ${new Date().toLocaleString('pt-BR')}\n`;

    const blob = new Blob([conteudo], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'painel_progresso_operacional.txt';
    link.click();
    URL.revokeObjectURL(url);
  };

  const getStatusIcon = (status: StatusAtividade): string => {
    const icons = {
      planejada: '⏳',
      em_execucao: '⚙️',
      concluida: '✅',
      bloqueada: '🚫'
    };
    return icons[status];
  };

  const getStatusLabel = (status: StatusAtividade): string => {
    const labels = {
      planejada: 'Planejado',
      em_execucao: 'Em execução',
      concluida: 'Concluído',
      bloqueada: 'Bloqueada'
    };
    return labels[status];
  };

  const getStatusColor = (status: StatusAtividade): string => {
    const colors = {
      planejada: '#6c757d',
      em_execucao: '#0d6efd',
      concluida: '#198754',
      bloqueada: '#dc3545'
    };
    return colors[status];
  };

  const getProgressColor = (percentual: number): string => {
    if (percentual === 100) return '#198754';
    if (percentual >= 70) return '#0d6efd';
    if (percentual >= 30) return '#ffc107';
    return '#dc3545';
  };

  // Cálculos para estatísticas
  const progressoGeral = atividades.length > 0
    ? Math.round(atividades.reduce((acc, a) => acc + a.percentual, 0) / atividades.length)
    : 0;

  const totalConcluidas = atividades.filter(a => a.status === 'concluida').length;
  const totalEmExecucao = atividades.filter(a => a.status === 'em_execucao').length;
  const totalBloqueadas = atividades.filter(a => a.status === 'bloqueada').length;

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <div>
          <h2>📊 Painel de Progresso Operacional</h2>
          <p className="artefato-descricao">
            Acompanhar status das atividades e gerar alertas sobre o andamento do projeto.
          </p>
        </div>
        <button className="btn-exportar" onClick={exportarTxt}>
          📥 Exportar TXT
        </button>
      </div>

      {/* Dashboard de Estatísticas */}
      <div className="dashboard-progresso">
        <div className="progresso-geral-card">
          <h3>📈 Progresso Geral do Projeto</h3>
          <div className="progresso-geral-circular">
            <svg width="160" height="160" viewBox="0 0 160 160">
              <circle
                cx="80"
                cy="80"
                r="70"
                fill="none"
                stroke="#e9ecef"
                strokeWidth="12"
              />
              <circle
                cx="80"
                cy="80"
                r="70"
                fill="none"
                stroke={getProgressColor(progressoGeral)}
                strokeWidth="12"
                strokeDasharray={`${2 * Math.PI * 70 * progressoGeral / 100} ${2 * Math.PI * 70}`}
                strokeLinecap="round"
                transform="rotate(-90 80 80)"
              />
              <text
                x="80"
                y="80"
                textAnchor="middle"
                dy=".3em"
                fontSize="36"
                fontWeight="700"
                fill="#212529"
              >
                {progressoGeral}%
              </text>
            </svg>
          </div>
        </div>

        <div className="stats-grid">
          <div className="stat-box stat-concluida">
            <div className="stat-icon">✅</div>
            <div className="stat-number">{totalConcluidas}</div>
            <div className="stat-text">Concluídas</div>
          </div>
          <div className="stat-box stat-em-execucao">
            <div className="stat-icon">⚙️</div>
            <div className="stat-number">{totalEmExecucao}</div>
            <div className="stat-text">Em execução</div>
          </div>
          <div className="stat-box stat-bloqueada">
            <div className="stat-icon">🚫</div>
            <div className="stat-number">{totalBloqueadas}</div>
            <div className="stat-text">Bloqueadas</div>
          </div>
          <div className="stat-box">
            <div className="stat-icon">📋</div>
            <div className="stat-number">{atividades.length}</div>
            <div className="stat-text">Total</div>
          </div>
        </div>
      </div>

      {/* Alertas */}
      {totalBloqueadas > 0 && (
        <div className="alerta-bloqueadas">
          <span className="alerta-icon">⚠️</span>
          <strong>Atenção:</strong> {totalBloqueadas} atividade(s) bloqueada(s) precisam de atenção imediata!
        </div>
      )}

      <div className="artefato-controls">
        <button className="btn-adicionar" onClick={adicionarAtividade}>
          ➕ Adicionar Atividade
        </button>
      </div>

      {/* Cards de Atividades */}
      <div className="atividades-cards-grid">
        {atividades.map((atividade) => (
          <div key={atividade.id} className="atividade-progress-card">
            <div className="atividade-progress-header">
              <input
                type="text"
                value={atividade.atividade}
                onChange={(e) => atualizarAtividade(atividade.id, 'atividade', e.target.value)}
                placeholder="Nome da atividade"
                className="atividade-titulo-input"
              />
              <button
                className="btn-remover-card"
                onClick={() => removerAtividade(atividade.id)}
                title="Remover atividade"
              >
                ✕
              </button>
            </div>

            <div className="atividade-status-select">
              <label>Status:</label>
              <select
                value={atividade.status}
                onChange={(e) => atualizarAtividade(atividade.id, 'status', e.target.value as StatusAtividade)}
                style={{ backgroundColor: getStatusColor(atividade.status), color: 'white' }}
              >
                <option value="planejada">⏳ Planejado</option>
                <option value="em_execucao">⚙️ Em execução</option>
                <option value="concluida">✅ Concluído</option>
                <option value="bloqueada">🚫 Bloqueada</option>
              </select>
            </div>

            <div className="atividade-percentual">
              <label>Progresso: {atividade.percentual}%</label>
              <div className="progress-bar-container">
                <div
                  className="progress-bar-fill"
                  style={{
                    width: `${atividade.percentual}%`,
                    backgroundColor: getProgressColor(atividade.percentual)
                  }}
                >
                  {atividade.percentual > 10 && <span>{atividade.percentual}%</span>}
                </div>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={atividade.percentual}
                onChange={(e) => atualizarAtividade(atividade.id, 'percentual', parseInt(e.target.value))}
                className="progress-range"
              />
            </div>

            <div className="atividade-data">
              <label>Última atualização:</label>
              <input
                type="date"
                value={atividade.ultimaAtualizacao}
                onChange={(e) => atualizarAtividade(atividade.id, 'ultimaAtualizacao', e.target.value)}
                className="input-date-small"
              />
            </div>

            <div className="atividade-observacoes">
              <label>Observações:</label>
              <textarea
                value={atividade.observacoes}
                onChange={(e) => atualizarAtividade(atividade.id, 'observacoes', e.target.value)}
                placeholder="Adicione observações sobre o andamento..."
                rows={2}
              />
            </div>
          </div>
        ))}
      </div>

      {atividades.length === 0 && (
        <div className="empty-state">
          <p>Nenhuma atividade cadastrada. Clique em "Adicionar Atividade" para começar.</p>
        </div>
      )}

      <style>{`
        .dashboard-progresso {
          display: grid;
          grid-template-columns: 240px 1fr;
          gap: 20px;
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.05);
          margin: 20px 0;
        }

        .progresso-geral-card {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 15px;
        }

        .progresso-geral-card h3 {
          font-size: 14px;
          text-align: center;
          color: #495057;
        }

        .progresso-geral-circular {
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 15px;
        }

        .stat-box {
          background: #f8f9fa;
          padding: 20px;
          border-radius: 8px;
          text-align: center;
          border: 2px solid transparent;
          transition: all 0.2s;
        }

        .stat-box:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        .stat-box.stat-concluida {
          border-color: #198754;
        }

        .stat-box.stat-em-execucao {
          border-color: #0d6efd;
        }

        .stat-box.stat-bloqueada {
          border-color: #dc3545;
        }

        .stat-icon {
          font-size: 28px;
          margin-bottom: 8px;
        }

        .stat-number {
          font-size: 36px;
          font-weight: 700;
          color: #212529;
        }

        .stat-text {
          font-size: 13px;
          color: #6c757d;
          margin-top: 4px;
        }

        .alerta-bloqueadas {
          background: #fff3cd;
          border: 1px solid #ffc107;
          border-left: 4px solid #dc3545;
          padding: 15px;
          border-radius: 6px;
          display: flex;
          align-items: center;
          gap: 10px;
          margin: 20px 0;
          font-size: 14px;
        }

        .alerta-icon {
          font-size: 20px;
        }

        .atividades-cards-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          gap: 20px;
          margin-top: 20px;
        }

        .atividade-progress-card {
          background: white;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.05);
          display: flex;
          flex-direction: column;
          gap: 15px;
        }

        .atividade-progress-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 10px;
        }

        .atividade-titulo-input {
          flex: 1;
          padding: 8px;
          border: 1px solid #ced4da;
          border-radius: 6px;
          font-size: 16px;
          font-weight: 600;
        }

        .btn-remover-card {
          background: #dc3545;
          color: white;
          border: none;
          border-radius: 50%;
          width: 28px;
          height: 28px;
          cursor: pointer;
          font-size: 16px;
          flex-shrink: 0;
          transition: all 0.2s;
        }

        .btn-remover-card:hover {
          background: #bb2d3b;
          transform: scale(1.1);
        }

        .atividade-status-select {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .atividade-status-select label {
          font-size: 13px;
          font-weight: 600;
          color: #495057;
        }

        .atividade-status-select select {
          padding: 8px 12px;
          border: none;
          border-radius: 6px;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
        }

        .atividade-percentual {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .atividade-percentual label {
          font-size: 13px;
          font-weight: 600;
          color: #495057;
        }

        .progress-bar-container {
          height: 28px;
          background: #e9ecef;
          border-radius: 6px;
          overflow: hidden;
          position: relative;
        }

        .progress-bar-fill {
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: flex-end;
          padding-right: 10px;
          transition: width 0.3s ease;
        }

        .progress-bar-fill span {
          color: white;
          font-size: 12px;
          font-weight: 600;
        }

        .progress-range {
          width: 100%;
          height: 6px;
          -webkit-appearance: none;
          appearance: none;
          background: #e9ecef;
          border-radius: 3px;
          outline: none;
        }

        .progress-range::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 18px;
          height: 18px;
          background: #0d6efd;
          border-radius: 50%;
          cursor: pointer;
        }

        .progress-range::-moz-range-thumb {
          width: 18px;
          height: 18px;
          background: #0d6efd;
          border-radius: 50%;
          cursor: pointer;
          border: none;
        }

        .atividade-data {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .atividade-data label {
          font-size: 13px;
          font-weight: 600;
          color: #495057;
        }

        .input-date-small {
          padding: 8px;
          border: 1px solid #ced4da;
          border-radius: 6px;
          font-size: 14px;
        }

        .atividade-observacoes {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .atividade-observacoes label {
          font-size: 13px;
          font-weight: 600;
          color: #495057;
        }

        .atividade-observacoes textarea {
          padding: 8px;
          border: 1px solid #ced4da;
          border-radius: 6px;
          font-size: 14px;
          font-family: inherit;
          resize: vertical;
        }

        @media (max-width: 768px) {
          .dashboard-progresso {
            grid-template-columns: 1fr;
          }

          .atividades-cards-grid {
            grid-template-columns: 1fr;
          }

          .stats-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }
      `}</style>
    </div>
  );
};

export default PainelProgressoOperacional;
