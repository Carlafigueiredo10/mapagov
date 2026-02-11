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

interface OrigemEntrada {
  tipo: string;
  especificacao?: string | null;
  area_decipex?: string | null;
  orgao_centralizado?: string | null;
  canais_atendimento?: string[] | null;
}

interface InterfaceFluxosSaidaProps {
  dados?: {
    areas_organizacionais?: AreaOrganizacional[];
    orgaos_centralizados?: OrgaoCentralizado[];
    canais_atendimento?: CanalAtendimento[];
    fluxos_entrada_estruturados?: OrigemEntrada[];
  };
  onConfirm: (resposta: string) => void;
}

const InterfaceFluxosSaida: React.FC<InterfaceFluxosSaidaProps> = ({ dados, onConfirm }) => {
  const [destinos, setDestinos] = useState<DestinoSelecionado[]>([]);
  const [outrosDestinos, setOutrosDestinos] = useState('');
  const [mostrarEspecificacao, setMostrarEspecificacao] = useState<Record<string, boolean>>({});
  const [especificacoes, setEspecificacoes] = useState<Record<string, string>>({});
  const [areaDecipexSelecionada, setAreaDecipexSelecionada] = useState<Record<string, string[]>>({});
  const [orgaoCentralizadoSelecionado, setOrgaoCentralizadoSelecionado] = useState<Record<string, string>>({});
  const [canaisSelecionados, setCanaisSelecionados] = useState<Record<string, string[]>>({});
  const [isLoading, setIsLoading] = useState(false); // ✅ Proteção contra duplo clique

  // Usar dados do backend (do CSV) em vez de hardcoded
  const areasDecipex = dados?.areas_organizacionais || [];
  const orgaosCentralizados = dados?.orgaos_centralizados || [];
  const canaisAtendimento = dados?.canais_atendimento || [];
  const fluxosEntradaEstruturados = dados?.fluxos_entrada_estruturados || [];

  // Mapeamento: label da entrada → id da opção de saída
  const MAPA_ENTRADA_SAIDA: Record<string, string> = {
    'De outra área da DECIPEX': 'outra_area_decipex',
    'De algum órgão centralizado': 'orgao_centralizado',
    'De fora da DECIPEX (outro órgão/entidade)': 'fora_decipex',
    'Do usuário/requerente diretamente': 'usuario_requerente',
    'De outra área interna da sua Coordenação Geral': 'area_interna_cg',
    'Órgãos de Controle': 'orgaos_controle',
    'Demanda judicial': 'demanda_judicial',
  };

  const replicarEntrada = () => {
    const novosDestinos: DestinoSelecionado[] = [];
    const novasEspecs: Record<string, string> = {};
    const novasAreas: Record<string, string> = {};
    const novosOrgaos: Record<string, string> = {};
    const novosCanais: Record<string, string[]> = {};
    const novosMostrar: Record<string, boolean> = {};

    for (const origem of fluxosEntradaEstruturados) {
      const idSaida = MAPA_ENTRADA_SAIDA[origem.tipo];
      if (!idSaida) continue;

      novosDestinos.push({
        tipo: idSaida,
        especificacao: origem.especificacao || undefined,
        area_decipex: origem.area_decipex || undefined,
        orgao_centralizado: origem.orgao_centralizado || undefined,
        canais_atendimento: origem.canais_atendimento || undefined,
      });

      novosMostrar[idSaida] = true;

      if (origem.especificacao) {
        novasEspecs[idSaida] = origem.especificacao;
      }
      if (origem.area_decipex) {
        novasAreas[idSaida] = origem.area_decipex.split(';').filter(Boolean);
      }
      if (origem.orgao_centralizado) {
        novosOrgaos[idSaida] = origem.orgao_centralizado;
      }
      if (origem.canais_atendimento && origem.canais_atendimento.length > 0) {
        novosCanais[idSaida] = origem.canais_atendimento;
      }
    }

    setDestinos(novosDestinos);
    setMostrarEspecificacao(novosMostrar);
    setEspecificacoes(novasEspecs);
    setAreaDecipexSelecionada(novasAreas);
    setOrgaoCentralizadoSelecionado(novosOrgaos);
    setCanaisSelecionados(novosCanais);
  };

  const opcoesDestino: OpcaoDestino[] = [
    { id: 'outra_area_decipex', label: 'Para outra área da DECIPEX', requerEspecificacao: true, requerAreaDecipex: true },
    { id: 'orgao_centralizado', label: 'Para algum órgão centralizado', requerEspecificacao: true, requerOrgaoCentralizado: true },
    { id: 'fora_decipex', label: 'Para fora da DECIPEX (outro órgão/entidade)', requerEspecificacao: true, obrigatorio: true },
    { id: 'usuario_requerente', label: 'Para o usuário/requerente diretamente', requerEspecificacao: true, requerCanaisAtendimento: true },
    { id: 'area_interna_cg', label: 'Para outra área interna da sua Coordenação Geral', requerEspecificacao: true, obrigatorio: true },
    { id: 'orgaos_controle', label: 'Órgãos de Controle', requerEspecificacao: true, opcoesPredefinidas: ['TCU - Indícios', 'TCU - Acórdão', 'CGU'] },
    { id: 'demanda_judicial', label: 'Demanda judicial', requerEspecificacao: true, opcoesPredefinidas: ['AGU/PRU', 'Defensoria Pública', 'Direto das partes (ex: pensão alimentícia)'] },
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

  const handleToggleAreaDecipex = (id: string, codigoArea: string) => {
    setAreaDecipexSelecionada(prev => {
      const atuais = prev[id] || [];
      const jaExiste = atuais.includes(codigoArea);
      const novas = jaExiste ? atuais.filter(c => c !== codigoArea) : [...atuais, codigoArea];

      setDestinos(p => p.map(o =>
        o.tipo === id ? { ...o, area_decipex: novas.join(';') } : o
      ));

      return { ...prev, [id]: novas };
    });
  };

  const handleOrgaoCentralizado = (id: string, valor: string) => {
    setOrgaoCentralizadoSelecionado(prev => ({ ...prev, [id]: valor }));
    setDestinos(prev => prev.map(o =>
      o.tipo === id ? { ...o, orgao_centralizado: valor } : o
    ));
  };

  const handleToggleCanal = (idDestino: string, codigoCanal: string) => {
    setCanaisSelecionados(prev => {
      const canaisAtuais = prev[idDestino] || [];
      const jaExiste = canaisAtuais.includes(codigoCanal);

      const novosCanais = jaExiste
        ? canaisAtuais.filter(c => c !== codigoCanal)
        : [...canaisAtuais, codigoCanal];

      const nomesCanais = novosCanais.map(codigo => {
        const canal = canaisAtendimento.find(c => c.codigo === codigo);
        return canal ? canal.nome : codigo;
      });
      const especificacao = nomesCanais.join(', ');

      setEspecificacoes(prev => ({ ...prev, [idDestino]: especificacao }));
      setDestinos(prev => prev.map(o =>
        o.tipo === idDestino ? { ...o, canais_atendimento: novosCanais, especificacao } : o
      ));

      return { ...prev, [idDestino]: novosCanais };
    });
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

        {fluxosEntradaEstruturados.length > 0 && (
          <div style={{
            marginBottom: '1rem',
            padding: '0.75rem',
            background: '#e7f3ff',
            borderLeft: '4px solid #1351B4',
            borderRadius: '4px',
            fontSize: '0.85rem',
            color: '#004085',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '1rem'
          }}>
            <span>
              <strong>Sugestão:</strong> A saída costuma ser devolvida ao demandante.
              Deseja replicar os fluxos de entrada?
            </span>
            <button
              onClick={replicarEntrada}
              disabled={isLoading}
              style={{
                padding: '0.5rem 1rem',
                background: '#1351B4',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: 500,
                fontSize: '0.85rem',
                whiteSpace: 'nowrap'
              }}
            >
              Replicar fluxos de entrada
            </button>
          </div>
        )}

        <div style={{
          marginBottom: '1rem',
          padding: '0.75rem',
          background: '#fff3cd',
          borderLeft: '4px solid #ffc107',
          borderRadius: '4px',
          fontSize: '0.85rem',
          color: '#856404'
        }}>
          <strong>Atenção:</strong> Em se tratando de processo administrativo,
          considere sempre enviar à CGGAF para inclusão em assentamento funcional.
        </div>

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

              {/* Seletor de Áreas DECIPEX (múltipla seleção) */}
              {mostrarEspecificacao[opcao.id] && opcao.requerAreaDecipex && areasDecipex.length > 0 && (
                <div style={{ marginTop: '0.5rem', marginLeft: '2rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: '#495057', fontWeight: 500 }}>
                    Selecione as áreas da DECIPEX (pode selecionar várias):
                  </label>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                    gap: '0.5rem',
                    padding: '0.75rem',
                    border: '1px solid #ced4da',
                    borderRadius: '6px',
                    background: '#f8f9fa'
                  }}>
                    {areasDecipex.map(area => (
                      <div
                        key={area.codigo}
                        onClick={() => handleToggleAreaDecipex(opcao.id, area.codigo)}
                        style={{
                          padding: '0.5rem',
                          border: '2px solid',
                          borderColor: (areaDecipexSelecionada[opcao.id] || []).includes(area.codigo) ? '#1351B4' : '#dee2e6',
                          borderRadius: '6px',
                          background: (areaDecipexSelecionada[opcao.id] || []).includes(area.codigo) ? '#e7f3ff' : 'white',
                          cursor: 'pointer',
                          transition: 'all 0.2s',
                          fontSize: '0.85rem'
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={(areaDecipexSelecionada[opcao.id] || []).includes(area.codigo)}
                          readOnly
                          style={{ marginRight: '0.5rem', cursor: 'pointer' }}
                        />
                        <strong>{area.sigla || area.codigo}</strong> - {area.nome}
                      </div>
                    ))}
                  </div>
                  {(areaDecipexSelecionada[opcao.id] || []).length > 0 && (
                    <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#28a745', fontWeight: 500 }}>
                      ✓ {areaDecipexSelecionada[opcao.id].length} área(s) selecionada(s)
                    </div>
                  )}
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

              {/* Seletor de Canais de Atendimento (múltipla seleção) */}
              {mostrarEspecificacao[opcao.id] && opcao.requerCanaisAtendimento && canaisAtendimento.length > 0 && (
                <div style={{ marginTop: '0.5rem', marginLeft: '2rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: '#495057', fontWeight: 500 }}>
                    Selecione os canais de atendimento (pode selecionar vários):
                  </label>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
                    gap: '0.5rem',
                    padding: '0.75rem',
                    border: '1px solid #ced4da',
                    borderRadius: '6px',
                    background: '#f8f9fa'
                  }}>
                    {canaisAtendimento.map(canal => (
                      <div
                        key={canal.codigo}
                        onClick={() => handleToggleCanal(opcao.id, canal.codigo)}
                        style={{
                          padding: '0.5rem',
                          border: '2px solid',
                          borderColor: (canaisSelecionados[opcao.id] || []).includes(canal.codigo) ? '#1351B4' : '#dee2e6',
                          borderRadius: '6px',
                          background: (canaisSelecionados[opcao.id] || []).includes(canal.codigo) ? '#e7f3ff' : 'white',
                          cursor: 'pointer',
                          transition: 'all 0.2s',
                          fontSize: '0.85rem'
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={(canaisSelecionados[opcao.id] || []).includes(canal.codigo)}
                          readOnly
                          style={{ marginRight: '0.5rem', cursor: 'pointer' }}
                        />
                        <strong>{canal.nome}</strong>
                        {canal.descricao && (
                          <div style={{ fontSize: '0.75rem', color: '#6c757d', marginTop: '0.25rem', marginLeft: '1.5rem' }}>
                            {canal.descricao}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                  {(canaisSelecionados[opcao.id] || []).length > 0 && (
                    <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#28a745', fontWeight: 500 }}>
                      ✓ {canaisSelecionados[opcao.id].length} canal(is) selecionado(s)
                    </div>
                  )}
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
