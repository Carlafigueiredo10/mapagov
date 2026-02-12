import React, { useState } from 'react';
import { Edit2, Trash2, Plus, ChevronDown, ChevronRight, AlertCircle, ArrowUp, ArrowDown, PlusCircle } from 'lucide-react';
import type { Etapa, Cenario } from '../../types/pop.types';

interface InterfaceEditarEtapasProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

const InterfaceEditarEtapas: React.FC<InterfaceEditarEtapasProps> = ({ dados, onConfirm }) => {
  const etapasOriginais = (dados?.etapas as Etapa[]) || [];
  const [etapas, setEtapas] = useState<Etapa[]>([...etapasOriginais]);
  const [expandidas, setExpandidas] = useState<Record<string, boolean>>({});

  const getEtapaKey = (etapa: Etapa) => etapa.id || String(etapa.numero);
  const getEtapaLabel = (etapa: Etapa) => etapa.acao_principal || etapa.descricao || '[Sem descricao]';

  const toggleExpansao = (key: string) => {
    setExpandidas(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleDeletar = (etapa: Etapa) => {
    const label = getEtapaLabel(etapa);
    const confirmacao = confirm(`Tem certeza que deseja deletar a Etapa ${etapa.numero}?\n\n"${label}"\n\nEsta acao nao pode ser desfeita.`);
    if (!confirmacao) return;

    const novasEtapas = etapas
      .filter(e => getEtapaKey(e) !== getEtapaKey(etapa))
      .map((e, idx) => ({ ...e, numero: String(idx + 1), ordem: idx + 1 }));
    setEtapas(novasEtapas);
  };

  const handleEditar = (etapa: Etapa) => {
    onConfirm(JSON.stringify({
      acao: 'editar_etapa',
      etapa_id: etapa.id,
      numero_etapa: Number(etapa.numero)
    }));
  };

  const handleMoverCima = (etapa: Etapa) => {
    const idx = etapas.findIndex(e => getEtapaKey(e) === getEtapaKey(etapa));
    if (idx <= 0) return;
    const novas = [...etapas];
    [novas[idx - 1], novas[idx]] = [novas[idx], novas[idx - 1]];
    setEtapas(novas.map((e, i) => ({ ...e, numero: String(i + 1), ordem: i + 1 })));
  };

  const handleMoverBaixo = (etapa: Etapa) => {
    const idx = etapas.findIndex(e => getEtapaKey(e) === getEtapaKey(etapa));
    if (idx < 0 || idx >= etapas.length - 1) return;
    const novas = [...etapas];
    [novas[idx], novas[idx + 1]] = [novas[idx + 1], novas[idx]];
    setEtapas(novas.map((e, i) => ({ ...e, numero: String(i + 1), ordem: i + 1 })));
  };

  const handleInserirAntes = (etapa: Etapa) => {
    const numero = Number(etapa.numero);
    onConfirm(JSON.stringify({
      acao: 'inserir_etapa',
      posicao: numero - 1
    }));
  };

  const handleInserirDepois = (etapa: Etapa) => {
    const numero = Number(etapa.numero);
    onConfirm(JSON.stringify({
      acao: 'inserir_etapa',
      posicao: numero
    }));
  };

  const handleAdicionarNova = () => {
    onConfirm(JSON.stringify({
      acao: 'adicionar_etapa',
      numero_etapa: etapas.length + 1
    }));
  };

  const handleSalvar = () => {
    if (etapas.length === 0) {
      alert('Voce precisa ter pelo menos uma etapa no processo.');
      return;
    }
    onConfirm(JSON.stringify({ acao: 'salvar_etapas', etapas }));
  };

  const handleCancelar = () => {
    onConfirm('cancelar');
  };

  const renderVerificacoes = (etapa: Etapa) => {
    const items = etapa.verificacoes || etapa.detalhes || [];
    if (items.length === 0) return null;
    return (
      <div className="detalhe-section">
        <div className="detalhe-label">Verificacoes:</div>
        <ul className="detalhe-lista">
          {items.slice(0, 4).map((v, i) => <li key={i}>{v}</li>)}
          {items.length > 4 && <li className="detalhe-mais">... e mais {items.length - 4}</li>}
        </ul>
      </div>
    );
  };

  const renderCenarios = (cenarios?: Cenario[], tipoCondicional?: string) => {
    if (!cenarios || cenarios.length === 0) return null;
    return (
      <div className="cenarios-preview">
        <div className="cenarios-header">
          <AlertCircle size={16} className="cenarios-icone" />
          <span className="cenarios-titulo">
            Condicional {tipoCondicional ? `(${tipoCondicional})` : ''} - {cenarios.length} cenario(s):
          </span>
        </div>
        <div className="cenarios-lista">
          {cenarios.slice(0, 3).map((cen, idx) => (
            <div key={idx} className="cenario-item">
              <span className="cenario-bullet">{cen.numero || '•'}</span>
              <span className="cenario-texto">{cen.descricao}</span>
              {cen.subetapas?.length > 0 && (
                <span className="cenario-sub-count">({cen.subetapas.length} sub)</span>
              )}
            </div>
          ))}
          {cenarios.length > 3 && (
            <div className="cenario-item cenario-mais">
              <span>... e mais {cenarios.length - 3} cenario(s)</span>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderMetadados = (etapa: Etapa) => {
    const campos: { label: string; valor: string }[] = [];
    if (etapa.operador_nome) campos.push({ label: 'Operador', valor: etapa.operador_nome });
    if (etapa.tempo_estimado) campos.push({ label: 'Tempo', valor: etapa.tempo_estimado });
    if (etapa.sistemas?.length) campos.push({ label: 'Sistemas', valor: etapa.sistemas.join(', ') });
    if (etapa.docs_requeridos?.length) campos.push({ label: 'Docs requeridos', valor: etapa.docs_requeridos.join(', ') });
    if (etapa.docs_gerados?.length) campos.push({ label: 'Docs gerados', valor: etapa.docs_gerados.join(', ') });
    if (campos.length === 0) return null;
    return (
      <div className="metadados-grid">
        {campos.map((c, i) => (
          <div key={i} className="metadado-item">
            <span className="metadado-label">{c.label}:</span>
            <span className="metadado-valor">{c.valor}</span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="interface-editar-etapas fade-in">
      <div className="etapas-header">
        <div className="etapas-title">
          <Edit2 size={24} className="icon-edit" />
          <h2>Editar Etapas do Processo</h2>
        </div>
        <p className="etapas-subtitle">
          {etapas.length} {etapas.length === 1 ? 'etapa mapeada' : 'etapas mapeadas'}.
          Voce pode adicionar, editar ou remover etapas.
        </p>
      </div>

      {etapas.length === 0 ? (
        <div className="etapas-vazias">
          <AlertCircle size={48} className="icon-alerta" />
          <p className="texto-vazio">Nenhuma etapa no processo ainda.</p>
          <button onClick={handleAdicionarNova} className="btn-adicionar-primeira">
            <Plus size={20} /> Adicionar Primeira Etapa
          </button>
        </div>
      ) : (
        <div className="etapas-lista">
          {etapas.map((etapa) => {
            const key = getEtapaKey(etapa);
            const estaExpandida = expandidas[key];
            const isCondicional = etapa.tipo === 'condicional';
            const label = getEtapaLabel(etapa);

            return (
              <div key={key} className="etapa-card">
                <div className="etapa-header-card">
                  <div className="etapa-info-principal">
                    <button
                      onClick={() => toggleExpansao(key)}
                      className="btn-expandir"
                      aria-label={estaExpandida ? 'Recolher' : 'Expandir'}
                    >
                      {estaExpandida ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                    </button>
                    <div className="etapa-numero-badge">
                      Etapa {etapa.numero}
                    </div>
                    <div className="etapa-descricao-principal">
                      <span className="etapa-descricao-texto">{label}</span>
                      {isCondicional && (
                        <span className="badge-condicional" title="Etapa com decisoes condicionais">
                          <AlertCircle size={14} /> Condicional
                        </span>
                      )}
                      {etapa.operador_nome && (
                        <span className="badge-operador" title="Operador responsavel">
                          {etapa.operador_nome}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="etapa-acoes">
                    <div className="acoes-mover">
                      <button
                        onClick={() => handleMoverCima(etapa)}
                        className="btn-mover"
                        title="Mover para cima"
                        disabled={Number(etapa.numero) === 1}
                      >
                        <ArrowUp size={16} />
                      </button>
                      <button
                        onClick={() => handleMoverBaixo(etapa)}
                        className="btn-mover"
                        title="Mover para baixo"
                        disabled={Number(etapa.numero) === etapas.length}
                      >
                        <ArrowDown size={16} />
                      </button>
                    </div>
                    <button onClick={() => handleEditar(etapa)} className="btn-acao btn-editar" title="Editar esta etapa">
                      <Edit2 size={16} /> Editar
                    </button>
                    <button onClick={() => handleDeletar(etapa)} className="btn-acao btn-deletar" title="Deletar esta etapa">
                      <Trash2 size={16} /> Deletar
                    </button>
                    <div className="acoes-inserir">
                      <button onClick={() => handleInserirAntes(etapa)} className="btn-inserir" title="Inserir etapa antes">
                        <PlusCircle size={14} /> Incluir uma etapa antes
                      </button>
                      <button onClick={() => handleInserirDepois(etapa)} className="btn-inserir" title="Inserir etapa depois">
                        <PlusCircle size={14} /> Incluir uma etapa depois
                      </button>
                    </div>
                  </div>
                </div>

                {estaExpandida && (
                  <div className="etapa-detalhes">
                    {renderMetadados(etapa)}
                    {renderVerificacoes(etapa)}
                    {isCondicional && renderCenarios(etapa.cenarios, etapa.tipo_condicional)}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {etapas.length > 0 && (
        <div className="adicionar-nova-section">
          <button onClick={handleAdicionarNova} className="btn-adicionar-nova">
            <Plus size={20} /> Adicionar Nova Etapa
          </button>
        </div>
      )}

      <div className="etapas-footer">
        <button onClick={handleCancelar} className="btn-etapas btn-cancelar">Cancelar</button>
        <button onClick={handleSalvar} className="btn-etapas btn-salvar" disabled={etapas.length === 0}>
          <Edit2 size={18} /> Salvar Alteracoes
        </button>
      </div>

      <style>{`
        .interface-editar-etapas { background: white; border-radius: 12px; padding: 1.5rem; max-height: 70vh; overflow-y: auto; }
        .etapas-header { margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid #e9ecef; }
        .etapas-title { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; }
        .etapas-title h2 { margin: 0; font-size: 1.5rem; color: #212529; }
        .icon-edit { color: #1351B4; }
        .etapas-subtitle { margin: 0; color: #6c757d; font-size: 0.95rem; }
        .etapas-vazias { display: flex; flex-direction: column; align-items: center; padding: 3rem 1rem; background: #f8f9fa; border-radius: 8px; border: 2px dashed #dee2e6; }
        .icon-alerta { color: #ffc107; margin-bottom: 1rem; }
        .texto-vazio { color: #6c757d; font-size: 1.1rem; margin-bottom: 1.5rem; }
        .btn-adicionar-primeira { display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem; background: #1351B4; color: white; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
        .btn-adicionar-primeira:hover { background: #0c3d8a; transform: translateY(-1px); }
        .etapas-lista { display: flex; flex-direction: column; gap: 0.75rem; margin-bottom: 1.5rem; }
        .etapa-card { background: #f8f9fa; border: 2px solid #dee2e6; border-radius: 8px; overflow: hidden; transition: all 0.2s; }
        .etapa-card:hover { border-color: #adb5bd; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .etapa-header-card { display: flex; align-items: center; justify-content: space-between; padding: 1rem; gap: 1rem; }
        .etapa-info-principal { display: flex; align-items: center; gap: 0.75rem; flex: 1; min-width: 0; }
        .btn-expandir { background: none; border: none; padding: 0.25rem; cursor: pointer; color: #6c757d; display: flex; align-items: center; transition: all 0.2s; flex-shrink: 0; }
        .btn-expandir:hover { color: #212529; transform: scale(1.1); }
        .etapa-numero-badge { background: #1351B4; color: white; padding: 0.375rem 0.75rem; border-radius: 6px; font-weight: 600; font-size: 0.85rem; flex-shrink: 0; }
        .etapa-descricao-principal { display: flex; align-items: center; gap: 0.5rem; flex: 1; min-width: 0; flex-wrap: wrap; }
        .etapa-descricao-texto { font-size: 0.95rem; color: #212529; font-weight: 500; word-break: break-word; }
        .badge-condicional, .badge-operador { display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.72rem; font-weight: 600; white-space: nowrap; }
        .badge-condicional { background: #fff3cd; color: #856404; border: 1px solid #ffc107; }
        .badge-operador { background: #e8f0fe; color: #1351B4; border: 1px solid #b8d4fe; }
        .etapa-acoes { display: flex; gap: 0.4rem; flex-shrink: 0; align-items: center; flex-wrap: wrap; }
        .acoes-mover { display: flex; flex-direction: column; gap: 0.15rem; }
        .btn-mover { background: #e9ecef; border: none; border-radius: 4px; padding: 0.2rem; cursor: pointer; color: #495057; display: flex; align-items: center; transition: all 0.2s; }
        .btn-mover:hover:not(:disabled) { background: #1351B4; color: white; }
        .btn-mover:disabled { opacity: 0.3; cursor: not-allowed; }
        .acoes-inserir { display: flex; flex-direction: column; gap: 0.15rem; }
        .btn-inserir { display: flex; align-items: center; gap: 0.2rem; background: #e8f0fe; border: none; border-radius: 4px; padding: 0.2rem 0.4rem; cursor: pointer; color: #1351B4; font-size: 0.7rem; font-weight: 500; transition: all 0.2s; white-space: nowrap; }
        .btn-inserir:hover { background: #1351B4; color: white; }
        .btn-acao { display: flex; align-items: center; gap: 0.375rem; padding: 0.5rem 0.75rem; border: none; border-radius: 6px; font-weight: 500; font-size: 0.85rem; cursor: pointer; transition: all 0.2s; }
        .btn-editar { background: #1351B4; color: white; }
        .btn-editar:hover { background: #0c3d8a; transform: translateY(-1px); }
        .btn-deletar { background: #dc3545; color: white; }
        .btn-deletar:hover { background: #c82333; transform: translateY(-1px); }
        .etapa-detalhes { padding: 0 1rem 1rem 1rem; border-top: 1px solid #dee2e6; background: white; }
        .metadados-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 0.5rem; padding: 0.75rem; background: #f8f9fa; border-radius: 6px; margin-top: 0.75rem; }
        .metadado-item { font-size: 0.82rem; color: #495057; }
        .metadado-label { font-weight: 600; margin-right: 0.3rem; }
        .metadado-valor { color: #212529; }
        .detalhe-section { margin-top: 0.75rem; padding: 0.75rem; background: #e9ecef; border-radius: 6px; border-left: 4px solid #1351B4; }
        .detalhe-label { font-size: 0.82rem; font-weight: 600; color: #495057; margin-bottom: 0.4rem; }
        .detalhe-lista { margin: 0; padding-left: 1.2rem; font-size: 0.82rem; color: #495057; }
        .detalhe-lista li { margin-bottom: 0.2rem; }
        .detalhe-mais { color: #6c757d; font-style: italic; }
        .cenarios-preview { margin-top: 0.75rem; padding: 0.75rem; background: #fff3cd; border-radius: 6px; border-left: 4px solid #ffc107; }
        .cenarios-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
        .cenarios-titulo { font-size: 0.82rem; font-weight: 600; color: #856404; }
        .cenarios-icone { color: #856404; }
        .cenarios-lista { display: flex; flex-direction: column; gap: 0.375rem; margin-left: 1rem; }
        .cenario-item { display: flex; align-items: flex-start; gap: 0.5rem; font-size: 0.82rem; color: #495057; }
        .cenario-bullet { font-weight: 600; flex-shrink: 0; }
        .cenario-texto { flex: 1; word-break: break-word; }
        .cenario-sub-count { color: #6c757d; font-size: 0.75rem; }
        .cenario-mais { color: #6c757d; font-style: italic; }
        .adicionar-nova-section { margin-top: 1rem; padding-top: 1rem; border-top: 2px dashed #dee2e6; display: flex; justify-content: center; }
        .btn-adicionar-nova { display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem; background: #28a745; color: white; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
        .btn-adicionar-nova:hover { background: #218838; transform: translateY(-1px); }
        .etapas-footer { margin-top: 1.5rem; padding-top: 1rem; border-top: 2px solid #e9ecef; display: flex; gap: 1rem; justify-content: flex-end; }
        .btn-etapas { display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; transition: all 0.2s; font-size: 0.95rem; }
        .btn-cancelar { background: #6c757d; color: white; }
        .btn-cancelar:hover { background: #5a6268; transform: translateY(-1px); }
        .btn-salvar { background: #28a745; color: white; }
        .btn-salvar:hover:not(:disabled) { background: #218838; transform: translateY(-1px); }
        .btn-salvar:disabled { background: #ced4da; color: #6c757d; cursor: not-allowed; }
        .interface-editar-etapas::-webkit-scrollbar { width: 8px; }
        .interface-editar-etapas::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 4px; }
        .interface-editar-etapas::-webkit-scrollbar-thumb { background: #888; border-radius: 4px; }
        .interface-editar-etapas::-webkit-scrollbar-thumb:hover { background: #555; }
        @media (max-width: 768px) {
          .etapa-header-card { flex-direction: column; align-items: flex-start; }
          .etapa-acoes { width: 100%; justify-content: flex-end; }
          .etapas-footer { flex-direction: column; }
          .btn-etapas { width: 100%; justify-content: center; }
        }
      `}</style>
    </div>
  );
};

export default InterfaceEditarEtapas;
