import React, { useState } from 'react';
import './Artefatos.css';

type Quadrante = 'Q1' | 'Q2' | 'Q3' | 'Q4';

interface StakeholderMatriz {
  id: string;
  nome: string;
  influencia: number; // 0-100
  interesse: number; // 0-100
  quadrante: Quadrante;
}

export const MatrizEngajamento: React.FC = () => {
  const [stakeholders, setStakeholders] = useState<StakeholderMatriz[]>([
    {
      id: '1',
      nome: 'Secretaria X',
      influencia: 85,
      interesse: 90,
      quadrante: 'Q1'
    },
    {
      id: '2',
      nome: 'CGU',
      influencia: 80,
      interesse: 45,
      quadrante: 'Q2'
    },
    {
      id: '3',
      nome: 'Equipe Técnica',
      influencia: 40,
      interesse: 85,
      quadrante: 'Q3'
    },
    {
      id: '4',
      nome: 'Fornecedor Y',
      influencia: 30,
      interesse: 25,
      quadrante: 'Q4'
    }
  ]);

  const adicionarStakeholder = () => {
    const novoStakeholder: StakeholderMatriz = {
      id: Date.now().toString(),
      nome: '',
      influencia: 50,
      interesse: 50,
      quadrante: calcularQuadrante(50, 50)
    };
    setStakeholders([...stakeholders, novoStakeholder]);
  };

  const removerStakeholder = (id: string) => {
    setStakeholders(stakeholders.filter(s => s.id !== id));
  };

  const calcularQuadrante = (influencia: number, interesse: number): Quadrante => {
    if (influencia >= 50 && interesse >= 50) return 'Q1';
    if (influencia >= 50 && interesse < 50) return 'Q2';
    if (influencia < 50 && interesse >= 50) return 'Q3';
    return 'Q4';
  };

  const atualizarStakeholder = (id: string, campo: 'nome' | 'influencia' | 'interesse', valor: string | number) => {
    setStakeholders(stakeholders.map(s => {
      if (s.id !== id) return s;

      const updated = { ...s, [campo]: valor };
      if (campo === 'influencia' || campo === 'interesse') {
        updated.quadrante = calcularQuadrante(
          campo === 'influencia' ? Number(valor) : s.influencia,
          campo === 'interesse' ? Number(valor) : s.interesse
        );
      }
      return updated;
    }));
  };

  const getQuadranteInfo = (quadrante: Quadrante) => {
    const info = {
      Q1: {
        nome: 'Q1: Envolver e Cocriar',
        cor: '#dc3545',
        descricao: 'Alta influência / Alto interesse',
        estrategia: 'Envolver profundamente, parceria estratégica'
      },
      Q2: {
        nome: 'Q2: Manter Informado',
        cor: '#fd7e14',
        descricao: 'Alta influência / Baixo interesse',
        estrategia: 'Manter satisfeito e informado sobre marcos'
      },
      Q3: {
        nome: 'Q3: Consultar e Valorizar',
        cor: '#ffc107',
        descricao: 'Baixa influência / Alto interesse',
        estrategia: 'Consultar e considerar opiniões'
      },
      Q4: {
        nome: 'Q4: Monitorar',
        cor: '#6c757d',
        descricao: 'Baixa influência / Baixo interesse',
        estrategia: 'Informar apenas sobre marcos principais'
      }
    };
    return info[quadrante];
  };

  const exportarTxt = () => {
    let conteudo = '═══════════════════════════════════════════════════════════\n';
    conteudo += '  MATRIZ DE ENGAJAMENTO (INFLUÊNCIA X INTERESSE)\n';
    conteudo += '  Domínio 5 - Partes Interessadas e Comunicação\n';
    conteudo += '═══════════════════════════════════════════════════════════\n\n';

    conteudo += '📊 DISTRIBUIÇÃO POR QUADRANTE\n\n';

    ['Q1', 'Q2', 'Q3', 'Q4'].forEach((q) => {
      const quadrante = q as Quadrante;
      const info = getQuadranteInfo(quadrante);
      const stakeholdersQuadrante = stakeholders.filter(s => s.quadrante === quadrante);

      conteudo += `${info.nome}\n`;
      conteudo += `${info.descricao}\n`;
      conteudo += `📋 Estratégia: ${info.estrategia}\n`;
      conteudo += `👥 Stakeholders (${stakeholdersQuadrante.length}):\n`;

      if (stakeholdersQuadrante.length > 0) {
        stakeholdersQuadrante.forEach(s => {
          conteudo += `   • ${s.nome || '(sem nome)'} (Influência: ${s.influencia}%, Interesse: ${s.interesse}%)\n`;
        });
      } else {
        conteudo += '   (nenhum)\n';
      }
      conteudo += '\n';
    });

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += `Total de stakeholders mapeados: ${stakeholders.length}\n`;
    conteudo += `Exportado em: ${new Date().toLocaleString('pt-BR')}\n`;

    const blob = new Blob([conteudo], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'matriz_engajamento.txt';
    link.click();
    URL.revokeObjectURL(url);
  };

  const stakeholdersQ1 = stakeholders.filter(s => s.quadrante === 'Q1').length;
  const stakeholdersQ2 = stakeholders.filter(s => s.quadrante === 'Q2').length;
  const stakeholdersQ3 = stakeholders.filter(s => s.quadrante === 'Q3').length;
  const stakeholdersQ4 = stakeholders.filter(s => s.quadrante === 'Q4').length;

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <div>
          <h2>📊 Matriz de Engajamento (Influência x Interesse)</h2>
          <p className="artefato-descricao">
            Visualizar graficamente onde concentrar esforços de comunicação e engajamento.
          </p>
        </div>
        <button className="btn-exportar" onClick={exportarTxt}>
          📥 Exportar TXT
        </button>
      </div>

      {/* Estatísticas por Quadrante */}
      <div className="quadrantes-stats">
        <div className="quadrante-stat" style={{ borderLeftColor: '#dc3545' }}>
          <div className="quadrante-label">Q1 - Envolver</div>
          <div className="quadrante-valor">{stakeholdersQ1}</div>
        </div>
        <div className="quadrante-stat" style={{ borderLeftColor: '#fd7e14' }}>
          <div className="quadrante-label">Q2 - Informar</div>
          <div className="quadrante-valor">{stakeholdersQ2}</div>
        </div>
        <div className="quadrante-stat" style={{ borderLeftColor: '#ffc107' }}>
          <div className="quadrante-label">Q3 - Consultar</div>
          <div className="quadrante-valor">{stakeholdersQ3}</div>
        </div>
        <div className="quadrante-stat" style={{ borderLeftColor: '#6c757d' }}>
          <div className="quadrante-label">Q4 - Monitorar</div>
          <div className="quadrante-valor">{stakeholdersQ4}</div>
        </div>
      </div>

      <div className="artefato-controls">
        <button className="btn-adicionar" onClick={adicionarStakeholder}>
          ➕ Adicionar Stakeholder
        </button>
      </div>

      {/* Matriz Visual 2x2 */}
      <div className="matriz-visual-container">
        <h3>📈 Matriz de Priorização</h3>

        <div className="matriz-2x2">
          <div className="matriz-eixo-y">
            <span className="eixo-label">Influência</span>
            <div className="eixo-line"></div>
          </div>

          <div className="matriz-grid">
            {/* Q3 - Baixa Influência / Alto Interesse */}
            <div className="matriz-quadrante q3" style={{ backgroundColor: '#fff9e6' }}>
              <div className="quadrante-header">
                <h4>Q3: Consultar e Valorizar</h4>
                <p>Baixa Influência / Alto Interesse</p>
              </div>
              <div className="stakeholders-bubbles">
                {stakeholders.filter(s => s.quadrante === 'Q3').map(s => (
                  <div key={s.id} className="stakeholder-bubble" style={{ backgroundColor: '#ffc107' }}>
                    {s.nome || '?'}
                  </div>
                ))}
              </div>
            </div>

            {/* Q1 - Alta Influência / Alto Interesse */}
            <div className="matriz-quadrante q1" style={{ backgroundColor: '#ffe6e6' }}>
              <div className="quadrante-header">
                <h4>Q1: Envolver e Cocriar</h4>
                <p>Alta Influência / Alto Interesse</p>
              </div>
              <div className="stakeholders-bubbles">
                {stakeholders.filter(s => s.quadrante === 'Q1').map(s => (
                  <div key={s.id} className="stakeholder-bubble" style={{ backgroundColor: '#dc3545' }}>
                    {s.nome || '?'}
                  </div>
                ))}
              </div>
            </div>

            {/* Q4 - Baixa Influência / Baixo Interesse */}
            <div className="matriz-quadrante q4" style={{ backgroundColor: '#f0f0f0' }}>
              <div className="quadrante-header">
                <h4>Q4: Monitorar</h4>
                <p>Baixa Influência / Baixo Interesse</p>
              </div>
              <div className="stakeholders-bubbles">
                {stakeholders.filter(s => s.quadrante === 'Q4').map(s => (
                  <div key={s.id} className="stakeholder-bubble" style={{ backgroundColor: '#6c757d' }}>
                    {s.nome || '?'}
                  </div>
                ))}
              </div>
            </div>

            {/* Q2 - Alta Influência / Baixo Interesse */}
            <div className="matriz-quadrante q2" style={{ backgroundColor: '#fff0e6' }}>
              <div className="quadrante-header">
                <h4>Q2: Manter Informado</h4>
                <p>Alta Influência / Baixo Interesse</p>
              </div>
              <div className="stakeholders-bubbles">
                {stakeholders.filter(s => s.quadrante === 'Q2').map(s => (
                  <div key={s.id} className="stakeholder-bubble" style={{ backgroundColor: '#fd7e14' }}>
                    {s.nome || '?'}
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="matriz-eixo-x">
            <div className="eixo-line"></div>
            <span className="eixo-label">Interesse</span>
          </div>
        </div>
      </div>

      {/* Tabela de Edição */}
      <div className="tabela-stakeholders-matriz">
        <h3>📝 Editar Stakeholders</h3>
        <table>
          <thead>
            <tr>
              <th style={{ width: '25%' }}>Nome</th>
              <th style={{ width: '25%' }}>Influência (%)</th>
              <th style={{ width: '25%' }}>Interesse (%)</th>
              <th style={{ width: '20%' }}>Quadrante</th>
              <th style={{ width: '5%' }}></th>
            </tr>
          </thead>
          <tbody>
            {stakeholders.map((stakeholder) => {
              const info = getQuadranteInfo(stakeholder.quadrante);
              return (
                <tr key={stakeholder.id}>
                  <td>
                    <input
                      type="text"
                      value={stakeholder.nome}
                      onChange={(e) => atualizarStakeholder(stakeholder.id, 'nome', e.target.value)}
                      placeholder="Nome do stakeholder"
                      className="input-inline"
                    />
                  </td>
                  <td>
                    <div className="slider-cell">
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={stakeholder.influencia}
                        onChange={(e) => atualizarStakeholder(stakeholder.id, 'influencia', parseInt(e.target.value))}
                        className="slider-range"
                      />
                      <span className="slider-value">{stakeholder.influencia}%</span>
                    </div>
                  </td>
                  <td>
                    <div className="slider-cell">
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={stakeholder.interesse}
                        onChange={(e) => atualizarStakeholder(stakeholder.id, 'interesse', parseInt(e.target.value))}
                        className="slider-range"
                      />
                      <span className="slider-value">{stakeholder.interesse}%</span>
                    </div>
                  </td>
                  <td>
                    <span
                      className="quadrante-badge"
                      style={{ backgroundColor: info.cor, color: 'white' }}
                    >
                      {info.nome.split(':')[0]}
                    </span>
                  </td>
                  <td>
                    <button
                      className="btn-remover-table"
                      onClick={() => removerStakeholder(stakeholder.id)}
                      title="Remover"
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

      {stakeholders.length === 0 && (
        <div className="empty-state">
          <p>Nenhum stakeholder cadastrado. Clique em "Adicionar Stakeholder" para começar.</p>
        </div>
      )}

      <style>{`
        .quadrantes-stats {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
          margin: 20px 0;
        }

        .quadrante-stat {
          background: white;
          border: 1px solid #dee2e6;
          border-left: 4px solid;
          border-radius: 8px;
          padding: 15px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .quadrante-label {
          font-size: 14px;
          font-weight: 600;
          color: #495057;
        }

        .quadrante-valor {
          font-size: 28px;
          font-weight: 700;
          color: #212529;
        }

        .matriz-visual-container {
          background: white;
          padding: 30px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.05);
          margin: 20px 0;
        }

        .matriz-visual-container h3 {
          margin-bottom: 25px;
          font-size: 18px;
        }

        .matriz-2x2 {
          display: flex;
          gap: 15px;
          position: relative;
        }

        .matriz-eixo-y {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 10px;
          writing-mode: vertical-rl;
          transform: rotate(180deg);
        }

        .matriz-eixo-x {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 10px;
        }

        .eixo-label {
          font-weight: 600;
          font-size: 14px;
          color: #495057;
        }

        .eixo-line {
          flex: 1;
          width: 2px;
          background: #dee2e6;
        }

        .matriz-grid {
          flex: 1;
          display: grid;
          grid-template-columns: 1fr 1fr;
          grid-template-rows: 1fr 1fr;
          gap: 2px;
          background: #dee2e6;
          border: 2px solid #dee2e6;
          border-radius: 8px;
          overflow: hidden;
          min-height: 400px;
        }

        .matriz-quadrante {
          padding: 20px;
          display: flex;
          flex-direction: column;
          gap: 15px;
        }

        .quadrante-header h4 {
          font-size: 16px;
          margin-bottom: 4px;
          color: #212529;
        }

        .quadrante-header p {
          font-size: 12px;
          color: #6c757d;
          margin: 0;
        }

        .stakeholders-bubbles {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          margin-top: 10px;
        }

        .stakeholder-bubble {
          padding: 8px 14px;
          border-radius: 20px;
          color: white;
          font-size: 13px;
          font-weight: 500;
          box-shadow: 0 2px 4px rgba(0,0,0,0.15);
          transition: transform 0.2s;
        }

        .stakeholder-bubble:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        .tabela-stakeholders-matriz {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.05);
          margin-top: 20px;
        }

        .tabela-stakeholders-matriz h3 {
          margin-bottom: 15px;
          font-size: 18px;
        }

        .tabela-stakeholders-matriz table {
          width: 100%;
          border-collapse: collapse;
        }

        .tabela-stakeholders-matriz th {
          background: #f8f9fa;
          padding: 12px;
          text-align: left;
          font-weight: 600;
          border-bottom: 2px solid #dee2e6;
          font-size: 14px;
        }

        .tabela-stakeholders-matriz td {
          padding: 10px;
          border-bottom: 1px solid #dee2e6;
        }

        .slider-cell {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .slider-range {
          flex: 1;
          height: 6px;
          -webkit-appearance: none;
          appearance: none;
          background: #e9ecef;
          border-radius: 3px;
          outline: none;
        }

        .slider-range::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 16px;
          height: 16px;
          background: #0d6efd;
          border-radius: 50%;
          cursor: pointer;
        }

        .slider-range::-moz-range-thumb {
          width: 16px;
          height: 16px;
          background: #0d6efd;
          border-radius: 50%;
          cursor: pointer;
          border: none;
        }

        .slider-value {
          font-weight: 600;
          font-size: 13px;
          min-width: 40px;
          text-align: right;
        }

        .quadrante-badge {
          display: inline-block;
          padding: 6px 12px;
          border-radius: 16px;
          font-size: 12px;
          font-weight: 600;
        }

        @media (max-width: 768px) {
          .matriz-grid {
            min-height: 300px;
          }

          .stakeholder-bubble {
            font-size: 11px;
            padding: 6px 10px;
          }
        }
      `}</style>
    </div>
  );
};

export default MatrizEngajamento;
