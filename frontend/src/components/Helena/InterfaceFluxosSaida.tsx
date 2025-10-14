import React, { useState } from 'react';

interface DestinoSelecionado {
  tipo: string;
  especificacao?: string;
}

interface InterfaceFluxosSaidaProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

const InterfaceFluxosSaida: React.FC<InterfaceFluxosSaidaProps> = ({ onConfirm }) => {
  const [destinos, setDestinos] = useState<DestinoSelecionado[]>([]);
  const [outrosDestinos, setOutrosDestinos] = useState('');
  const [mostrarEspecificacao, setMostrarEspecificacao] = useState<Record<string, boolean>>({});
  const [especificacoes, setEspecificacoes] = useState<Record<string, string>>({});

  const opcoesDestino = [
    { id: 'outra_area_decipex', label: 'Para outra área da DECIPEX', requerEspecificacao: true },
    { id: 'fora_decipex', label: 'Para fora da DECIPEX (outro órgão/entidade)', requerEspecificacao: true },
    { id: 'usuario_requerente', label: 'Para o usuário/requerente diretamente', requerEspecificacao: false },
    { id: 'area_interna_cg', label: 'Para outra área interna da sua Coordenação Geral', requerEspecificacao: true },
  ];

  const toggleDestino = (id: string, requerEspecificacao: boolean) => {
    const jaExiste = destinos.find(d => d.tipo === id);

    if (jaExiste) {
      // Remover destino
      setDestinos(destinos.filter(d => d.tipo !== id));
      setMostrarEspecificacao(prev => ({ ...prev, [id]: false }));
      setEspecificacoes(prev => {
        const novo = { ...prev };
        delete novo[id];
        return novo;
      });
    } else {
      // Adicionar destino
      setDestinos([...destinos, { tipo: id }]);
      if (requerEspecificacao) {
        setMostrarEspecificacao(prev => ({ ...prev, [id]: true }));
      }
    }
  };

  const handleEspecificacao = (id: string, valor: string) => {
    setEspecificacoes(prev => ({ ...prev, [id]: valor }));
    // Atualizar o destino com a especificação
    setDestinos(prev => prev.map(d =>
      d.tipo === id ? { ...d, especificacao: valor } : d
    ));
  };

  const handleConfirm = () => {
    if (destinos.length === 0 && !outrosDestinos.trim()) {
      alert('Por favor, selecione ao menos um destino ou descreva manualmente.');
      return;
    }

    // Montar resposta estruturada
    const respostaObj: any = {
      destinos_selecionados: destinos.map(d => ({
        tipo: opcoesDestino.find(op => op.id === d.tipo)?.label || d.tipo,
        especificacao: d.especificacao || null
      })),
      outros_destinos: outrosDestinos.trim() || null
    };

    // Enviar como JSON string
    onConfirm(JSON.stringify(respostaObj));
  };

  const handleSkip = () => {
    onConfirm('nao_sei');
  };

  return (
    <div className="interface-container fade-in">
      <div className="interface-title">📤 Saída do Processo</div>

      <div className="interface-content">
        <p style={{ marginBottom: '1.5rem', color: '#495057', lineHeight: '1.6' }}>
          E agora, <strong>para onde vai o resultado do seu trabalho?</strong><br />
          Para qual área você entrega ou encaminha?
        </p>

        <div style={{ marginBottom: '1.5rem' }}>
          <p style={{ fontSize: '0.9rem', color: '#6c757d', marginBottom: '1rem' }}>
            Selecione todos os destinos que se aplicam:
          </p>

          {opcoesDestino.map(opcao => (
            <div key={opcao.id} style={{ marginBottom: '1rem' }}>
              <div
                className={`option-card ${destinos.find(d => d.tipo === opcao.id) ? 'selected' : ''}`}
                onClick={() => toggleDestino(opcao.id, opcao.requerEspecificacao)}
                style={{
                  cursor: 'pointer',
                  padding: '1rem',
                  border: '2px solid #dee2e6',
                  borderRadius: '8px',
                  background: destinos.find(d => d.tipo === opcao.id) ? '#e7f3ff' : 'white',
                  transition: 'all 0.2s'
                }}
              >
                <input
                  type="checkbox"
                  checked={!!destinos.find(d => d.tipo === opcao.id)}
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
            📝 Ou descreva outros destinos manualmente:
          </label>
          <textarea
            value={outrosDestinos}
            onChange={(e) => setOutrosDestinos(e.target.value)}
            placeholder="Ex: Encaminho para a CGU, TCU, e também para outras coordenações dependendo do caso..."
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
          💡 <strong>Dica:</strong> Queremos mapear todos os destinos do resultado do processo.
          Pode selecionar múltiplas opções se o resultado vai para vários lugares!
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

export default InterfaceFluxosSaida;
