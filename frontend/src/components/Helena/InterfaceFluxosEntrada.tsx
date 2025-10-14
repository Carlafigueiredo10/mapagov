import React, { useState } from 'react';

interface OrigemSelecionada {
  tipo: string;
  especificacao?: string;
}

interface InterfaceFluxosEntradaProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

const InterfaceFluxosEntrada: React.FC<InterfaceFluxosEntradaProps> = ({ onConfirm }) => {
  const [origens, setOrigens] = useState<OrigemSelecionada[]>([]);
  const [outrasOrigens, setOutrasOrigens] = useState('');
  const [mostrarEspecificacao, setMostrarEspecificacao] = useState<Record<string, boolean>>({});
  const [especificacoes, setEspecificacoes] = useState<Record<string, string>>({});

  const opcoesOrigem = [
    { id: 'outra_area_decipex', label: 'De outra área da DECIPEX', requerEspecificacao: true },
    { id: 'fora_decipex', label: 'De fora da DECIPEX (outro órgão/entidade)', requerEspecificacao: true },
    { id: 'usuario_requerente', label: 'Do usuário/requerente diretamente', requerEspecificacao: false },
    { id: 'area_interna_cg', label: 'De outra área interna da sua Coordenação Geral', requerEspecificacao: true },
  ];

  const toggleOrigem = (id: string, requerEspecificacao: boolean) => {
    const jaExiste = origens.find(o => o.tipo === id);

    if (jaExiste) {
      // Remover origem
      setOrigens(origens.filter(o => o.tipo !== id));
      setMostrarEspecificacao(prev => ({ ...prev, [id]: false }));
      setEspecificacoes(prev => {
        const novo = { ...prev };
        delete novo[id];
        return novo;
      });
    } else {
      // Adicionar origem
      setOrigens([...origens, { tipo: id }]);
      if (requerEspecificacao) {
        setMostrarEspecificacao(prev => ({ ...prev, [id]: true }));
      }
    }
  };

  const handleEspecificacao = (id: string, valor: string) => {
    setEspecificacoes(prev => ({ ...prev, [id]: valor }));
    // Atualizar a origem com a especificação
    setOrigens(prev => prev.map(o =>
      o.tipo === id ? { ...o, especificacao: valor } : o
    ));
  };

  const handleConfirm = () => {
    if (origens.length === 0 && !outrasOrigens.trim()) {
      alert('Por favor, selecione ao menos uma origem ou descreva manualmente.');
      return;
    }

    // Montar resposta estruturada
    const respostaObj: any = {
      origens_selecionadas: origens.map(o => ({
        tipo: opcoesOrigem.find(op => op.id === o.tipo)?.label || o.tipo,
        especificacao: o.especificacao || null
      })),
      outras_origens: outrasOrigens.trim() || null
    };

    // Enviar como JSON string
    onConfirm(JSON.stringify(respostaObj));
  };

  const handleSkip = () => {
    onConfirm('nao_sei');
  };

  return (
    <div className="interface-container fade-in">
      <div className="interface-title">📥 Entrada do Processo</div>

      <div className="interface-content">
        <p style={{ marginBottom: '1.5rem', color: '#495057', lineHeight: '1.6' }}>
          Agora vamos começar a falar do seu processo. <strong>De onde ele vem?</strong><br />
          Ou seja, como ele chega até você?
        </p>

        <div style={{ marginBottom: '1.5rem' }}>
          <p style={{ fontSize: '0.9rem', color: '#6c757d', marginBottom: '1rem' }}>
            Selecione todas as origens que se aplicam:
          </p>

          {opcoesOrigem.map(opcao => (
            <div key={opcao.id} style={{ marginBottom: '1rem' }}>
              <div
                className={`option-card ${origens.find(o => o.tipo === opcao.id) ? 'selected' : ''}`}
                onClick={() => toggleOrigem(opcao.id, opcao.requerEspecificacao)}
                style={{
                  cursor: 'pointer',
                  padding: '1rem',
                  border: '2px solid #dee2e6',
                  borderRadius: '8px',
                  background: origens.find(o => o.tipo === opcao.id) ? '#e7f3ff' : 'white',
                  transition: 'all 0.2s'
                }}
              >
                <input
                  type="checkbox"
                  checked={!!origens.find(o => o.tipo === opcao.id)}
                  readOnly
                  style={{ marginRight: '0.75rem' }}
                />
                <label style={{ cursor: 'pointer', margin: 0 }}>{opcao.label}</label>
              </div>

              {mostrarEspecificacao[opcao.id] && (
                <div style={{ marginTop: '0.5rem', marginLeft: '2rem' }}>
                  <input
                    type="text"
                    placeholder="Especifique qual área/órgão..."
                    value={especificacoes[opcao.id] || ''}
                    onChange={(e) => handleEspecificacao(opcao.id, e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #ced4da',
                      borderRadius: '6px',
                      fontSize: '0.95rem'
                    }}
                  />
                </div>
              )}
            </div>
          ))}
        </div>

        <div style={{ marginTop: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500, color: '#495057' }}>
            📝 Ou descreva outras origens manualmente:
          </label>
          <textarea
            value={outrasOrigens}
            onChange={(e) => setOutrasOrigens(e.target.value)}
            placeholder="Ex: Recebo processos vindos da CGU, TCU, e também de outras coordenações..."
            rows={3}
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid #ced4da',
              borderRadius: '6px',
              fontSize: '0.95rem',
              resize: 'vertical'
            }}
          />
        </div>

        <div style={{
          marginTop: '1rem',
          padding: '0.75rem',
          background: '#e7f3ff',
          borderLeft: '4px solid #1351B4',
          borderRadius: '4px',
          fontSize: '0.85rem',
          color: '#004085'
        }}>
          💡 <strong>Dica:</strong> Queremos mapear todos os canais de entrada do processo.
          Pode selecionar múltiplas opções se o processo vem de vários lugares!
        </div>
      </div>

      <div className="action-buttons" style={{ marginTop: '1.5rem' }}>
        <button
          className="btn-interface btn-secondary"
          onClick={handleSkip}
        >
          Não Sei
        </button>
        <button
          className="btn-interface btn-primary"
          onClick={handleConfirm}
        >
          Confirmar
        </button>
      </div>

      <style>{`
        .action-buttons {
          display: flex;
          gap: 1rem;
        }

        .btn-interface {
          flex: 1;
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 6px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-secondary {
          background: #6c757d;
          color: white;
        }

        .btn-secondary:hover {
          background: #5a6268;
        }

        .btn-primary {
          background: #007bff;
          color: white;
        }

        .btn-primary:hover {
          background: #0056b3;
        }

        .option-card:hover {
          border-color: #1351B4 !important;
        }

        .option-card.selected {
          border-color: #1351B4 !important;
          background: #e7f3ff !important;
        }
      `}</style>
    </div>
  );
};

export default InterfaceFluxosEntrada;
