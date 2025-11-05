import React, { useState } from 'react';
import './Artefatos.css';

type TipoStakeholder = 'interna' | 'externa';
type NivelInteresse = 'baixo' | 'medio' | 'alto';
type NivelInfluencia = 'baixo' | 'medio' | 'alto';

interface ParteInteressada {
  id: string;
  nome: string;
  tipo: TipoStakeholder;
  papel: string;
  interesse: NivelInteresse;
  influencia: NivelInfluencia;
  estrategia: string;
}

export const MapaStakeholders: React.FC = () => {
  const [stakeholders, setStakeholders] = useState<ParteInteressada[]>([
    {
      id: '1',
      nome: 'Secretaria X',
      tipo: 'externa',
      papel: 'Parceiro técnico',
      interesse: 'alto',
      influencia: 'alto',
      estrategia: 'Engajamento ativo'
    },
    {
      id: '2',
      nome: 'CGU',
      tipo: 'externa',
      papel: 'Órgão de controle',
      interesse: 'medio',
      influencia: 'alto',
      estrategia: 'Comunicação periódica'
    },
    {
      id: '3',
      nome: 'Coordenação interna',
      tipo: 'interna',
      papel: 'Executor',
      interesse: 'alto',
      influencia: 'alto',
      estrategia: 'Comunicação direta'
    }
  ]);

  const [filtroTipo, setFiltroTipo] = useState<TipoStakeholder | 'todos'>('todos');

  const adicionarStakeholder = () => {
    const novoStakeholder: ParteInteressada = {
      id: Date.now().toString(),
      nome: '',
      tipo: 'interna',
      papel: '',
      interesse: 'medio',
      influencia: 'medio',
      estrategia: ''
    };
    setStakeholders([...stakeholders, novoStakeholder]);
  };

  const removerStakeholder = (id: string) => {
    setStakeholders(stakeholders.filter(s => s.id !== id));
  };

  const atualizarStakeholder = (id: string, campo: keyof ParteInteressada, valor: string | TipoStakeholder | NivelInteresse | NivelInfluencia) => {
    setStakeholders(stakeholders.map(s =>
      s.id === id ? { ...s, [campo]: valor } : s
    ));
  };

  const getNivelColor = (nivel: NivelInteresse | NivelInfluencia): string => {
    const colors = {
      baixo: '#6c757d',
      medio: '#ffc107',
      alto: '#dc3545'
    };
    return colors[nivel];
  };

  const getNivelLabel = (nivel: NivelInteresse | NivelInfluencia): string => {
    const labels = {
      baixo: 'Baixo',
      medio: 'Médio',
      alto: 'Alto'
    };
    return labels[nivel];
  };

  const getPrioridade = (interesse: NivelInteresse, influencia: NivelInfluencia): string => {
    if (interesse === 'alto' && influencia === 'alto') return '🔴 Crítico';
    if (interesse === 'alto' || influencia === 'alto') return '🟠 Alto';
    if (interesse === 'medio' || influencia === 'medio') return '🟡 Médio';
    return '🟢 Baixo';
  };

  const exportarTxt = () => {
    let conteudo = '═══════════════════════════════════════════════════════════\n';
    conteudo += '  MAPA DE PARTES INTERESSADAS (STAKEHOLDERS)\n';
    conteudo += '  Domínio 5 - Partes Interessadas e Comunicação\n';
    conteudo += '═══════════════════════════════════════════════════════════\n\n';

    conteudo += '📊 PARTES INTERESSADAS MAPEADAS\n\n';

    stakeholders.forEach((stakeholder, index) => {
      conteudo += `${index + 1}. ${stakeholder.nome || '(não identificado)'}\n`;
      conteudo += `   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
      conteudo += `   🏢 Tipo:        ${stakeholder.tipo === 'interna' ? 'Interna' : 'Externa'}\n`;
      conteudo += `   👤 Papel:       ${stakeholder.papel || '—'}\n`;
      conteudo += `   📊 Interesse:   ${getNivelLabel(stakeholder.interesse)}\n`;
      conteudo += `   ⚡ Influência:  ${getNivelLabel(stakeholder.influencia)}\n`;
      conteudo += `   🎯 Prioridade:  ${getPrioridade(stakeholder.interesse, stakeholder.influencia)}\n`;
      conteudo += `   📋 Estratégia:  ${stakeholder.estrategia || '—'}\n`;
      conteudo += '\n';
    });

    // Estatísticas
    const totalInternas = stakeholders.filter(s => s.tipo === 'interna').length;
    const totalExternas = stakeholders.filter(s => s.tipo === 'externa').length;
    const totalCriticos = stakeholders.filter(s => s.interesse === 'alto' && s.influencia === 'alto').length;

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += '📈 ESTATÍSTICAS GERAIS\n\n';
    conteudo += `Total de stakeholders: ${stakeholders.length}\n`;
    conteudo += `Partes internas: ${totalInternas}\n`;
    conteudo += `Partes externas: ${totalExternas}\n`;
    conteudo += `Stakeholders críticos (alto interesse + alta influência): ${totalCriticos}\n`;
    conteudo += '\n';

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += `Exportado em: ${new Date().toLocaleString('pt-BR')}\n`;

    const blob = new Blob([conteudo], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'mapa_stakeholders.txt';
    link.click();
    URL.revokeObjectURL(url);
  };

  const stakeholdersFiltrados = filtroTipo === 'todos'
    ? stakeholders
    : stakeholders.filter(s => s.tipo === filtroTipo);

  const totalCriticos = stakeholders.filter(s => s.interesse === 'alto' && s.influencia === 'alto').length;
  const totalAltos = stakeholders.filter(s =>
    (s.interesse === 'alto' || s.influencia === 'alto') &&
    !(s.interesse === 'alto' && s.influencia === 'alto')
  ).length;

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <div>
          <h2>👥 Mapa de Partes Interessadas</h2>
          <p className="artefato-descricao">
            Identificar, classificar e priorizar os atores-chave do projeto (stakeholders).
          </p>
        </div>
        <button className="btn-exportar" onClick={exportarTxt}>
          📥 Exportar TXT
        </button>
      </div>

      {/* Estatísticas Resumidas */}
      <div className="estatisticas-stakeholders">
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-info">
            <div className="stat-value">{stakeholders.length}</div>
            <div className="stat-label">Total Stakeholders</div>
          </div>
        </div>
        <div className="stat-card stat-critico">
          <div className="stat-icon">🔴</div>
          <div className="stat-info">
            <div className="stat-value">{totalCriticos}</div>
            <div className="stat-label">Críticos</div>
          </div>
        </div>
        <div className="stat-card stat-alto">
          <div className="stat-icon">🟠</div>
          <div className="stat-info">
            <div className="stat-value">{totalAltos}</div>
            <div className="stat-label">Alta Prioridade</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🏢</div>
          <div className="stat-info">
            <div className="stat-value">{stakeholders.filter(s => s.tipo === 'externa').length}</div>
            <div className="stat-label">Externos</div>
          </div>
        </div>
      </div>

      <div className="artefato-controls">
        <button className="btn-adicionar" onClick={adicionarStakeholder}>
          ➕ Adicionar Parte Interessada
        </button>

        <div className="filtro-tipo">
          <label>Filtrar por tipo:</label>
          <select
            value={filtroTipo}
            onChange={(e) => setFiltroTipo(e.target.value as TipoStakeholder | 'todos')}
          >
            <option value="todos">Todos</option>
            <option value="interna">Interna</option>
            <option value="externa">Externa</option>
          </select>
        </div>
      </div>

      {/* Tabela de Stakeholders */}
      <div className="tabela-stakeholders">
        <table>
          <thead>
            <tr>
              <th style={{ width: '18%' }}>Parte Interessada</th>
              <th style={{ width: '10%' }}>Tipo</th>
              <th style={{ width: '15%' }}>Papel</th>
              <th style={{ width: '12%' }}>Interesse</th>
              <th style={{ width: '12%' }}>Influência</th>
              <th style={{ width: '10%' }}>Prioridade</th>
              <th style={{ width: '20%' }}>Estratégia</th>
              <th style={{ width: '3%' }}></th>
            </tr>
          </thead>
          <tbody>
            {stakeholdersFiltrados.map((stakeholder) => (
              <tr key={stakeholder.id}>
                <td>
                  <input
                    type="text"
                    value={stakeholder.nome}
                    onChange={(e) => atualizarStakeholder(stakeholder.id, 'nome', e.target.value)}
                    placeholder="Nome da parte"
                    className="input-inline"
                  />
                </td>
                <td>
                  <select
                    value={stakeholder.tipo}
                    onChange={(e) => atualizarStakeholder(stakeholder.id, 'tipo', e.target.value as TipoStakeholder)}
                    className="select-inline"
                  >
                    <option value="interna">Interna</option>
                    <option value="externa">Externa</option>
                  </select>
                </td>
                <td>
                  <input
                    type="text"
                    value={stakeholder.papel}
                    onChange={(e) => atualizarStakeholder(stakeholder.id, 'papel', e.target.value)}
                    placeholder="Papel"
                    className="input-inline"
                  />
                </td>
                <td>
                  <select
                    value={stakeholder.interesse}
                    onChange={(e) => atualizarStakeholder(stakeholder.id, 'interesse', e.target.value as NivelInteresse)}
                    className="select-inline"
                    style={{ backgroundColor: getNivelColor(stakeholder.interesse), color: 'white' }}
                  >
                    <option value="baixo">Baixo</option>
                    <option value="medio">Médio</option>
                    <option value="alto">Alto</option>
                  </select>
                </td>
                <td>
                  <select
                    value={stakeholder.influencia}
                    onChange={(e) => atualizarStakeholder(stakeholder.id, 'influencia', e.target.value as NivelInfluencia)}
                    className="select-inline"
                    style={{ backgroundColor: getNivelColor(stakeholder.influencia), color: 'white' }}
                  >
                    <option value="baixo">Baixo</option>
                    <option value="medio">Médio</option>
                    <option value="alto">Alto</option>
                  </select>
                </td>
                <td>
                  <span className="prioridade-badge">
                    {getPrioridade(stakeholder.interesse, stakeholder.influencia)}
                  </span>
                </td>
                <td>
                  <input
                    type="text"
                    value={stakeholder.estrategia}
                    onChange={(e) => atualizarStakeholder(stakeholder.id, 'estrategia', e.target.value)}
                    placeholder="Estratégia de engajamento"
                    className="input-inline"
                  />
                </td>
                <td>
                  <button
                    className="btn-remover-table"
                    onClick={() => removerStakeholder(stakeholder.id)}
                    title="Remover stakeholder"
                  >
                    ✕
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {stakeholdersFiltrados.length === 0 && (
        <div className="empty-state">
          <p>Nenhuma parte interessada encontrada para o filtro selecionado.</p>
        </div>
      )}

      <style>{`
        .estatisticas-stakeholders {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
          margin: 20px 0;
        }

        .tabela-stakeholders {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.05);
          margin-top: 20px;
          overflow-x: auto;
        }

        .tabela-stakeholders table {
          width: 100%;
          border-collapse: collapse;
          min-width: 900px;
        }

        .tabela-stakeholders th {
          background: #f8f9fa;
          padding: 12px;
          text-align: left;
          font-weight: 600;
          border-bottom: 2px solid #dee2e6;
          font-size: 14px;
        }

        .tabela-stakeholders td {
          padding: 10px;
          border-bottom: 1px solid #dee2e6;
        }

        .prioridade-badge {
          display: inline-block;
          padding: 6px 10px;
          border-radius: 16px;
          font-size: 12px;
          font-weight: 600;
          background: #f8f9fa;
          border: 1px solid #dee2e6;
        }

        .filtro-tipo {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .filtro-tipo label {
          font-weight: 500;
          font-size: 14px;
        }

        .filtro-tipo select {
          padding: 8px 12px;
          border: 1px solid #ced4da;
          border-radius: 6px;
          font-size: 14px;
        }

        @media (max-width: 768px) {
          .tabela-stakeholders {
            overflow-x: auto;
          }
        }
      `}</style>
    </div>
  );
};

export default MapaStakeholders;
