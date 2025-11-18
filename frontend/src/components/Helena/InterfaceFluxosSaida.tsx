import React, { useState } from 'react';

interface DestinoSelecionado {
  tipo: string;
  especificacao?: string;
  area_decipex?: string;
  orgao_centralizado?: string;
  canais_atendimento?: string[];
}

interface AreaOrganizacional {
  codigo: string;
  nome: string;
  sigla?: string;
}

interface OrgaoCentralizado {
  sigla: string;
  nome_completo: string;
  observacao?: string;
}

interface CanalAtendimento {
  codigo: string;
  nome: string;
  descricao?: string;
}

interface OpcaoDestino {
  id: string;
  label: string;
  requerEspecificacao: boolean;
  requerAreaDecipex?: boolean;
  requerOrgaoCentralizado?: boolean;
  requerCanaisAtendimento?: boolean;
  obrigatorio?: boolean;
  opcoesPredefinidas?: string[];
}

interface InterfaceFluxosSaidaProps {
  dados?: {
    areas_organizacionais?: AreaOrganizacional[];
    orgaos_centralizados?: OrgaoCentralizado[];
    canais_atendimento?: CanalAtendimento[];
  };
  onConfirm: (resposta: string) => void;
}

const InterfaceFluxosSaida: React.FC<InterfaceFluxosSaidaProps> = ({ dados, onConfirm }) => {
  const [destinos, setDestinos] = useState<DestinoSelecionado[]>([]);
  const [outrosDestinos, setOutrosDestinos] = useState('');
  const [mostrarEspecificacao, setMostrarEspecificacao] = useState<Record<string, boolean>>({});
  const [especificacoes, setEspecificacoes] = useState<Record<string, string>>({});
  const [areaDecipexSelecionada, setAreaDecipexSelecionada] = useState<Record<string, string>>({});
  const [orgaoCentralizadoSelecionado, setOrgaoCentralizadoSelecionado] = useState<Record<string, string>>({});
  const [canaisSelecionados, setCanaisSelecionados] = useState<Record<string, string[]>>({});
  const [isLoading, setIsLoading] = useState(false); // ✅ Proteção contra duplo clique

  // Usar dados do backend (do CSV) em vez de hardcoded
  const areasDecipex = dados?.areas_organizacionais || [];
  const orgaosCentralizados = dados?.orgaos_centralizados || [];
  const canaisAtendimento = dados?.canais_atendimento || [];

  const opcoesDestino: OpcaoDestino[] = [
    { id: 'outra_area_decipex', label: 'Para outra área da DECIPEX', requerEspecificacao: true, requerAreaDecipex: true },
    { id: 'orgao_centralizado', label: 'Para algum órgão centralizado', requerEspecificacao: true, requerOrgaoCentralizado: true },
    { id: 'fora_decipex', label: 'Para fora da DECIPEX (outro órgão/entidade)', requerEspecificacao: true, obrigatorio: true },
    { id: 'usuario_requerente', label: 'Para o usuário/requerente diretamente', requerEspecificacao: true, requerCanaisAtendimento: true },
    { id: 'area_interna_cg', label: 'Para outra área interna da sua Coordenação Geral', requerEspecificacao: true, obrigatorio: true },
    { id: 'orgaos_controle', label: 'Órgãos de Controle', requerEspecificacao: true, opcoesPredefinidas: ['TCU - Indícios', 'TCU - Acórdão', 'CGU'] },
  ];

  const toggleDestino = (id: string, requerEspecificacao: boolean) => {
    const jaExiste = destinos.find(o => o.tipo === id);

    if (jaExiste) {
      // Remover destino
      setDestinos(destinos.filter(o => o.tipo !== id));
      setMostrarEspecificacao(prev => ({ ...prev, [id]: false }));
      setEspecificacoes(prev => {
        const novo = { ...prev };
        delete novo[id];
        return novo;
      });
      setAreaDecipexSelecionada(prev => {
        const novo = { ...prev };
        delete novo[id];
        return novo;
      });
      setOrgaoCentralizadoSelecionado(prev => {
        const novo = { ...prev };
        delete novo[id];
        return novo;
      });
      setCanaisSelecionados(prev => {
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
    setDestinos(prev => prev.map(o =>
      o.tipo === id ? { ...o, especificacao: valor } : o
    ));
  };

  const handleAreaDecipex = (id: string, valor: string) => {
    setAreaDecipexSelecionada(prev => ({ ...prev, [id]: valor }));
    setDestinos(prev => prev.map(o =>
      o.tipo === id ? { ...o, area_decipex: valor } : o
    ));
  };

  const handleOrgaoCentralizado = (id: string, valor: string) => {
    setOrgaoCentralizadoSelecionado(prev => ({ ...prev, [id]: valor }));
    setDestinos(prev => prev.map(o =>
      o.tipo === id ? { ...o, orgao_centralizado: valor } : o
    ));
  };

  const handleCanaisAtendimento = (id: string, codigo: string, checked: boolean) => {
    setCanaisSelecionados(prev => {
      const canaisAtuais = prev[id] || [];
      const novosCanais = checked
        ? [...canaisAtuais, codigo]
        : canaisAtuais.filter(c => c !== codigo);
      return { ...prev, [id]: novosCanais };
    });

    setDestinos(prev => prev.map(o =>
      o.tipo === id ? { ...o, canais_atendimento: canaisSelecionados[id] || [] } : o
    ));
  };

  const handleConfirm = () => {
    if (isLoading) return; // Evitar duplo clique

    // Validação: pelo menos um destino ou campo livre
    if (destinos.length === 0 && !outrosDestinos.trim()) {
      alert('Por favor, selecione ao menos um destino ou descreva manualmente.');
      return;
    }

    // Validar campos obrigatórios
    for (const destino of destinos) {
      const opcao = opcoesDestino.find(op => op.id === destino.tipo);
      if (opcao?.obrigatorio && !destino.especificacao?.trim()) {
        alert(`Por favor, especifique "${opcao.label}"`);
        return;
      }
    }

    setIsLoading(true);

    // Montar resposta estruturada
    const respostaObj: any = {
      destinos_selecionados: destinos.map(o => {
        const opcao = opcoesDestino.find(op => op.id === o.tipo);
        return {
          tipo: opcao?.label || o.tipo,
          especificacao: o.especificacao || null,
          area_decipex: o.area_decipex || null,
          orgao_centralizado: o.orgao_centralizado || null,
          canais_atendimento: o.canais_atendimento || null
        };
      }),
      outros_destinos: outrosDestinos.trim() || null
    };

    // Enviar como JSON string
    onConfirm(JSON.stringify(respostaObj));
  };

  const handleSkip = () => {
    if (isLoading) return;
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
                className={`option-card ${destinos.find(o => o.tipo === opcao.id) ? 'selected' : ''}`}
                onClick={() => toggleDestino(opcao.id, opcao.requerEspecificacao)}
                style={{
                  cursor: 'pointer',
                  padding: '1rem',
                  border: '2px solid #dee2e6',
                  borderRadius: '8px',
                  background: destinos.find(o => o.tipo === opcao.id) ? '#e7f3ff' : 'white',
                  transition: 'all 0.2s'
                }}
              >
                <input
                  type="checkbox"
                  checked={!!destinos.find(o => o.tipo === opcao.id)}
                  readOnly
                  style={{ marginRight: '0.75rem' }}
                />
                <label style={{ cursor: 'pointer', margin: 0 }}>{opcao.label}</label>
              </div>

              {/* Especificação com dropdown de áreas */}
              {mostrarEspecificacao[opcao.id] && opcao.requerAreaDecipex && areasDecipex.length > 0 && (
                <div style={{ marginTop: '0.5rem', marginLeft: '2rem' }}>
                  <select
                    value={areaDecipexSelecionada[opcao.id] || ''}
                    onChange={(e) => handleAreaDecipex(opcao.id, e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #ced4da',
                      borderRadius: '6px',
                      fontSize: '0.95rem'
                    }}
                  >
                    <option value="">Selecione uma área da DECIPEX...</option>
                    {areasDecipex.map(area => (
                      <option key={area.codigo} value={area.codigo}>
                        {area.sigla || area.codigo} - {area.nome}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Especificação com dropdown de órgãos */}
              {mostrarEspecificacao[opcao.id] && opcao.requerOrgaoCentralizado && orgaosCentralizados.length > 0 && (
                <div style={{ marginTop: '0.5rem', marginLeft: '2rem' }}>
                  <select
                    value={orgaoCentralizadoSelecionado[opcao.id] || ''}
                    onChange={(e) => handleOrgaoCentralizado(opcao.id, e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #ced4da',
                      borderRadius: '6px',
                      fontSize: '0.95rem'
                    }}
                  >
                    <option value="">Selecione um órgão...</option>
                    {orgaosCentralizados.map(orgao => (
                      <option key={orgao.sigla} value={orgao.sigla}>
                        {orgao.sigla} - {orgao.nome_completo}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Especificação com checkboxes de canais */}
              {mostrarEspecificacao[opcao.id] && opcao.requerCanaisAtendimento && canaisAtendimento.length > 0 && (
                <div style={{ marginTop: '0.5rem', marginLeft: '2rem', background: '#f8f9fa', padding: '1rem', borderRadius: '6px' }}>
                  <p style={{ fontSize: '0.85rem', color: '#495057', marginBottom: '0.5rem', fontWeight: 500 }}>
                    Selecione os canais de atendimento:
                  </p>
                  {canaisAtendimento.map(canal => (
                    <div key={canal.codigo} style={{ marginBottom: '0.3rem' }}>
                      <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                        <input
                          type="checkbox"
                          checked={(canaisSelecionados[opcao.id] || []).includes(canal.codigo)}
                          onChange={(e) => handleCanaisAtendimento(opcao.id, canal.codigo, e.target.checked)}
                          style={{ marginRight: '0.5rem' }}
                        />
                        <span style={{ fontSize: '0.9rem' }}>{canal.nome}</span>
                      </label>
                    </div>
                  ))}
                </div>
              )}

              {/* Especificação com dropdown de opções predefinidas */}
              {mostrarEspecificacao[opcao.id] && opcao.opcoesPredefinidas && (
                <div style={{ marginTop: '0.5rem', marginLeft: '2rem' }}>
                  <select
                    value={especificacoes[opcao.id] || ''}
                    onChange={(e) => handleEspecificacao(opcao.id, e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #ced4da',
                      borderRadius: '6px',
                      fontSize: '0.95rem'
                    }}
                  >
                    <option value="">Selecione...</option>
                    {opcao.opcoesPredefinidas.map(pred => (
                      <option key={pred} value={pred}>{pred}</option>
                    ))}
                  </select>
                </div>
              )}

              {/* Especificação com campo de texto livre (para casos obrigatórios) */}
              {mostrarEspecificacao[opcao.id] && opcao.obrigatorio && !opcao.requerAreaDecipex && !opcao.requerOrgaoCentralizado && !opcao.opcoesPredefinidas && (
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
          disabled={isLoading}
        >
          Não Sei
        </button>
        <button
          className="btn-interface btn-primary"
          onClick={handleConfirm}
          disabled={isLoading}
        >
          {isLoading ? 'Confirmando...' : 'Confirmar'}
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

        .btn-interface:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .btn-secondary {
          background: #6c757d;
          color: white;
        }

        .btn-secondary:hover:not(:disabled) {
          background: #5a6268;
        }

        .btn-primary {
          background: #007bff;
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
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
