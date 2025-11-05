import React, { useState } from 'react';
import './Artefatos.css';

type CanalInteracao = 'reuniao' | 'email' | 'telefone' | 'whatsapp' | 'oficio' | 'outro';
type StatusEncaminhamento = 'pendente' | 'em_analise' | 'concluido' | 'nao_aplicavel';

interface RegistroInteracao {
  id: string;
  data: string;
  parteEnvolvida: string;
  canal: CanalInteracao;
  feedbackPrincipal: string;
  encaminhamento: string;
  statusEncaminhamento: StatusEncaminhamento;
  responsavel: string;
}

export const RegistroFeedbacks: React.FC = () => {
  const [registros, setRegistros] = useState<RegistroInteracao[]>([
    {
      id: '1',
      data: '2025-03-15',
      parteEnvolvida: 'Secretaria X',
      canal: 'reuniao',
      feedbackPrincipal: 'Solicitou mais dados sobre indicadores de desempenho',
      encaminhamento: 'Incluir no relatório trimestral',
      statusEncaminhamento: 'em_analise',
      responsavel: 'Equipe Técnica'
    },
    {
      id: '2',
      data: '2025-03-25',
      parteEnvolvida: 'CGU',
      canal: 'oficio',
      feedbackPrincipal: 'Sugeriu nova métrica de transparência',
      encaminhamento: 'Encaminhado ao comitê gestor',
      statusEncaminhamento: 'concluido',
      responsavel: 'Coordenação'
    },
    {
      id: '3',
      data: '2025-04-02',
      parteEnvolvida: 'Equipe de campo',
      canal: 'whatsapp',
      feedbackPrincipal: 'Dificuldades operacionais no sistema',
      encaminhamento: 'Agendar treinamento adicional',
      statusEncaminhamento: 'pendente',
      responsavel: 'TI'
    }
  ]);

  const [filtroStatus, setFiltroStatus] = useState<StatusEncaminhamento | 'todos'>('todos');

  const adicionarRegistro = () => {
    const novoRegistro: RegistroInteracao = {
      id: Date.now().toString(),
      data: new Date().toISOString().split('T')[0],
      parteEnvolvida: '',
      canal: 'reuniao',
      feedbackPrincipal: '',
      encaminhamento: '',
      statusEncaminhamento: 'pendente',
      responsavel: ''
    };
    setRegistros([...registros, novoRegistro]);
  };

  const removerRegistro = (id: string) => {
    setRegistros(registros.filter(r => r.id !== id));
  };

  const atualizarRegistro = (id: string, campo: keyof RegistroInteracao, valor: string | CanalInteracao | StatusEncaminhamento) => {
    setRegistros(registros.map(r =>
      r.id === id ? { ...r, [campo]: valor } : r
    ));
  };

  const getCanalLabel = (canal: CanalInteracao): string => {
    const labels = {
      reuniao: '👥 Reunião',
      email: '📧 E-mail',
      telefone: '📞 Telefone',
      whatsapp: '💬 WhatsApp',
      oficio: '📄 Ofício',
      outro: '📋 Outro'
    };
    return labels[canal];
  };

  const getStatusLabel = (status: StatusEncaminhamento): string => {
    const labels = {
      pendente: '⏳ Pendente',
      em_analise: '⚙️ Em análise',
      concluido: '✅ Concluído',
      nao_aplicavel: '🚫 Não aplicável'
    };
    return labels[status];
  };

  const getStatusColor = (status: StatusEncaminhamento): string => {
    const colors = {
      pendente: '#ffc107',
      em_analise: '#0d6efd',
      concluido: '#198754',
      nao_aplicavel: '#6c757d'
    };
    return colors[status];
  };

  const exportarTxt = () => {
    let conteudo = '═══════════════════════════════════════════════════════════\n';
    conteudo += '  REGISTRO DE INTERAÇÕES E FEEDBACKS\n';
    conteudo += '  Domínio 5 - Partes Interessadas e Comunicação\n';
    conteudo += '═══════════════════════════════════════════════════════════\n\n';

    conteudo += '📋 HISTÓRICO DE INTERAÇÕES\n\n';

    registros
      .sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime())
      .forEach((registro, index) => {
        conteudo += `${index + 1}. ${new Date(registro.data).toLocaleDateString('pt-BR')} - ${registro.parteEnvolvida || '(não identificado)'}\n`;
        conteudo += `   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
        conteudo += `   📢 Canal:          ${getCanalLabel(registro.canal)}\n`;
        conteudo += `   💬 Feedback:       ${registro.feedbackPrincipal || '—'}\n`;
        conteudo += `   📋 Encaminhamento: ${registro.encaminhamento || '—'}\n`;
        conteudo += `   📊 Status:         ${getStatusLabel(registro.statusEncaminhamento)}\n`;
        conteudo += `   👤 Responsável:    ${registro.responsavel || '—'}\n`;
        conteudo += '\n';
      });

    // Estatísticas
    const totalPendente = registros.filter(r => r.statusEncaminhamento === 'pendente').length;
    const totalEmAnalise = registros.filter(r => r.statusEncaminhamento === 'em_analise').length;
    const totalConcluido = registros.filter(r => r.statusEncaminhamento === 'concluido').length;

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += '📊 ESTATÍSTICAS\n\n';
    conteudo += `Total de interações registradas: ${registros.length}\n`;
    conteudo += `Pendentes: ${totalPendente}\n`;
    conteudo += `Em análise: ${totalEmAnalise}\n`;
    conteudo += `Concluídos: ${totalConcluido}\n`;
    conteudo += '\n';

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += `Exportado em: ${new Date().toLocaleString('pt-BR')}\n`;

    const blob = new Blob([conteudo], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'registro_feedbacks.txt';
    link.click();
    URL.revokeObjectURL(url);
  };

  const registrosFiltrados = filtroStatus === 'todos'
    ? registros
    : registros.filter(r => r.statusEncaminhamento === filtroStatus);

  const totalPendente = registros.filter(r => r.statusEncaminhamento === 'pendente').length;
  const totalEmAnalise = registros.filter(r => r.statusEncaminhamento === 'em_analise').length;
  const totalConcluido = registros.filter(r => r.statusEncaminhamento === 'concluido').length;

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <div>
          <h2>📝 Registro de Interações e Feedbacks</h2>
          <p className="artefato-descricao">
            Documentar reuniões, percepções e respostas obtidas das partes interessadas.
          </p>
        </div>
        <button className="btn-exportar" onClick={exportarTxt}>
          📥 Exportar TXT
        </button>
      </div>

      {/* Estatísticas de Status */}
      <div className="status-feedbacks-stats">
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
            <div className="stat-value">{totalEmAnalise}</div>
            <div className="stat-label">Em Análise</div>
          </div>
        </div>
        <div className="stat-card stat-concluido">
          <div className="stat-icon">✅</div>
          <div className="stat-info">
            <div className="stat-value">{totalConcluido}</div>
            <div className="stat-label">Concluídos</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-info">
            <div className="stat-value">{registros.length}</div>
            <div className="stat-label">Total</div>
          </div>
        </div>
      </div>

      {/* Alerta de Pendências */}
      {totalPendente > 0 && (
        <div className="alerta-pendencias">
          <span className="alerta-icon">⚠️</span>
          <strong>Atenção:</strong> {totalPendente} feedback(s) pendente(s) de encaminhamento!
        </div>
      )}

      <div className="artefato-controls">
        <button className="btn-adicionar" onClick={adicionarRegistro}>
          ➕ Adicionar Registro de Feedback
        </button>

        <div className="filtro-status">
          <label>Filtrar por status:</label>
          <select
            value={filtroStatus}
            onChange={(e) => setFiltroStatus(e.target.value as StatusEncaminhamento | 'todos')}
          >
            <option value="todos">Todos</option>
            <option value="pendente">Pendente</option>
            <option value="em_analise">Em análise</option>
            <option value="concluido">Concluído</option>
            <option value="nao_aplicavel">Não aplicável</option>
          </select>
        </div>
      </div>

      {/* Tabela de Registros */}
      <div className="tabela-feedbacks">
        <table>
          <thead>
            <tr>
              <th style={{ width: '10%' }}>Data</th>
              <th style={{ width: '15%' }}>Parte Envolvida</th>
              <th style={{ width: '10%' }}>Canal</th>
              <th style={{ width: '22%' }}>Feedback Principal</th>
              <th style={{ width: '20%' }}>Encaminhamento</th>
              <th style={{ width: '10%' }}>Status</th>
              <th style={{ width: '10%' }}>Responsável</th>
              <th style={{ width: '3%' }}></th>
            </tr>
          </thead>
          <tbody>
            {registrosFiltrados
              .sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime())
              .map((registro) => (
                <tr key={registro.id}>
                  <td>
                    <input
                      type="date"
                      value={registro.data}
                      onChange={(e) => atualizarRegistro(registro.id, 'data', e.target.value)}
                      className="input-inline input-date"
                    />
                  </td>
                  <td>
                    <input
                      type="text"
                      value={registro.parteEnvolvida}
                      onChange={(e) => atualizarRegistro(registro.id, 'parteEnvolvida', e.target.value)}
                      placeholder="Nome da parte"
                      className="input-inline"
                    />
                  </td>
                  <td>
                    <select
                      value={registro.canal}
                      onChange={(e) => atualizarRegistro(registro.id, 'canal', e.target.value as CanalInteracao)}
                      className="select-inline"
                    >
                      <option value="reuniao">👥 Reunião</option>
                      <option value="email">📧 E-mail</option>
                      <option value="telefone">📞 Telefone</option>
                      <option value="whatsapp">💬 WhatsApp</option>
                      <option value="oficio">📄 Ofício</option>
                      <option value="outro">📋 Outro</option>
                    </select>
                  </td>
                  <td>
                    <input
                      type="text"
                      value={registro.feedbackPrincipal}
                      onChange={(e) => atualizarRegistro(registro.id, 'feedbackPrincipal', e.target.value)}
                      placeholder="Resumo do feedback"
                      className="input-inline"
                    />
                  </td>
                  <td>
                    <input
                      type="text"
                      value={registro.encaminhamento}
                      onChange={(e) => atualizarRegistro(registro.id, 'encaminhamento', e.target.value)}
                      placeholder="Ação tomada"
                      className="input-inline"
                    />
                  </td>
                  <td>
                    <select
                      value={registro.statusEncaminhamento}
                      onChange={(e) => atualizarRegistro(registro.id, 'statusEncaminhamento', e.target.value as StatusEncaminhamento)}
                      className="select-inline"
                      style={{ backgroundColor: getStatusColor(registro.statusEncaminhamento), color: 'white' }}
                    >
                      <option value="pendente">⏳ Pendente</option>
                      <option value="em_analise">⚙️ Em análise</option>
                      <option value="concluido">✅ Concluído</option>
                      <option value="nao_aplicavel">🚫 Não aplicável</option>
                    </select>
                  </td>
                  <td>
                    <input
                      type="text"
                      value={registro.responsavel}
                      onChange={(e) => atualizarRegistro(registro.id, 'responsavel', e.target.value)}
                      placeholder="Responsável"
                      className="input-inline"
                    />
                  </td>
                  <td>
                    <button
                      className="btn-remover-table"
                      onClick={() => removerRegistro(registro.id)}
                      title="Remover registro"
                    >
                      ✕
                    </button>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      {registrosFiltrados.length === 0 && (
        <div className="empty-state">
          <p>Nenhum registro encontrado para o filtro selecionado.</p>
        </div>
      )}

      <style>{`
        .status-feedbacks-stats {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
          gap: 15px;
          margin: 20px 0;
        }

        .stat-card.stat-pendente {
          border-left: 4px solid #ffc107;
        }

        .stat-card.stat-analise {
          border-left: 4px solid #0d6efd;
        }

        .stat-card.stat-concluido {
          border-left: 4px solid #198754;
        }

        .alerta-pendencias {
          background: #fff3cd;
          border: 1px solid #ffc107;
          border-left: 4px solid #ffc107;
          padding: 15px;
          border-radius: 6px;
          display: flex;
          align-items: center;
          gap: 10px;
          margin: 20px 0;
          font-size: 14px;
        }

        .tabela-feedbacks {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.05);
          margin-top: 20px;
          overflow-x: auto;
        }

        .tabela-feedbacks table {
          width: 100%;
          border-collapse: collapse;
          min-width: 1000px;
        }

        .tabela-feedbacks th {
          background: #f8f9fa;
          padding: 12px;
          text-align: left;
          font-weight: 600;
          border-bottom: 2px solid #dee2e6;
          font-size: 14px;
        }

        .tabela-feedbacks td {
          padding: 10px;
          border-bottom: 1px solid #dee2e6;
        }

        .input-date {
          font-family: inherit;
        }

        @media (max-width: 768px) {
          .tabela-feedbacks {
            overflow-x: auto;
          }
        }
      `}</style>
    </div>
  );
};

export default RegistroFeedbacks;
