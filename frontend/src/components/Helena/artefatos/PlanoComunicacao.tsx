import React, { useState } from 'react';
import './Artefatos.css';

type CanalComunicacao = 'reuniao' | 'email' | 'relatorio' | 'portal' | 'whatsapp' | 'outro';
type FrequenciaComunicacao = 'diaria' | 'semanal' | 'quinzenal' | 'mensal' | 'trimestral' | 'sob_demanda';

interface ItemComunicacao {
  id: string;
  publicoAlvo: string;
  mensagemChave: string;
  canal: CanalComunicacao;
  frequencia: FrequenciaComunicacao;
  responsavel: string;
  observacoes: string;
}

export const PlanoComunicacao: React.FC = () => {
  const [itens, setItens] = useState<ItemComunicacao[]>([
    {
      id: '1',
      publicoAlvo: 'Equipe interna',
      mensagemChave: 'Status e prazos do projeto',
      canal: 'reuniao',
      frequencia: 'semanal',
      responsavel: 'Coordenação',
      observacoes: 'Reunião às segundas, 9h'
    },
    {
      id: '2',
      publicoAlvo: 'Comitê gestor',
      mensagemChave: 'Resultados e riscos',
      canal: 'relatorio',
      frequencia: 'mensal',
      responsavel: 'Gestor do projeto',
      observacoes: 'Enviar até dia 5 de cada mês'
    },
    {
      id: '3',
      publicoAlvo: 'Sociedade',
      mensagemChave: 'Avanços e impacto social',
      canal: 'portal',
      frequencia: 'trimestral',
      responsavel: 'Comunicação Social',
      observacoes: 'Publicar no portal institucional'
    }
  ]);

  const adicionarItem = () => {
    const novoItem: ItemComunicacao = {
      id: Date.now().toString(),
      publicoAlvo: '',
      mensagemChave: '',
      canal: 'email',
      frequencia: 'mensal',
      responsavel: '',
      observacoes: ''
    };
    setItens([...itens, novoItem]);
  };

  const removerItem = (id: string) => {
    setItens(itens.filter(i => i.id !== id));
  };

  const atualizarItem = (id: string, campo: keyof ItemComunicacao, valor: string | CanalComunicacao | FrequenciaComunicacao) => {
    setItens(itens.map(i =>
      i.id === id ? { ...i, [campo]: valor } : i
    ));
  };

  const getCanalLabel = (canal: CanalComunicacao): string => {
    const labels = {
      reuniao: '👥 Reunião',
      email: '📧 E-mail',
      relatorio: '📄 Relatório/SEI',
      portal: '🌐 Portal',
      whatsapp: '💬 WhatsApp',
      outro: '📋 Outro'
    };
    return labels[canal];
  };

  const getFrequenciaLabel = (frequencia: FrequenciaComunicacao): string => {
    const labels = {
      diaria: 'Diária',
      semanal: 'Semanal',
      quinzenal: 'Quinzenal',
      mensal: 'Mensal',
      trimestral: 'Trimestral',
      sob_demanda: 'Sob demanda'
    };
    return labels[frequencia];
  };

  const getCanalIcon = (canal: CanalComunicacao): string => {
    const icons = {
      reuniao: '👥',
      email: '📧',
      relatorio: '📄',
      portal: '🌐',
      whatsapp: '💬',
      outro: '📋'
    };
    return icons[canal];
  };

  const exportarTxt = () => {
    let conteudo = '═══════════════════════════════════════════════════════════\n';
    conteudo += '  PLANO DE COMUNICAÇÃO INSTITUCIONAL\n';
    conteudo += '  Domínio 5 - Partes Interessadas e Comunicação\n';
    conteudo += '═══════════════════════════════════════════════════════════\n\n';

    conteudo += '📋 ITENS DO PLANO DE COMUNICAÇÃO\n\n';

    itens.forEach((item, index) => {
      conteudo += `${index + 1}. Público-Alvo: ${item.publicoAlvo || '(não definido)'}\n`;
      conteudo += `   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
      conteudo += `   💬 Mensagem-Chave:  ${item.mensagemChave || '—'}\n`;
      conteudo += `   📢 Canal:           ${getCanalLabel(item.canal)}\n`;
      conteudo += `   📅 Frequência:      ${getFrequenciaLabel(item.frequencia)}\n`;
      conteudo += `   👤 Responsável:     ${item.responsavel || '—'}\n`;
      conteudo += `   📝 Observações:     ${item.observacoes || '—'}\n`;
      conteudo += '\n';
    });

    // Estatísticas
    const totalReuniao = itens.filter(i => i.canal === 'reuniao').length;
    const totalEmail = itens.filter(i => i.canal === 'email').length;
    const totalSemanal = itens.filter(i => i.frequencia === 'semanal').length;

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += '📊 ESTATÍSTICAS\n\n';
    conteudo += `Total de ações de comunicação: ${itens.length}\n`;
    conteudo += `Reuniões: ${totalReuniao}\n`;
    conteudo += `E-mails: ${totalEmail}\n`;
    conteudo += `Comunicações semanais: ${totalSemanal}\n`;
    conteudo += '\n';

    conteudo += '═══════════════════════════════════════════════════════════\n';
    conteudo += `Exportado em: ${new Date().toLocaleString('pt-BR')}\n`;

    const blob = new Blob([conteudo], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'plano_comunicacao.txt';
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <div>
          <h2>📢 Plano de Comunicação Institucional</h2>
          <p className="artefato-descricao">
            Planejar mensagens, canais, periodicidade e responsáveis pela comunicação do projeto.
          </p>
        </div>
        <button className="btn-exportar" onClick={exportarTxt}>
          📥 Exportar TXT
        </button>
      </div>

      {/* Estatísticas por Canal */}
      <div className="canais-stats">
        <div className="canal-stat">
          <div className="canal-icon">👥</div>
          <div className="canal-info">
            <div className="canal-valor">{itens.filter(i => i.canal === 'reuniao').length}</div>
            <div className="canal-label">Reuniões</div>
          </div>
        </div>
        <div className="canal-stat">
          <div className="canal-icon">📧</div>
          <div className="canal-info">
            <div className="canal-valor">{itens.filter(i => i.canal === 'email').length}</div>
            <div className="canal-label">E-mails</div>
          </div>
        </div>
        <div className="canal-stat">
          <div className="canal-icon">📄</div>
          <div className="canal-info">
            <div className="canal-valor">{itens.filter(i => i.canal === 'relatorio').length}</div>
            <div className="canal-label">Relatórios</div>
          </div>
        </div>
        <div className="canal-stat">
          <div className="canal-icon">🌐</div>
          <div className="canal-info">
            <div className="canal-valor">{itens.filter(i => i.canal === 'portal').length}</div>
            <div className="canal-label">Portal</div>
          </div>
        </div>
      </div>

      <div className="artefato-controls">
        <button className="btn-adicionar" onClick={adicionarItem}>
          ➕ Adicionar Ação de Comunicação
        </button>
      </div>

      {/* Cards de Comunicação */}
      <div className="comunicacao-cards-grid">
        {itens.map((item) => (
          <div key={item.id} className="comunicacao-card">
            <div className="comunicacao-card-header">
              <div className="canal-badge">
                {getCanalIcon(item.canal)} {getCanalLabel(item.canal).split(' ')[1]}
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
                <label>🎯 Público-Alvo</label>
                <input
                  type="text"
                  value={item.publicoAlvo}
                  onChange={(e) => atualizarItem(item.id, 'publicoAlvo', e.target.value)}
                  placeholder="Ex: Equipe interna, Comitê gestor..."
                />
              </div>

              <div className="form-group-comunicacao">
                <label>💬 Mensagem-Chave</label>
                <textarea
                  value={item.mensagemChave}
                  onChange={(e) => atualizarItem(item.id, 'mensagemChave', e.target.value)}
                  placeholder="Qual a mensagem principal a ser comunicada?"
                  rows={2}
                />
              </div>

              <div className="form-row">
                <div className="form-group-comunicacao">
                  <label>📢 Canal</label>
                  <select
                    value={item.canal}
                    onChange={(e) => atualizarItem(item.id, 'canal', e.target.value as CanalComunicacao)}
                  >
                    <option value="reuniao">👥 Reunião</option>
                    <option value="email">📧 E-mail</option>
                    <option value="relatorio">📄 Relatório/SEI</option>
                    <option value="portal">🌐 Portal</option>
                    <option value="whatsapp">💬 WhatsApp</option>
                    <option value="outro">📋 Outro</option>
                  </select>
                </div>

                <div className="form-group-comunicacao">
                  <label>📅 Frequência</label>
                  <select
                    value={item.frequencia}
                    onChange={(e) => atualizarItem(item.id, 'frequencia', e.target.value as FrequenciaComunicacao)}
                  >
                    <option value="diaria">Diária</option>
                    <option value="semanal">Semanal</option>
                    <option value="quinzenal">Quinzenal</option>
                    <option value="mensal">Mensal</option>
                    <option value="trimestral">Trimestral</option>
                    <option value="sob_demanda">Sob demanda</option>
                  </select>
                </div>
              </div>

              <div className="form-group-comunicacao">
                <label>👤 Responsável</label>
                <input
                  type="text"
                  value={item.responsavel}
                  onChange={(e) => atualizarItem(item.id, 'responsavel', e.target.value)}
                  placeholder="Quem será responsável por esta comunicação?"
                />
              </div>

              <div className="form-group-comunicacao">
                <label>📝 Observações</label>
                <textarea
                  value={item.observacoes}
                  onChange={(e) => atualizarItem(item.id, 'observacoes', e.target.value)}
                  placeholder="Detalhes adicionais (horário, formato, etc.)"
                  rows={2}
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      {itens.length === 0 && (
        <div className="empty-state">
          <p>Nenhuma ação de comunicação cadastrada. Clique em "Adicionar Ação de Comunicação" para começar.</p>
        </div>
      )}

      <style>{`
        .canais-stats {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
          gap: 15px;
          margin: 20px 0;
        }

        .canal-stat {
          background: white;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 15px;
          display: flex;
          align-items: center;
          gap: 12px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .canal-icon {
          font-size: 28px;
        }

        .canal-info {
          flex: 1;
        }

        .canal-valor {
          font-size: 24px;
          font-weight: 700;
          color: #212529;
        }

        .canal-label {
          font-size: 12px;
          color: #6c757d;
        }

        .comunicacao-cards-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
          gap: 20px;
          margin-top: 20px;
        }

        .comunicacao-card {
          background: white;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .comunicacao-card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .canal-badge {
          background: #0d6efd;
          color: white;
          padding: 6px 12px;
          border-radius: 16px;
          font-size: 13px;
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
          transition: all 0.2s;
        }

        .btn-remover-card:hover {
          background: #bb2d3b;
          transform: scale(1.1);
        }

        .comunicacao-form {
          display: flex;
          flex-direction: column;
          gap: 15px;
        }

        .form-group-comunicacao {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .form-group-comunicacao label {
          font-weight: 600;
          font-size: 13px;
          color: #495057;
        }

        .form-group-comunicacao input,
        .form-group-comunicacao select,
        .form-group-comunicacao textarea {
          padding: 10px;
          border: 1px solid #ced4da;
          border-radius: 6px;
          font-size: 14px;
          font-family: inherit;
        }

        .form-group-comunicacao input:focus,
        .form-group-comunicacao select:focus,
        .form-group-comunicacao textarea:focus {
          outline: none;
          border-color: #0d6efd;
          box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
        }

        .form-group-comunicacao textarea {
          resize: vertical;
        }

        .form-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 15px;
        }

        @media (max-width: 768px) {
          .comunicacao-cards-grid {
            grid-template-columns: 1fr;
          }

          .form-row {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default PlanoComunicacao;
