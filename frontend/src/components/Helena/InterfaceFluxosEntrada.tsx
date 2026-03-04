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
  const [origensDigitadas, setOrigensDigitadas] = useState<string[]>([]);
  const [origemManual, setOrigemManual] = useState('');
  const [mostrarEspecificacao, setMostrarEspecificacao] = useState<Record<string, boolean>>({});
  const [especificacoes, setEspecificacoes] = useState<Record<string, string>>({});
  const [areaDecipexSelecionada, setAreaDecipexSelecionada] = useState<Record<string, string[]>>({});
  const [orgaoCentralizadoSelecionado, setOrgaoCentralizadoSelecionado] = useState<Record<string, string[]>>({});
  const [canaisSelecionados, setCanaisSelecionados] = useState<Record<string, string[]>>({});
  const [isLoading, setIsLoading] = useState(false); // ✅ Proteção contra duplo clique

  // Usar dados do backend (do CSV) em vez de hardcoded
  const areasDecipex = dados?.areas_organizacionais || [];
  const orgaosCentralizados = dados?.orgaos_centralizados || [];
  const canaisAtendimento = dados?.canais_atendimento || [];

  const opcoesOrigem: OpcaoOrigem[] = [
    { id: 'outra_area_decipex', label: 'De outra área da DECIPEX', requerEspecificacao: true, requerAreaDecipex: true },
    { id: 'orgao_centralizado', label: 'De algum órgão centralizado', requerEspecificacao: true, requerOrgaoCentralizado: true },
    { id: 'usuario_requerente', label: 'Do usuário/requerente diretamente', requerEspecificacao: true, requerCanaisAtendimento: true },
    { id: 'area_interna_cg', label: 'De outra área interna da sua Coordenação Geral', requerEspecificacao: true, obrigatorio: true },
    { id: 'orgaos_controle', label: 'Órgãos de Controle', requerEspecificacao: true, opcoesPredefinidas: ['TCU - Indícios', 'TCU - Acórdão', 'CGU'] },
    { id: 'demanda_judicial', label: 'Demanda judicial', requerEspecificacao: true, opcoesPredefinidas: ['AGU/PRU', 'PGFN', 'Defensoria Pública', 'Direto das partes (ex: pensão alimentícia)'] },
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

  const handleToggleAreaDecipex = (id: string, codigoArea: string) => {
    setAreaDecipexSelecionada(prev => {
      const atuais = prev[id] || [];
      const jaExiste = atuais.includes(codigoArea);
      const novas = jaExiste ? atuais.filter(c => c !== codigoArea) : [...atuais, codigoArea];

      // Atualizar especificação com todos os selecionados
      const especificacao = novas.map(cod => {
        const info = areasDecipex.find(a => a.codigo === cod);
        return info ? `${info.codigo} - ${info.nome}` : cod;
      }).join('; ');

      setEspecificacoes(p => ({ ...p, [id]: especificacao }));
      setOrigens(p => p.map(o =>
        o.tipo === id ? { ...o, area_decipex: novas.join(';'), especificacao } : o
      ));

      return { ...prev, [id]: novas };
    });
  };

  const handleToggleOrgaoCentralizado = (id: string, siglaOrgao: string) => {
    setOrgaoCentralizadoSelecionado(prev => {
      const atuais = prev[id] || [];
      const jaExiste = atuais.includes(siglaOrgao);
      const novos = jaExiste ? atuais.filter(s => s !== siglaOrgao) : [...atuais, siglaOrgao];

      const especificacao = novos.map(sigla => {
        const info = orgaosCentralizados.find(o => o.sigla === sigla);
        return info ? `${info.sigla} - ${info.nome_completo}` : sigla;
      }).join('; ');

      setEspecificacoes(p => ({ ...p, [id]: especificacao }));
      setOrigens(p => p.map(o =>
        o.tipo === id ? { ...o, orgao_centralizado: novos.join(';'), especificacao } : o
      ));

      return { ...prev, [id]: novos };
    });
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

  const adicionarOrigemManual = () => {
    const origem = origemManual.trim();
    if (origem && !origensDigitadas.includes(origem)) {
      setOrigensDigitadas([...origensDigitadas, origem]);
      setOrigemManual('');
    }
  };

  const removerOrigemDigitada = (origem: string) => {
    setOrigensDigitadas(origensDigitadas.filter(o => o !== origem));
  };

  const handleKeyPressManual = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      adicionarOrigemManual();
    }
  };

  const handleConfirm = () => {
    // ✅ Proteção contra duplo clique
    if (isLoading) return;
    setIsLoading(true);

    try {
      if (origens.length === 0 && origensDigitadas.length === 0) {
        alert('Por favor, selecione ao menos uma origem ou adicione manualmente.');
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
        if (opcao?.requerAreaDecipex && (!areaDecipexSelecionada[origem.tipo] || areaDecipexSelecionada[origem.tipo].length === 0)) {
          alert(`Por favor, selecione a área da DECIPEX de origem.`);
          setIsLoading(false);
          return;
        }
        if (opcao?.requerOrgaoCentralizado && (!orgaoCentralizadoSelecionado[origem.tipo] || orgaoCentralizadoSelecionado[origem.tipo].length === 0)) {
          alert(`Por favor, selecione ao menos um órgão centralizado de origem.`);
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
        outras_origens: origensDigitadas.length > 0 ? origensDigitadas.join('; ') : null,
        outras_origens_lista: origensDigitadas.length > 0 ? origensDigitadas : null
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

              {/* Seletor de Áreas DECIPEX (múltipla seleção) */}
              {mostrarEspecificacao[opcao.id] && opcao.requerAreaDecipex && (
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
                        <strong>{area.codigo}</strong> - {area.nome}
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

              {/* Seletor de Órgãos Centralizados (múltipla seleção) */}
              {mostrarEspecificacao[opcao.id] && opcao.requerOrgaoCentralizado && (
                <div style={{ marginTop: '0.5rem', marginLeft: '2rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: '#495057', fontWeight: 500 }}>
                    Selecione os órgãos centralizados (pode selecionar vários):
                  </label>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
                    gap: '0.5rem',
                  }}>
                    {orgaosCentralizados.map(orgao => (
                      <div
                        key={orgao.sigla}
                        onClick={() => handleToggleOrgaoCentralizado(opcao.id, orgao.sigla)}
                        style={{
                          padding: '0.6rem 0.8rem',
                          border: '1px solid',
                          borderColor: (orgaoCentralizadoSelecionado[opcao.id] || []).includes(orgao.sigla) ? '#1351B4' : '#dee2e6',
                          borderRadius: '6px',
                          background: (orgaoCentralizadoSelecionado[opcao.id] || []).includes(orgao.sigla) ? '#e7f3ff' : 'white',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'flex-start',
                          gap: '0.5rem',
                          transition: 'all 0.15s',
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={(orgaoCentralizadoSelecionado[opcao.id] || []).includes(orgao.sigla)}
                          readOnly
                          style={{ marginTop: '3px', accentColor: '#1351B4' }}
                        />
                        <div>
                          <strong>{orgao.sigla}</strong>
                          <span style={{ fontSize: '0.85rem', color: '#6c757d', marginLeft: '0.3rem' }}>
                            {orgao.nome_completo}
                          </span>
                          {orgao.observacao && (
                            <div style={{ fontSize: '0.8rem', color: '#999', marginTop: '2px' }}>
                              {orgao.observacao}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                  {(orgaoCentralizadoSelecionado[opcao.id] || []).length > 0 && (
                    <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#28a745', fontWeight: 500 }}>
                      ✓ {orgaoCentralizadoSelecionado[opcao.id].length} órgão(s) selecionado(s)
                    </div>
                  )}
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
              {mostrarEspecificacao[opcao.id] && !opcao.requerAreaDecipex && !opcao.opcoesPredefinidas && !opcao.requerOrgaoCentralizado && (
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

        {/* Origens adicionadas manualmente (chips) */}
        {origensDigitadas.length > 0 && (
          <div style={{
            margin: '1rem 0',
            padding: '1rem',
            background: '#e8f5e9',
            borderRadius: '8px',
            border: '2px solid #4caf50'
          }}>
            <div style={{ marginBottom: '0.75rem', fontSize: '0.875rem', color: '#2e7d32', fontWeight: 600 }}>
              📝 Origens adicionadas manualmente:
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {origensDigitadas.map((origem, idx) => (
                <div key={idx} style={{
                  display: 'flex', alignItems: 'center', gap: '0.5rem',
                  padding: '0.5rem 0.75rem', background: 'white',
                  border: '2px solid #4caf50', borderRadius: '20px',
                  fontSize: '0.875rem', fontWeight: 500, color: '#2e7d32'
                }}>
                  <span>{origem}</span>
                  <button
                    onClick={() => removerOrigemDigitada(origem)}
                    title="Remover"
                    type="button"
                    style={{
                      width: '20px', height: '20px', padding: 0,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      background: '#f44336', color: 'white', border: 'none',
                      borderRadius: '50%', cursor: 'pointer', fontSize: '12px', lineHeight: 1
                    }}
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Campo de entrada manual */}
        <div style={{
          margin: '1.5rem 0',
          padding: '1.25rem',
          background: '#fff9e6',
          borderRadius: '8px',
          border: '2px dashed #ffc107'
        }}>
          <div style={{ marginBottom: '0.75rem', fontSize: '0.875rem', color: '#856404', fontWeight: 500 }}>
            Outra origem? ✍️ Digite manualmente abaixo.
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="text"
              placeholder="Ex: Recebo processos vindos de outras fontes não listadas acima..."
              value={origemManual}
              onChange={(e) => setOrigemManual(e.target.value)}
              onKeyPress={handleKeyPressManual}
              style={{
                flex: 1, padding: '0.625rem 0.875rem',
                border: '2px solid #ddd', borderRadius: '6px',
                fontSize: '0.875rem'
              }}
            />
            <button
              onClick={adicionarOrigemManual}
              disabled={!origemManual.trim()}
              type="button"
              style={{
                padding: '0.625rem 1.25rem',
                background: origemManual.trim() ? '#28a745' : '#6c757d',
                color: 'white', border: 'none', borderRadius: '6px',
                cursor: origemManual.trim() ? 'pointer' : 'not-allowed',
                fontSize: '0.875rem', fontWeight: 500, whiteSpace: 'nowrap',
                opacity: origemManual.trim() ? 1 : 0.5
              }}
            >
              + Adicionar
            </button>
          </div>
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
