import React, { useState } from 'react';
import './Artefatos.css';

type NivelRisco = 'baixo' | 'medio' | 'alto' | 'critico';

interface RecursoCapacidade {
  id: string;
  recurso: string; // Nome do recurso/pessoa
  atividadesAtribuidas: number;
  capacidadeDisponivel: number; // 0 a 100 (%)
  observacoes: string;
}

export const MapaGargalos: React.FC = () => {
  const [recursos, setRecursos] = useState<RecursoCapacidade[]>([
    {
      id: '1',
      recurso: 'Ana / Analista',
      atividadesAtribuidas: 7,
      capacidadeDisponivel: 15,
      observacoes: 'Sobrecarga - redistribuir tarefas'
    },
    {
      id: '2',
      recurso: 'Pedro / Técnico',
      atividadesAtribuidas: 3,
      capacidadeDisponivel: 90,
      observacoes: 'Disponível para novas demandas'
    },
    {
      id: '3',
      recurso: 'Maria / Coordenadora',
      atividadesAtribuidas: 5,
      capacidadeDisponivel: 40,
      observacoes: 'Capacidade em nível adequado'
    }
  ]);

  const adicionarRecurso = () => {
    const novoRecurso: RecursoCapacidade = {
      id: Date.now().toString(),
      recurso: '',
      atividadesAtribuidas: 0,
      capacidadeDisponivel: 100,
      observacoes: ''
    };
    setRecursos([...recursos, novoRecurso]);
  };

  const removerRecurso = (id: string) => {
    setRecursos(recursos.filter(r => r.id !== id));
  };

  const atualizarRecurso = (id: string, campo: keyof RecursoCapacidade, valor: string | number) => {
    setRecursos(recursos.map(r =>
      r.id === id ? { ...r, [campo]: valor } : r
    ));
  };

  const calcularRisco = (capacidade: number): NivelRisco => {
    if (capacidade >= 80) return 'baixo';
    if (capacidade >= 50) return 'medio';
    if (capacidade >= 20) return 'alto';
    return 'critico';
  };

  const getRiscoLabel = (risco: NivelRisco): string => {
    const labels = {
      baixo: '🟢 Baixo',
      medio: '🟡 Médio',
      alto: '🟠 Alto',
      critico: '🔴 Crítico'
    };
    return labels[risco];
  };

  const getRiscoColor = (risco: NivelRisco): string => {
    const colors = {
      baixo: '#198754',
      medio: '#ffc107',
      alto: '#fd7e14',
      critico: '#dc3545'
    };
    return colors[risco];
  };

  const getCapacidadeColor = (capacidade: number): string => {
    if (capacidade >= 80) return '#198754';
    if (capacidade >= 50) return '#ffc107';
    if (capacidade >= 20) return '#fd7e14';
    return '#dc3545';
  };

  const exportarTxt = () => {
    let conteudo = '═══════════════════════════════════════════════════════════\n';
    conteudo += '  MAPA DE GARGALOS E CAPACIDADES CRÍTICAS\n';
    conteudo += '  Domínio 4 - Capacidades e Atividades\n';
    conteudo += '═══════════════════════════════════════════════════════════\n\n';

    conteudo += '📊 ANÁLISE DE CARGA DE TRABALHO\n\n';

    recursos.forEach((recurso, index) => {
      const risco = calcularRisco(recurso.capacidadeDisponivel);
      conteudo += `${index + 1}. ${recurso.recurso || '(não identificado)'}\n`;
      conteudo += `   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
      conteudo += `   📋 Atividades atribuídas: ${recurso.atividadesAtribuidas}\n`;
      conteudo += `   💪 Capacidade disponível:  ${recurso.capacidadeDisponivel}%\n`;
      conteudo += `   ⚠️  Nível de risco:        ${getRiscoLabel(risco)}\n`;
      conteudo += `   📝 Observações:            ${recurso.observacoes || '—'}\n`;
      conteudo += '\n';
    });

    // Estatísticas gerais
    const mediaCapacidade = recursos.length > 0
      ? Math.round(recursos.reduce((acc, r) => acc + r.capacidadeDisponivel, 0) / recursos.length)
      : 0;
    const recursosRiscoCritico = recursos.filter(r => calcularRisco(r.capacidadeDisponivel) === 'critico').length;
    const recursosRiscoAlto = recursos.filter(r => calcularRisco(r.capacidadeDisponivel) === 'alto').length;

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += '📈 ESTATÍSTICAS GERAIS\n\n';
    conteudo += `Total de recursos: ${recursos.length}\n`;
    conteudo += `Capacidade média disponível: ${mediaCapacidade}%\n`;
    conteudo += `Recursos em risco crítico (< 20%): ${recursosRiscoCritico}\n`;
    conteudo += `Recursos em risco alto (20-50%): ${recursosRiscoAlto}\n`;
    conteudo += '\n';

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += `Exportado em: ${new Date().toLocaleString('pt-BR')}\n`;

    const blob = new Blob([conteudo], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'mapa_gargalos.txt';
    link.click();
    URL.revokeObjectURL(url);
  };

  const mediaCapacidade = recursos.length > 0
    ? Math.round(recursos.reduce((acc, r) => acc + r.capacidadeDisponivel, 0) / recursos.length)
    : 0;

  const recursosRiscoCritico = recursos.filter(r => calcularRisco(r.capacidadeDisponivel) === 'critico').length;
  const recursosRiscoAlto = recursos.filter(r => calcularRisco(r.capacidadeDisponivel) === 'alto').length;

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <div>
          <h2>⚠️ Mapa de Gargalos e Capacidades Críticas</h2>
          <p className="artefato-descricao">
            Identificar sobrecargas e lacunas de recursos, evitando colapsos operacionais.
          </p>
        </div>
        <button className="btn-exportar" onClick={exportarTxt}>
          📥 Exportar TXT
        </button>
      </div>

      {/* Estatísticas Resumidas */}
      <div className="estatisticas-gargalos">
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-info">
            <div className="stat-value">{mediaCapacidade}%</div>
            <div className="stat-label">Capacidade Média</div>
          </div>
        </div>
        <div className="stat-card stat-critico">
          <div className="stat-icon">🔴</div>
          <div className="stat-info">
            <div className="stat-value">{recursosRiscoCritico}</div>
            <div className="stat-label">Risco Crítico</div>
          </div>
        </div>
        <div className="stat-card stat-alto">
          <div className="stat-icon">🟠</div>
          <div className="stat-info">
            <div className="stat-value">{recursosRiscoAlto}</div>
            <div className="stat-label">Risco Alto</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-info">
            <div className="stat-value">{recursos.length}</div>
            <div className="stat-label">Total de Recursos</div>
          </div>
        </div>
      </div>

      <div className="artefato-controls">
        <button className="btn-adicionar" onClick={adicionarRecurso}>
          ➕ Adicionar Recurso
        </button>
      </div>

      {/* Visualização de Heatmap */}
      <div className="heatmap-container">
        <h3>📊 Heatmap de Capacidade</h3>
        <div className="heatmap-grid">
          {recursos.map((recurso) => {
            const risco = calcularRisco(recurso.capacidadeDisponivel);
            return (
              <div
                key={recurso.id}
                className="heatmap-cell"
                style={{ backgroundColor: getRiscoColor(risco) }}
              >
                <div className="heatmap-cell-header">
                  <span className="heatmap-name">{recurso.recurso || 'Sem nome'}</span>
                  <button
                    className="btn-remover-heatmap"
                    onClick={() => removerRecurso(recurso.id)}
                    title="Remover recurso"
                  >
                    ✕
                  </button>
                </div>
                <div className="heatmap-capacity">{recurso.capacidadeDisponivel}%</div>
                <div className="heatmap-tasks">{recurso.atividadesAtribuidas} tarefas</div>
                <div className="heatmap-risk">{getRiscoLabel(risco)}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Tabela Detalhada */}
      <div className="tabela-gargalos">
        <h3>📋 Detalhamento de Recursos</h3>
        <table>
          <thead>
            <tr>
              <th style={{ width: '25%' }}>Recurso / Pessoa</th>
              <th style={{ width: '15%' }}>Atividades</th>
              <th style={{ width: '20%' }}>Capacidade Disponível</th>
              <th style={{ width: '12%' }}>Risco</th>
              <th style={{ width: '25%' }}>Observações</th>
              <th style={{ width: '3%' }}></th>
            </tr>
          </thead>
          <tbody>
            {recursos.map((recurso) => {
              const risco = calcularRisco(recurso.capacidadeDisponivel);
              return (
                <tr key={recurso.id}>
                  <td>
                    <input
                      type="text"
                      value={recurso.recurso}
                      onChange={(e) => atualizarRecurso(recurso.id, 'recurso', e.target.value)}
                      placeholder="Nome do recurso"
                      className="input-inline"
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      value={recurso.atividadesAtribuidas}
                      onChange={(e) => atualizarRecurso(recurso.id, 'atividadesAtribuidas', parseInt(e.target.value) || 0)}
                      className="input-inline input-number"
                      min="0"
                    />
                  </td>
                  <td>
                    <div className="capacidade-cell">
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={recurso.capacidadeDisponivel}
                        onChange={(e) => atualizarRecurso(recurso.id, 'capacidadeDisponivel', parseInt(e.target.value))}
                        className="capacidade-slider"
                      />
                      <span className="capacidade-value">{recurso.capacidadeDisponivel}%</span>
                    </div>
                  </td>
                  <td>
                    <span
                      className="risco-badge"
                      style={{ backgroundColor: getRiscoColor(risco), color: 'white' }}
                    >
                      {getRiscoLabel(risco)}
                    </span>
                  </td>
                  <td>
                    <input
                      type="text"
                      value={recurso.observacoes}
                      onChange={(e) => atualizarRecurso(recurso.id, 'observacoes', e.target.value)}
                      placeholder="Observações"
                      className="input-inline"
                    />
                  </td>
                  <td>
                    <button
                      className="btn-remover-table"
                      onClick={() => removerRecurso(recurso.id)}
                      title="Remover recurso"
                    >
                      ✕
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {recursos.length === 0 && (
        <div className="empty-state">
          <p>Nenhum recurso cadastrado. Clique em "Adicionar Recurso" para começar.</p>
        </div>
      )}

      <style>{`
        .estatisticas-gargalos {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
          margin: 20px 0;
        }

        .stat-card {
          background: white;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 20px;
          display: flex;
          align-items: center;
          gap: 15px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .stat-card.stat-critico {
          border-left: 4px solid #dc3545;
        }

        .stat-card.stat-alto {
          border-left: 4px solid #fd7e14;
        }

        .stat-icon {
          font-size: 32px;
        }

        .stat-info {
          flex: 1;
        }

        .stat-value {
          font-size: 28px;
          font-weight: 700;
          color: #212529;
        }

        .stat-label {
          font-size: 13px;
          color: #6c757d;
          margin-top: 4px;
        }

        .heatmap-container {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.05);
          margin: 20px 0;
        }

        .heatmap-container h3 {
          margin-bottom: 15px;
          font-size: 18px;
        }

        .heatmap-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
          gap: 12px;
        }

        .heatmap-cell {
          padding: 15px;
          border-radius: 8px;
          color: white;
          display: flex;
          flex-direction: column;
          gap: 8px;
          min-height: 140px;
          position: relative;
          transition: transform 0.2s;
        }

        .heatmap-cell:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        .heatmap-cell-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
        }

        .heatmap-name {
          font-weight: 600;
          font-size: 14px;
        }

        .btn-remover-heatmap {
          background: rgba(255,255,255,0.3);
          color: white;
          border: none;
          border-radius: 50%;
          width: 22px;
          height: 22px;
          cursor: pointer;
          font-size: 12px;
          transition: all 0.2s;
        }

        .btn-remover-heatmap:hover {
          background: rgba(255,255,255,0.5);
        }

        .heatmap-capacity {
          font-size: 32px;
          font-weight: 700;
          margin-top: auto;
        }

        .heatmap-tasks {
          font-size: 13px;
          opacity: 0.95;
        }

        .heatmap-risk {
          font-size: 12px;
          font-weight: 600;
          opacity: 0.9;
        }

        .tabela-gargalos {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.05);
          margin-top: 20px;
        }

        .tabela-gargalos h3 {
          margin-bottom: 15px;
          font-size: 18px;
        }

        .tabela-gargalos table {
          width: 100%;
          border-collapse: collapse;
        }

        .tabela-gargalos th {
          background: #f8f9fa;
          padding: 12px;
          text-align: left;
          font-weight: 600;
          border-bottom: 2px solid #dee2e6;
          font-size: 14px;
        }

        .tabela-gargalos td {
          padding: 10px;
          border-bottom: 1px solid #dee2e6;
        }

        .input-number {
          text-align: center;
        }

        .capacidade-cell {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .capacidade-slider {
          flex: 1;
          height: 6px;
          -webkit-appearance: none;
          appearance: none;
          background: #e9ecef;
          border-radius: 3px;
          outline: none;
        }

        .capacidade-slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 16px;
          height: 16px;
          background: #0d6efd;
          border-radius: 50%;
          cursor: pointer;
        }

        .capacidade-slider::-moz-range-thumb {
          width: 16px;
          height: 16px;
          background: #0d6efd;
          border-radius: 50%;
          cursor: pointer;
          border: none;
        }

        .capacidade-value {
          font-weight: 600;
          font-size: 13px;
          min-width: 40px;
          text-align: right;
        }

        .risco-badge {
          display: inline-block;
          padding: 6px 12px;
          border-radius: 16px;
          font-size: 12px;
          font-weight: 600;
        }

        @media (max-width: 768px) {
          .heatmap-grid {
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
          }

          .tabela-gargalos {
            overflow-x: auto;
          }
        }
      `}</style>
    </div>
  );
};

export default MapaGargalos;
