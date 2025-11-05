import React, { useState } from 'react';
import './Artefatos.css';

type StatusAtividade = 'planejada' | 'em_andamento' | 'concluida' | 'atrasada';

interface Atividade5W2H {
  id: string;
  what: string; // O quê
  why: string; // Por quê
  who: string; // Quem
  when: string; // Quando
  where: string; // Onde
  how: string; // Como
  howMuch: string; // Quanto custa
  status: StatusAtividade;
}

export const PlanoAtividades5W2H: React.FC = () => {
  const [atividades, setAtividades] = useState<Atividade5W2H[]>([
    {
      id: '1',
      what: 'Elaborar minuta do guia',
      why: 'Entregar produto 1',
      who: 'Equipe técnica',
      when: 'Maio/2025',
      where: 'Sede Brasília',
      how: 'Redigir e revisar',
      howMuch: 'Sem custo adicional',
      status: 'planejada'
    },
    {
      id: '2',
      what: 'Testar protótipo',
      why: 'Validar fluxo',
      who: 'Coordenação',
      when: 'Junho/2025',
      where: 'Plataforma Helena',
      how: 'Execução piloto',
      howMuch: 'R$ 8.000',
      status: 'planejada'
    }
  ]);

  const [filtroStatus, setFiltroStatus] = useState<StatusAtividade | 'todos'>('todos');

  const adicionarAtividade = () => {
    const novaAtividade: Atividade5W2H = {
      id: Date.now().toString(),
      what: '',
      why: '',
      who: '',
      when: '',
      where: '',
      how: '',
      howMuch: '',
      status: 'planejada'
    };
    setAtividades([...atividades, novaAtividade]);
  };

  const removerAtividade = (id: string) => {
    setAtividades(atividades.filter(a => a.id !== id));
  };

  const atualizarAtividade = (id: string, campo: keyof Atividade5W2H, valor: string | StatusAtividade) => {
    setAtividades(atividades.map(a =>
      a.id === id ? { ...a, [campo]: valor } : a
    ));
  };

  const exportarTxt = () => {
    let conteudo = '═══════════════════════════════════════════════════════════\n';
    conteudo += '  PLANO DE ATIVIDADES E RECURSOS (5W2H EXPANDIDO)\n';
    conteudo += '  Domínio 4 - Capacidades e Atividades\n';
    conteudo += '═══════════════════════════════════════════════════════════\n\n';

    atividades.forEach((atividade, index) => {
      conteudo += `${index + 1}. ${atividade.what || '(não preenchido)'}\n`;
      conteudo += `   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
      conteudo += `   📌 O quê (What):   ${atividade.what || '—'}\n`;
      conteudo += `   💡 Por quê (Why):  ${atividade.why || '—'}\n`;
      conteudo += `   👤 Quem (Who):     ${atividade.who || '—'}\n`;
      conteudo += `   📅 Quando (When):  ${atividade.when || '—'}\n`;
      conteudo += `   📍 Onde (Where):   ${atividade.where || '—'}\n`;
      conteudo += `   ⚙️  Como (How):     ${atividade.how || '—'}\n`;
      conteudo += `   💰 Quanto (How much): ${atividade.howMuch || '—'}\n`;
      conteudo += `   📊 Status:         ${getStatusLabel(atividade.status)}\n`;
      conteudo += '\n';
    });

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += `Exportado em: ${new Date().toLocaleString('pt-BR')}\n`;

    const blob = new Blob([conteudo], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'plano_atividades_5w2h.txt';
    link.click();
    URL.revokeObjectURL(url);
  };

  const getStatusLabel = (status: StatusAtividade): string => {
    const labels = {
      planejada: '⚙️ Planejada',
      em_andamento: '⏳ Em andamento',
      concluida: '✅ Concluída',
      atrasada: '🔴 Atrasada'
    };
    return labels[status];
  };

  const getStatusColor = (status: StatusAtividade): string => {
    const colors = {
      planejada: '#6c757d',
      em_andamento: '#0d6efd',
      concluida: '#198754',
      atrasada: '#dc3545'
    };
    return colors[status];
  };

  const atividadesFiltradas = filtroStatus === 'todos'
    ? atividades
    : atividades.filter(a => a.status === filtroStatus);

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <div>
          <h2>📋 Plano de Atividades e Recursos (5W2H expandido)</h2>
          <p className="artefato-descricao">
            Detalhar tarefas, responsáveis, prazos e recursos necessários para executar o projeto.
          </p>
        </div>
        <button className="btn-exportar" onClick={exportarTxt}>
          📥 Exportar TXT
        </button>
      </div>

      <div className="artefato-controls">
        <button className="btn-adicionar" onClick={adicionarAtividade}>
          ➕ Adicionar Atividade
        </button>

        <div className="filtro-status">
          <label>Filtrar por status:</label>
          <select
            value={filtroStatus}
            onChange={(e) => setFiltroStatus(e.target.value as StatusAtividade | 'todos')}
          >
            <option value="todos">Todos</option>
            <option value="planejada">Planejada</option>
            <option value="em_andamento">Em andamento</option>
            <option value="concluida">Concluída</option>
            <option value="atrasada">Atrasada</option>
          </select>
        </div>
      </div>

      <div className="plano-atividades-grid">
        {atividadesFiltradas.map((atividade) => (
          <div key={atividade.id} className="atividade-card">
            <div className="atividade-card-header">
              <div className="atividade-status-badge" style={{ backgroundColor: getStatusColor(atividade.status) }}>
                {getStatusLabel(atividade.status)}
              </div>
              <button
                className="btn-remover-small"
                onClick={() => removerAtividade(atividade.id)}
                title="Remover atividade"
              >
                ✕
              </button>
            </div>

            <div className="form-5w2h">
              <div className="form-group-5w2h">
                <label>📌 O quê (What)</label>
                <input
                  type="text"
                  value={atividade.what}
                  onChange={(e) => atualizarAtividade(atividade.id, 'what', e.target.value)}
                  placeholder="Descrição da atividade"
                />
              </div>

              <div className="form-group-5w2h">
                <label>💡 Por quê (Why)</label>
                <input
                  type="text"
                  value={atividade.why}
                  onChange={(e) => atualizarAtividade(atividade.id, 'why', e.target.value)}
                  placeholder="Justificativa/objetivo"
                />
              </div>

              <div className="form-group-5w2h">
                <label>👤 Quem (Who)</label>
                <input
                  type="text"
                  value={atividade.who}
                  onChange={(e) => atualizarAtividade(atividade.id, 'who', e.target.value)}
                  placeholder="Responsável"
                />
              </div>

              <div className="form-group-5w2h">
                <label>📅 Quando (When)</label>
                <input
                  type="text"
                  value={atividade.when}
                  onChange={(e) => atualizarAtividade(atividade.id, 'when', e.target.value)}
                  placeholder="Prazo/período"
                />
              </div>

              <div className="form-group-5w2h">
                <label>📍 Onde (Where)</label>
                <input
                  type="text"
                  value={atividade.where}
                  onChange={(e) => atualizarAtividade(atividade.id, 'where', e.target.value)}
                  placeholder="Local/plataforma"
                />
              </div>

              <div className="form-group-5w2h">
                <label>⚙️ Como (How)</label>
                <input
                  type="text"
                  value={atividade.how}
                  onChange={(e) => atualizarAtividade(atividade.id, 'how', e.target.value)}
                  placeholder="Método/processo"
                />
              </div>

              <div className="form-group-5w2h">
                <label>💰 Quanto (How much)</label>
                <input
                  type="text"
                  value={atividade.howMuch}
                  onChange={(e) => atualizarAtividade(atividade.id, 'howMuch', e.target.value)}
                  placeholder="Custo estimado"
                />
              </div>

              <div className="form-group-5w2h">
                <label>📊 Status</label>
                <select
                  value={atividade.status}
                  onChange={(e) => atualizarAtividade(atividade.id, 'status', e.target.value as StatusAtividade)}
                  style={{ backgroundColor: getStatusColor(atividade.status), color: 'white' }}
                >
                  <option value="planejada">⚙️ Planejada</option>
                  <option value="em_andamento">⏳ Em andamento</option>
                  <option value="concluida">✅ Concluída</option>
                  <option value="atrasada">🔴 Atrasada</option>
                </select>
              </div>
            </div>
          </div>
        ))}
      </div>

      {atividadesFiltradas.length === 0 && (
        <div className="empty-state">
          <p>Nenhuma atividade encontrada para o filtro selecionado.</p>
        </div>
      )}

      <style>{`
        .plano-atividades-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
          gap: 20px;
          margin-top: 20px;
        }

        .atividade-card {
          background: white;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .atividade-card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .atividade-status-badge {
          padding: 6px 12px;
          border-radius: 16px;
          color: white;
          font-size: 13px;
          font-weight: 500;
        }

        .form-5w2h {
          display: grid;
          gap: 15px;
        }

        .form-group-5w2h {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .form-group-5w2h label {
          font-weight: 600;
          font-size: 14px;
          color: #495057;
        }

        .form-group-5w2h input,
        .form-group-5w2h select {
          padding: 10px;
          border: 1px solid #ced4da;
          border-radius: 6px;
          font-size: 14px;
        }

        .form-group-5w2h input:focus,
        .form-group-5w2h select:focus {
          outline: none;
          border-color: #0d6efd;
          box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
        }

        .filtro-status {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .filtro-status label {
          font-weight: 500;
          font-size: 14px;
        }

        .filtro-status select {
          padding: 8px 12px;
          border: 1px solid #ced4da;
          border-radius: 6px;
          font-size: 14px;
        }

        .btn-remover-small {
          background: #dc3545;
          color: white;
          border: none;
          border-radius: 50%;
          width: 28px;
          height: 28px;
          cursor: pointer;
          font-size: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }

        .btn-remover-small:hover {
          background: #bb2d3b;
          transform: scale(1.1);
        }

        @media (max-width: 768px) {
          .plano-atividades-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default PlanoAtividades5W2H;
