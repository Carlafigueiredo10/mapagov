import React, { useState } from 'react';

interface OrigemSelecionada {
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

interface OpcaoOrigem {
  id: string;
  label: string;
  requerEspecificacao: boolean;
  requerAreaDecipex?: boolean;
  requerOrgaoCentralizado?: boolean;
  requerCanaisAtendimento?: boolean;
  obrigatorio?: boolean;
  opcoesPredefinidas?: string[];
}

interface InterfaceFluxosEntradaProps {
  dados?: {
    areas_organizacionais?: AreaOrganizacional[];
    orgaos_centralizados?: OrgaoCentralizado[];
    canais_atendimento?: CanalAtendimento[];
  };
  onConfirm: (resposta: string) => void;
}

const InterfaceFluxosEntrada: React.FC<InterfaceFluxosEntradaProps> = ({ dados, onConfirm }) => {
  const [origens, setOrigens] = useState<OrigemSelecionada[]>([]);
  const [outrasOrigens, setOutrasOrigens] = useState('');
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

  const opcoesOrigem: OpcaoOrigem[] = [
    { id: 'outra_area_decipex', label: 'De outra área da DECIPEX', requerEspecificacao: true, requerAreaDecipex: true },
    { id: 'orgao_centralizado', label: 'De algum órgão centralizado', requerEspecificacao: true, requerOrgaoCentralizado: true },
    { id: 'fora_decipex', label: 'De fora da DECIPEX (outro órgão/entidade)', requerEspecificacao: true, obrigatorio: true },
    { id: 'usuario_requerente', label: 'Do usuário/requerente diretamente', requerEspecificacao: true, requerCanaisAtendimento: true },
    { id: 'area_interna_cg', label: 'De outra área interna da sua Coordenação Geral', requerEspecificacao: true, obrigatorio: true },
    { id: 'orgaos_controle', label: 'Órgãos de Controle', requerEspecificacao: true, opcoesPredefinidas: ['TCU - Indícios', 'TCU - Acórdão', 'CGU'] },
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

  const handleAreaDecipex = (id: string, codigoArea: string) => {
    setAreaDecipexSelecionada(prev => ({ ...prev, [id]: codigoArea }));
    const areaInfo = areasDecipex.find(a => a.codigo === codigoArea);
    const especificacao = areaInfo ? `${areaInfo.codigo} - ${areaInfo.nome}` : codigoArea;

    setEspecificacoes(prev => ({ ...prev, [id]: especificacao }));
    setOrigens(prev => prev.map(o =>
      o.tipo === id ? { ...o, area_decipex: codigoArea, especificacao } : o
    ));
  };

  const handleOrgaoCentralizado = (id: string, siglaOrgao: string) => {
    setOrgaoCentralizadoSelecionado(prev => ({ ...prev, [id]: siglaOrgao }));
    const orgaoInfo = orgaosCentralizados.find(o => o.sigla === siglaOrgao);
    const especificacao = orgaoInfo ? `${orgaoInfo.sigla} - ${orgaoInfo.nome_completo}` : siglaOrgao;

    setEspecificacoes(prev => ({ ...prev, [id]: especificacao }));
    setOrigens(prev => prev.map(o =>
      o.tipo === id ? { ...o, orgao_centralizado: siglaOrgao, especificacao } : o
    ));
  };

  const handleToggleCanal = (idOrigem: string, codigoCanal: string) => {
    setCanaisSelecionados(prev => {
      const canaisAtuais = prev[idOrigem] || [];
      const jaExiste = canaisAtuais.includes(codigoCanal);

      const novosCanais = jaExiste
        ? canaisAtuais.filter(c => c !== codigoCanal)
        : [...canaisAtuais, codigoCanal];

      // Atualizar especificação com nomes dos canais
      const nomesCanais = novosCanais.map(codigo => {
        const canal = canaisAtendimento.find(c => c.codigo === codigo);
        return canal ? canal.nome : codigo;
      });
      const especificacao = nomesCanais.join(', ');

      setEspecificacoes(prev => ({ ...prev, [idOrigem]: especificacao }));
      setOrigens(prev => prev.map(o =>
        o.tipo === idOrigem ? { ...o, canais_atendimento: novosCanais, especificacao } : o
      ));

      return { ...prev, [idOrigem]: novosCanais };
    });
  };

  const handleConfirm = () => {
    // ✅ Proteção contra duplo clique
    if (isLoading) return;
    setIsLoading(true);

    try {
      if (origens.length === 0 && !outrasOrigens.trim()) {
        alert('Por favor, selecione ao menos uma origem ou descreva manualmente.');
        setIsLoading(false);
        return;
      }

      // Validar especificações obrigatórias
      for (const origem of origens) {
        const opcao = opcoesOrigem.find(o => o.id === origem.tipo);
        if (opcao?.obrigatorio && !especificacoes[origem.tipo]?.trim()) {
          alert(`Por favor, especifique: ${opcao.label}`);
          setIsLoading(false);
          return;
        }
        if (opcao?.requerAreaDecipex && !areaDecipexSelecionada[origem.tipo]) {
          alert(`Por favor, selecione a área da DECIPEX de origem.`);
          setIsLoading(false);
          return;
        }
        if (opcao?.requerOrgaoCentralizado && !orgaoCentralizadoSelecionado[origem.tipo]) {
          alert(`Por favor, selecione o órgão centralizado de origem.`);
          setIsLoading(false);
          return;
        }
        if (opcao?.requerCanaisAtendimento && (!canaisSelecionados[origem.tipo] || canaisSelecionados[origem.tipo].length === 0)) {
          alert(`Por favor, selecione ao menos um canal de atendimento.`);
          setIsLoading(false);
          return;
        }
      }

      // Montar resposta estruturada
      const respostaObj: any = {
        origens_selecionadas: origens.map(o => ({
          tipo: opcoesOrigem.find(op => op.id === o.tipo)?.label || o.tipo,
          especificacao: o.especificacao || null,
          area_decipex: o.area_decipex || null,
          orgao_centralizado: o.orgao_centralizado || null,
          canais_atendimento: o.canais_atendimento || null
        })),
        outras_origens: outrasOrigens.trim() || null
      };

      // Enviar como JSON string
      onConfirm(JSON.stringify(respostaObj));
      // Nota: não resetar isLoading aqui, pois o componente será desmontado
    } catch (error) {
      console.error('Erro ao confirmar:', error);
      setIsLoading(false);
    }
  };

  const handleSkip = () => {
    if (isLoading) return;
    setIsLoading(true);
    onConfirm('nao_sei');
  };

  return (
    <div className="interface-container fade-in">
      <div className="interface-title">📥 Entrada do Processo</div>

      <div className="interface-content">
        <div style={{ marginBottom: '1.5rem' }}>
          <p style={{ fontSize: '0.95rem', color: '#495057', marginBottom: '1rem', fontWeight: 500 }}>
            Selecione todas as origens que se aplicam:
          </p>

          {opcoesOrigem.map((opcao, index) => (
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
                <label style={{ cursor: 'pointer', margin: 0 }}>
                  <strong>{index + 1}.</strong> {opcao.label}
                </label>
              </div>

              {/* Seletor de Área DECIPEX */}
              {mostrarEspecificacao[opcao.id] && opcao.requerAreaDecipex && (
                <div style={{ marginTop: '0.5rem', marginLeft: '2rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: '#495057' }}>
                    Selecione a área da DECIPEX:
                  </label>
                  <select
                    value={areaDecipexSelecionada[opcao.id] || ''}
                    onChange={(e) => handleAreaDecipex(opcao.id, e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #ced4da',
                      borderRadius: '6px',
                      fontSize: '0.95rem',
                      background: 'white'
                    }}
                  >
                    <option value="">Selecione uma área...</option>
                    {areasDecipex.map(area => (
                      <option key={area.codigo} value={area.codigo}>
                        {area.codigo} - {area.nome}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Seletor de Órgão Centralizado */}
              {mostrarEspecificacao[opcao.id] && opcao.requerOrgaoCentralizado && (
                <div style={{ marginTop: '0.5rem', marginLeft: '2rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: '#495057' }}>
                    Selecione o órgão centralizado:
                  </label>
                  <select
                    value={orgaoCentralizadoSelecionado[opcao.id] || ''}
                    onChange={(e) => handleOrgaoCentralizado(opcao.id, e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #ced4da',
                      borderRadius: '6px',
                      fontSize: '0.95rem',
                      background: 'white'
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
              {mostrarEspecificacao[opcao.id] && opcao.requerCanaisAtendimento && (
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

              {/* Opções predefinidas (TCU, CGU) */}
              {mostrarEspecificacao[opcao.id] && opcao.opcoesPredefinidas && (
                <div style={{ marginTop: '0.5rem', marginLeft: '2rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: '#495057' }}>
                    Selecione o órgão de controle:
                  </label>
                  <select
                    value={especificacoes[opcao.id] || ''}
                    onChange={(e) => handleEspecificacao(opcao.id, e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #ced4da',
                      borderRadius: '6px',
                      fontSize: '0.95rem',
                      background: 'white'
                    }}
                  >
                    <option value="">Selecione uma opção...</option>
                    {opcao.opcoesPredefinidas.map(opt => (
                      <option key={opt} value={opt}>{opt}</option>
                    ))}
                  </select>
                </div>
              )}

              {/* Campo de texto para especificação (obrigatório ou opcional) */}
              {mostrarEspecificacao[opcao.id] && !opcao.requerAreaDecipex && !opcao.opcoesPredefinidas && (
                <div style={{ marginTop: '0.5rem', marginLeft: '2rem' }}>
                  <input
                    type="text"
                    placeholder={opcao.obrigatorio ? "Especifique (obrigatório)..." : "Especifique qual área/órgão..."}
                    value={especificacoes[opcao.id] || ''}
                    onChange={(e) => handleEspecificacao(opcao.id, e.target.value)}
                    required={opcao.obrigatorio}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: `1px solid ${opcao.obrigatorio ? '#dc3545' : '#ced4da'}`,
                      borderRadius: '6px',
                      fontSize: '0.95rem',
                      background: opcao.obrigatorio ? '#fff5f5' : 'white'
                    }}
                  />
                  {opcao.obrigatorio && (
                    <small style={{ color: '#dc3545', fontSize: '0.8rem', marginTop: '0.25rem', display: 'block' }}>
                      * Campo obrigatório
                    </small>
                  )}
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
            placeholder="Ex: Recebo processos vindos de outras fontes não listadas acima..."
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
          disabled={isLoading}
        >
          Não Sei
        </button>
        <button
          className="btn-interface btn-primary"
          onClick={handleConfirm}
          disabled={isLoading}
        >
          {isLoading ? 'Processando...' : 'Confirmar'}
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
