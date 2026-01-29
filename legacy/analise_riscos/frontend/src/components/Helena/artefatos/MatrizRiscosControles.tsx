import React, { useState } from 'react';
import './Artefatos.css';

type Probabilidade = 'baixa' | 'media' | 'alta';
type Impacto = 'baixo' | 'medio' | 'alto';
type NivelRisco = 'baixo' | 'medio' | 'alto' | 'critico';

interface RiscoControle {
  id: string;
  risco: string;
  causa: string;
  impacto: Impacto;
  probabilidade: Probabilidade;
  nivelRisco: NivelRisco;
  controleExistente: string;
  responsavel: string;
}

export const MatrizRiscosControles: React.FC = () => {
  const [riscos, setRiscos] = useState<RiscoControle[]>([
    {
      id: '1',
      risco: 'Falta de equipe técnica',
      causa: 'Saída de servidores',
      impacto: 'alto',
      probabilidade: 'alta',
      nivelRisco: 'critico',
      controleExistente: 'Redistribuição de tarefas',
      responsavel: 'Coordenação'
    },
    {
      id: '2',
      risco: 'Erro em dados críticos',
      causa: 'Falha de integração de sistemas',
      impacto: 'medio',
      probabilidade: 'media',
      nivelRisco: 'medio',
      controleExistente: 'Validação cruzada',
      responsavel: 'TI'
    },
    {
      id: '3',
      risco: 'Mudança normativa',
      causa: 'Publicação de novo decreto',
      impacto: 'alto',
      probabilidade: 'alta',
      nivelRisco: 'critico',
      controleExistente: 'Acompanhamento jurídico',
      responsavel: 'Gabinete'
    }
  ]);

  const [filtroNivel, setFiltroNivel] = useState<NivelRisco | 'todos'>('todos');

  const adicionarRisco = () => {
    const novoRisco: RiscoControle = {
      id: Date.now().toString(),
      risco: '',
      causa: '',
      impacto: 'medio',
      probabilidade: 'media',
      nivelRisco: 'medio',
      controleExistente: '',
      responsavel: ''
    };
    setRiscos([...riscos, novoRisco]);
  };

  const removerRisco = (id: string) => {
    setRiscos(riscos.filter(r => r.id !== id));
  };

  const calcularNivelRisco = (probabilidade: Probabilidade, impacto: Impacto): NivelRisco => {
    const valores = { baixa: 1, media: 2, alta: 3, baixo: 1, medio: 2, alto: 3 };
    const score = valores[probabilidade] * valores[impacto];

    if (score >= 9) return 'critico';
    if (score >= 6) return 'alto';
    if (score >= 3) return 'medio';
    return 'baixo';
  };

  const atualizarRisco = (id: string, campo: keyof RiscoControle, valor: any) => {
    setRiscos(riscos.map(r => {
      if (r.id !== id) return r;

      const updated = { ...r, [campo]: valor };
      if (campo === 'probabilidade' || campo === 'impacto') {
        updated.nivelRisco = calcularNivelRisco(
          campo === 'probabilidade' ? valor : r.probabilidade,
          campo === 'impacto' ? valor : r.impacto
        );
      }
      return updated;
    }));
  };

  const getNivelColor = (nivel: NivelRisco): string => {
    const colors = {
      baixo: '#198754',
      medio: '#ffc107',
      alto: '#fd7e14',
      critico: '#dc3545'
    };
    return colors[nivel];
  };

  const getNivelLabel = (nivel: NivelRisco): string => {
    const labels = {
      baixo: '🟢 Baixo',
      medio: '🟡 Médio',
      alto: '🟠 Alto',
      critico: '🔴 Crítico'
    };
    return labels[nivel];
  };

  const exportarTxt = () => {
    let conteudo = '═══════════════════════════════════════════════════════════\n';
    conteudo += '  MATRIZ DE RISCOS E CONTROLES (ISO 31000)\n';
    conteudo += '  Domínio 6 - Incerteza e Contexto\n';
    conteudo += '═══════════════════════════════════════════════════════════\n\n';

    conteudo += '📊 RISCOS IDENTIFICADOS\n\n';

    riscos.forEach((risco, index) => {
      conteudo += `${index + 1}. ${risco.risco || '(não identificado)'}\n`;
      conteudo += `   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
      conteudo += `   🔍 Causa:            ${risco.causa || '—'}\n`;
      conteudo += `   ⚡ Impacto:          ${risco.impacto}\n`;
      conteudo += `   📊 Probabilidade:    ${risco.probabilidade}\n`;
      conteudo += `   ⚠️  Nível de Risco:   ${getNivelLabel(risco.nivelRisco)}\n`;
      conteudo += `   🛡️  Controle:         ${risco.controleExistente || '—'}\n`;
      conteudo += `   👤 Responsável:      ${risco.responsavel || '—'}\n`;
      conteudo += '\n';
    });

    // Estatísticas
    const totalCritico = riscos.filter(r => r.nivelRisco === 'critico').length;
    const totalAlto = riscos.filter(r => r.nivelRisco === 'alto').length;
    const totalMedio = riscos.filter(r => r.nivelRisco === 'medio').length;
    const totalBaixo = riscos.filter(r => r.nivelRisco === 'baixo').length;

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += '📈 ESTATÍSTICAS\n\n';
    conteudo += `Total de riscos mapeados: ${riscos.length}\n`;
    conteudo += `Riscos críticos: ${totalCritico}\n`;
    conteudo += `Riscos altos: ${totalAlto}\n`;
    conteudo += `Riscos médios: ${totalMedio}\n`;
    conteudo += `Riscos baixos: ${totalBaixo}\n`;
    conteudo += '\n';

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += `Exportado em: ${new Date().toLocaleString('pt-BR')}\n`;

    const blob = new Blob([conteudo], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'matriz_riscos.txt';
    link.click();
    URL.revokeObjectURL(url);
  };

  const riscosFiltrados = filtroNivel === 'todos'
    ? riscos
    : riscos.filter(r => r.nivelRisco === filtroNivel);

  const totalCritico = riscos.filter(r => r.nivelRisco === 'critico').length;
  const totalAlto = riscos.filter(r => r.nivelRisco === 'alto').length;
  const totalMedio = riscos.filter(r => r.nivelRisco === 'medio').length;

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <div>
          <h2>⚠️ Matriz de Riscos e Controles</h2>
          <p className="artefato-descricao">
            Identificar, avaliar e priorizar riscos de forma estruturada (ISO 31000).
          </p>
        </div>
        <button className="btn-exportar" onClick={exportarTxt}>
          📥 Exportar TXT
        </button>
      </div>

      {/* Estatísticas de Nível de Risco */}
      <div className="estatisticas-stakeholders">
        <div className="stat-card stat-critico">
          <div className="stat-icon">🔴</div>
          <div className="stat-info">
            <div className="stat-value">{totalCritico}</div>
            <div className="stat-label">Críticos</div>
          </div>
        </div>
        <div className="stat-card stat-alto">
          <div className="stat-icon">🟠</div>
          <div className="stat-info">
            <div className="stat-value">{totalAlto}</div>
            <div className="stat-label">Altos</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🟡</div>
          <div className="stat-info">
            <div className="stat-value">{totalMedio}</div>
            <div className="stat-label">Médios</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-info">
            <div className="stat-value">{riscos.length}</div>
            <div className="stat-label">Total</div>
          </div>
        </div>
      </div>

      {/* Alerta de Riscos Críticos */}
      {totalCritico > 0 && (
        <div className="alerta-pendencias" style={{ borderLeftColor: '#dc3545' }}>
          <span className="alerta-icon">🚨</span>
          <strong>Atenção:</strong> {totalCritico} risco(s) crítico(s) identificado(s)! Requer ação imediata.
        </div>
      )}

      <div className="artefato-controls">
        <button className="btn-adicionar" onClick={adicionarRisco}>
          ➕ Adicionar Risco
        </button>

        <div className="filtro-status">
          <label>Filtrar por nível:</label>
          <select
            value={filtroNivel}
            onChange={(e) => setFiltroNivel(e.target.value as NivelRisco | 'todos')}
          >
            <option value="todos">Todos</option>
            <option value="critico">Crítico</option>
            <option value="alto">Alto</option>
            <option value="medio">Médio</option>
            <option value="baixo">Baixo</option>
          </select>
        </div>
      </div>

      {/* Matriz Visual de Riscos */}
      <div className="matriz-visual-container">
        <h3>📊 Matriz de Probabilidade x Impacto</h3>
        <div className="matriz-risco-grid">
          <div className="matriz-risco-eixo-y">
            <span className="eixo-label">Probabilidade</span>
          </div>

          <div className="matriz-risco-cells">
            {/* Linha Alta Probabilidade */}
            <div className="matriz-risco-cell nivel-medio">
              <div className="cell-label">Médio</div>
              {riscos.filter(r => r.probabilidade === 'alta' && r.impacto === 'baixo').map(r => (
                <div key={r.id} className="risco-bubble medio">{r.risco.substring(0, 20)}...</div>
              ))}
            </div>
            <div className="matriz-risco-cell nivel-alto">
              <div className="cell-label">Alto</div>
              {riscos.filter(r => r.probabilidade === 'alta' && r.impacto === 'medio').map(r => (
                <div key={r.id} className="risco-bubble alto">{r.risco.substring(0, 20)}...</div>
              ))}
            </div>
            <div className="matriz-risco-cell nivel-critico">
              <div className="cell-label">Crítico</div>
              {riscos.filter(r => r.probabilidade === 'alta' && r.impacto === 'alto').map(r => (
                <div key={r.id} className="risco-bubble critico">{r.risco.substring(0, 20)}...</div>
              ))}
            </div>

            {/* Linha Média Probabilidade */}
            <div className="matriz-risco-cell nivel-baixo">
              <div className="cell-label">Baixo</div>
              {riscos.filter(r => r.probabilidade === 'media' && r.impacto === 'baixo').map(r => (
                <div key={r.id} className="risco-bubble baixo">{r.risco.substring(0, 20)}...</div>
              ))}
            </div>
            <div className="matriz-risco-cell nivel-medio">
              <div className="cell-label">Médio</div>
              {riscos.filter(r => r.probabilidade === 'media' && r.impacto === 'medio').map(r => (
                <div key={r.id} className="risco-bubble medio">{r.risco.substring(0, 20)}...</div>
              ))}
            </div>
            <div className="matriz-risco-cell nivel-alto">
              <div className="cell-label">Alto</div>
              {riscos.filter(r => r.probabilidade === 'media' && r.impacto === 'alto').map(r => (
                <div key={r.id} className="risco-bubble alto">{r.risco.substring(0, 20)}...</div>
              ))}
            </div>

            {/* Linha Baixa Probabilidade */}
            <div className="matriz-risco-cell nivel-baixo">
              <div className="cell-label">Baixo</div>
              {riscos.filter(r => r.probabilidade === 'baixa' && r.impacto === 'baixo').map(r => (
                <div key={r.id} className="risco-bubble baixo">{r.risco.substring(0, 20)}...</div>
              ))}
            </div>
            <div className="matriz-risco-cell nivel-baixo">
              <div className="cell-label">Baixo</div>
              {riscos.filter(r => r.probabilidade === 'baixa' && r.impacto === 'medio').map(r => (
                <div key={r.id} className="risco-bubble baixo">{r.risco.substring(0, 20)}...</div>
              ))}
            </div>
            <div className="matriz-risco-cell nivel-medio">
              <div className="cell-label">Médio</div>
              {riscos.filter(r => r.probabilidade === 'baixa' && r.impacto === 'alto').map(r => (
                <div key={r.id} className="risco-bubble medio">{r.risco.substring(0, 20)}...</div>
              ))}
            </div>
          </div>

          <div className="matriz-risco-eixo-x">
            <span className="eixo-label">Impacto</span>
            <div className="eixo-labels">
              <span>Baixo</span>
              <span>Médio</span>
              <span>Alto</span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabela Detalhada */}
      <div className="tabela-stakeholders">
        <h3>📋 Detalhamento de Riscos</h3>
        <table>
          <thead>
            <tr>
              <th style={{ width: '18%' }}>Risco</th>
              <th style={{ width: '15%' }}>Causa</th>
              <th style={{ width: '10%' }}>Impacto</th>
              <th style={{ width: '12%' }}>Probabilidade</th>
              <th style={{ width: '10%' }}>Nível</th>
              <th style={{ width: '18%' }}>Controle</th>
              <th style={{ width: '14%' }}>Responsável</th>
              <th style={{ width: '3%' }}></th>
            </tr>
          </thead>
          <tbody>
            {riscosFiltrados.map((risco) => (
              <tr key={risco.id}>
                <td>
                  <input
                    type="text"
                    value={risco.risco}
                    onChange={(e) => atualizarRisco(risco.id, 'risco', e.target.value)}
                    placeholder="Descrição do risco"
                    className="input-inline"
                  />
                </td>
                <td>
                  <input
                    type="text"
                    value={risco.causa}
                    onChange={(e) => atualizarRisco(risco.id, 'causa', e.target.value)}
                    placeholder="Causa"
                    className="input-inline"
                  />
                </td>
                <td>
                  <select
                    value={risco.impacto}
                    onChange={(e) => atualizarRisco(risco.id, 'impacto', e.target.value as Impacto)}
                    className="select-inline"
                  >
                    <option value="baixo">Baixo</option>
                    <option value="medio">Médio</option>
                    <option value="alto">Alto</option>
                  </select>
                </td>
                <td>
                  <select
                    value={risco.probabilidade}
                    onChange={(e) => atualizarRisco(risco.id, 'probabilidade', e.target.value as Probabilidade)}
                    className="select-inline"
                  >
                    <option value="baixa">Baixa</option>
                    <option value="media">Média</option>
                    <option value="alta">Alta</option>
                  </select>
                </td>
                <td>
                  <span
                    className="prioridade-badge"
                    style={{ backgroundColor: getNivelColor(risco.nivelRisco), color: 'white' }}
                  >
                    {getNivelLabel(risco.nivelRisco)}
                  </span>
                </td>
                <td>
                  <input
                    type="text"
                    value={risco.controleExistente}
                    onChange={(e) => atualizarRisco(risco.id, 'controleExistente', e.target.value)}
                    placeholder="Controle existente"
                    className="input-inline"
                  />
                </td>
                <td>
                  <input
                    type="text"
                    value={risco.responsavel}
                    onChange={(e) => atualizarRisco(risco.id, 'responsavel', e.target.value)}
                    placeholder="Responsável"
                    className="input-inline"
                  />
                </td>
                <td>
                  <button
                    className="btn-remover-table"
                    onClick={() => removerRisco(risco.id)}
                    title="Remover risco"
                  >
                    ✕
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {riscosFiltrados.length === 0 && (
        <div className="empty-state">
          <p>Nenhum risco encontrado para o filtro selecionado.</p>
        </div>
      )}

      <style>{`
        .matriz-risco-grid {
          display: flex;
          flex-direction: column;
          gap: 15px;
          margin-top: 20px;
        }

        .matriz-risco-eixo-y {
          writing-mode: vertical-rl;
          transform: rotate(180deg);
          text-align: center;
          font-weight: 600;
          color: #495057;
        }

        .matriz-risco-cells {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          grid-template-rows: repeat(3, 120px);
          gap: 2px;
          background: #dee2e6;
          border: 2px solid #dee2e6;
          border-radius: 8px;
        }

        .matriz-risco-cell {
          padding: 10px;
          display: flex;
          flex-direction: column;
          gap: 8px;
          position: relative;
        }

        .matriz-risco-cell.nivel-baixo { background: #d1e7dd; }
        .matriz-risco-cell.nivel-medio { background: #fff3cd; }
        .matriz-risco-cell.nivel-alto { background: #ffe5d0; }
        .matriz-risco-cell.nivel-critico { background: #f8d7da; }

        .cell-label {
          font-size: 11px;
          font-weight: 600;
          color: #495057;
        }

        .risco-bubble {
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 11px;
          color: white;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .risco-bubble.baixo { background: #198754; }
        .risco-bubble.medio { background: #ffc107; color: #212529; }
        .risco-bubble.alto { background: #fd7e14; }
        .risco-bubble.critico { background: #dc3545; }

        .matriz-risco-eixo-x {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 8px;
        }

        .eixo-labels {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          width: 100%;
          text-align: center;
          font-size: 12px;
          font-weight: 600;
          color: #495057;
        }

        @media (max-width: 768px) {
          .matriz-risco-cells {
            grid-template-rows: repeat(3, 100px);
          }
        }
      `}</style>
    </div>
  );
};

export default MatrizRiscosControles;
