import React, { useState } from 'react';
import { Edit2, Trash2, Plus, ChevronDown, ChevronRight, AlertCircle } from 'lucide-react';

interface Subetapa {
  numero?: string;
  descricao: string;
  sistemas?: string[];
  documentos?: string[];
}

interface Cenario {
  descricao: string;
  resultado?: string;
}

interface Etapa {
  numero: number;
  descricao: string;
  sistemas?: string[];
  documentos?: string[];
  subetapas?: Subetapa[];
  tem_decisoes?: boolean | string;
  tipo_decisao?: string;
  cenarios?: Cenario[];
}

interface InterfaceEditarEtapasProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

const InterfaceEditarEtapas: React.FC<InterfaceEditarEtapasProps> = ({ dados, onConfirm }) => {
  const etapasOriginais = (dados?.etapas as Etapa[]) || [];
  const [etapas, setEtapas] = useState<Etapa[]>([...etapasOriginais]);
  const [expandidas, setExpandidas] = useState<Record<number, boolean>>({});
  const [acaoSelecionada, setAcaoSelecionada] = useState<{ tipo: 'editar' | 'adicionar' | 'deletar' | null, numeroEtapa?: number }>({ tipo: null });

  // Toggle expansão de etapa
  const toggleExpansao = (numero: number) => {
    setExpandidas(prev => ({ ...prev, [numero]: !prev[numero] }));
  };

  // Handler para deletar etapa
  const handleDeletar = (numero: number) => {
    const etapaParaDeletar = etapas.find(e => e.numero === numero);
    if (!etapaParaDeletar) return;

    const confirmacao = confirm(`Tem certeza que deseja deletar a Etapa ${numero}?\n\n"${etapaParaDeletar.descricao}"\n\nEsta ação não pode ser desfeita.`);

    if (confirmacao) {
      // Remover etapa
      const novasEtapas = etapas.filter(e => e.numero !== numero);

      // Renumerar etapas
      const etapasRenumeradas = novasEtapas.map((etapa, idx) => ({
        ...etapa,
        numero: idx + 1
      }));

      setEtapas(etapasRenumeradas);

      // Limpar expansão da etapa deletada
      setExpandidas(prev => {
        const novo = { ...prev };
        delete novo[numero];
        return novo;
      });
    }
  };

  // Handler para editar etapa
  const handleEditar = (numero: number) => {
    setAcaoSelecionada({ tipo: 'editar', numeroEtapa: numero });
    // Enviar para backend para iniciar edição
    onConfirm(JSON.stringify({
      acao: 'editar_etapa',
      numero_etapa: numero
    }));
  };

  // Handler para adicionar nova etapa
  const handleAdicionarNova = () => {
    setAcaoSelecionada({ tipo: 'adicionar' });
    // Enviar para backend para iniciar adição
    onConfirm(JSON.stringify({
      acao: 'adicionar_etapa',
      numero_etapa: etapas.length + 1
    }));
  };

  // Handler para salvar alterações
  const handleSalvar = () => {
    if (etapas.length === 0) {
      alert('Você precisa ter pelo menos uma etapa no processo.');
      return;
    }

    // Enviar etapas atualizadas para backend
    onConfirm(JSON.stringify({
      acao: 'salvar_etapas',
      etapas: etapas
    }));
  };

  // Handler para cancelar
  const handleCancelar = () => {
    onConfirm('cancelar');
  };

  // Renderizar preview de subetapas
  const renderSubetapas = (subetapas: Subetapa[]) => {
    if (!subetapas || subetapas.length === 0) return null;

    return (
      <div className="subetapas-preview">
        <div className="subetapas-header">
          <span className="subetapas-icone">└─</span>
          <span className="subetapas-titulo">Subetapas ({subetapas.length}):</span>
        </div>
        <div className="subetapas-lista">
          {subetapas.slice(0, 3).map((sub, idx) => (
            <div key={idx} className="subetapa-item">
              <span className="subetapa-numero">{sub.numero || `${idx + 1}`}.</span>
              <span className="subetapa-texto">{sub.descricao}</span>
            </div>
          ))}
          {subetapas.length > 3 && (
            <div className="subetapa-item subetapa-mais">
              <span>... e mais {subetapas.length - 3} subetapa(s)</span>
            </div>
          )}
        </div>
      </div>
    );
  };

  // Renderizar preview de cenários
  const renderCenarios = (cenarios: Cenario[], tipoDecisao?: string) => {
    if (!cenarios || cenarios.length === 0) return null;

    return (
      <div className="cenarios-preview">
        <div className="cenarios-header">
          <AlertCircle size={16} className="cenarios-icone" />
          <span className="cenarios-titulo">
            Etapa Condicional {tipoDecisao ? `(${tipoDecisao})` : ''} - {cenarios.length} cenário(s):
          </span>
        </div>
        <div className="cenarios-lista">
          {cenarios.slice(0, 2).map((cen, idx) => (
            <div key={idx} className="cenario-item">
              <span className="cenario-bullet">•</span>
              <span className="cenario-texto">{cen.descricao}</span>
            </div>
          ))}
          {cenarios.length > 2 && (
            <div className="cenario-item cenario-mais">
              <span>... e mais {cenarios.length - 2} cenário(s)</span>
            </div>
          )}
        </div>
      </div>
    );
  };

  // Renderizar sistemas e documentos
  const renderRecursos = (etapa: Etapa) => {
    const temSistemas = etapa.sistemas && etapa.sistemas.length > 0;
    const temDocumentos = etapa.documentos && etapa.documentos.length > 0;

    if (!temSistemas && !temDocumentos) return null;

    return (
      <div className="recursos-preview">
        {temSistemas && (
          <div className="recurso-item">
            <span className="recurso-icone">💻</span>
            <span className="recurso-texto">Sistemas: {etapa.sistemas!.join(', ')}</span>
          </div>
        )}
        {temDocumentos && (
          <div className="recurso-item">
            <span className="recurso-icone">📄</span>
            <span className="recurso-texto">Documentos: {etapa.documentos!.join(', ')}</span>
          </div>
        )}
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
          Você pode adicionar, editar ou remover etapas.
        </p>
      </div>

      {etapas.length === 0 ? (
        <div className="etapas-vazias">
          <AlertCircle size={48} className="icon-alerta" />
          <p className="texto-vazio">Nenhuma etapa no processo ainda.</p>
          <button
            onClick={handleAdicionarNova}
            className="btn-adicionar-primeira"
          >
            <Plus size={20} />
            Adicionar Primeira Etapa
          </button>
        </div>
      ) : (
        <div className="etapas-lista">
          {etapas.map((etapa) => {
            const estaExpandida = expandidas[etapa.numero];
            const temSubetapas = etapa.subetapas && etapa.subetapas.length > 0;
            const temCondicional = etapa.tem_decisoes === true || etapa.tem_decisoes === 'sim';
            const temCenarios = etapa.cenarios && etapa.cenarios.length > 0;

            return (
              <div key={etapa.numero} className="etapa-card">
                <div className="etapa-header-card">
                  <div className="etapa-info-principal">
                    <button
                      onClick={() => toggleExpansao(etapa.numero)}
                      className="btn-expandir"
                      aria-label={estaExpandida ? 'Recolher' : 'Expandir'}
                    >
                      {estaExpandida ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                    </button>
                    <div className="etapa-numero-badge">
                      Etapa {etapa.numero}
                    </div>
                    <div className="etapa-descricao-principal">
                      <span className="etapa-descricao-texto">{etapa.descricao}</span>
                      {temCondicional && (
                        <span className="badge-condicional" title="Etapa com decisões condicionais">
                          <AlertCircle size={14} />
                          Condicional
                        </span>
                      )}
                      {temSubetapas && (
                        <span className="badge-subetapas" title={`${etapa.subetapas!.length} subetapas`}>
                          └─ {etapa.subetapas!.length}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="etapa-acoes">
                    <button
                      onClick={() => handleEditar(etapa.numero)}
                      className="btn-acao btn-editar"
                      title="Editar esta etapa"
                    >
                      <Edit2 size={18} />
                      Editar
                    </button>
                    <button
                      onClick={() => handleDeletar(etapa.numero)}
                      className="btn-acao btn-deletar"
                      title="Deletar esta etapa"
                    >
                      <Trash2 size={18} />
                      Deletar
                    </button>
                  </div>
                </div>

                {estaExpandida && (
                  <div className="etapa-detalhes">
                    {renderRecursos(etapa)}
                    {temSubetapas && renderSubetapas(etapa.subetapas!)}
                    {temCondicional && temCenarios && renderCenarios(etapa.cenarios!, etapa.tipo_decisao)}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {etapas.length > 0 && (
        <div className="adicionar-nova-section">
          <button
            onClick={handleAdicionarNova}
            className="btn-adicionar-nova"
          >
            <Plus size={20} />
            Adicionar Nova Etapa
          </button>
        </div>
      )}

      <div className="etapas-footer">
        <button
          onClick={handleCancelar}
          className="btn-etapas btn-cancelar"
        >
          Cancelar
        </button>
        <button
          onClick={handleSalvar}
          className="btn-etapas btn-salvar"
          disabled={etapas.length === 0}
        >
          <Edit2 size={18} />
          Salvar Alterações
        </button>
      </div>

      <style>{`
        .interface-editar-etapas {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          max-height: 70vh;
          overflow-y: auto;
        }

        .etapas-header {
          margin-bottom: 1.5rem;
          padding-bottom: 1rem;
          border-bottom: 2px solid #e9ecef;
        }

        .etapas-title {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 0.5rem;
        }

        .etapas-title h2 {
          margin: 0;
          font-size: 1.5rem;
          color: #212529;
        }

        .icon-edit {
          color: #007bff;
        }

        .etapas-subtitle {
          margin: 0;
          color: #6c757d;
          font-size: 0.95rem;
        }

        .etapas-vazias {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 3rem 1rem;
          background: #f8f9fa;
          border-radius: 8px;
          border: 2px dashed #dee2e6;
        }

        .icon-alerta {
          color: #ffc107;
          margin-bottom: 1rem;
        }

        .texto-vazio {
          color: #6c757d;
          font-size: 1.1rem;
          margin-bottom: 1.5rem;
        }

        .btn-adicionar-primeira {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1.5rem;
          background: #007bff;
          color: white;
          border: none;
          border-radius: 6px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-adicionar-primeira:hover {
          background: #0056b3;
          transform: translateY(-1px);
        }

        .etapas-lista {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
          margin-bottom: 1.5rem;
        }

        .etapa-card {
          background: #f8f9fa;
          border: 2px solid #dee2e6;
          border-radius: 8px;
          overflow: hidden;
          transition: all 0.2s;
        }

        .etapa-card:hover {
          border-color: #adb5bd;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .etapa-header-card {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 1rem;
          gap: 1rem;
        }

        .etapa-info-principal {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          flex: 1;
          min-width: 0;
        }

        .btn-expandir {
          background: none;
          border: none;
          padding: 0.25rem;
          cursor: pointer;
          color: #6c757d;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
          flex-shrink: 0;
        }

        .btn-expandir:hover {
          color: #212529;
          transform: scale(1.1);
        }

        .etapa-numero-badge {
          background: #007bff;
          color: white;
          padding: 0.375rem 0.75rem;
          border-radius: 6px;
          font-weight: 600;
          font-size: 0.85rem;
          flex-shrink: 0;
        }

        .etapa-descricao-principal {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          flex: 1;
          min-width: 0;
          flex-wrap: wrap;
        }

        .etapa-descricao-texto {
          font-size: 0.95rem;
          color: #212529;
          font-weight: 500;
          word-break: break-word;
        }

        .badge-condicional,
        .badge-subetapas {
          display: inline-flex;
          align-items: center;
          gap: 0.25rem;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.75rem;
          font-weight: 600;
          white-space: nowrap;
        }

        .badge-condicional {
          background: #fff3cd;
          color: #856404;
          border: 1px solid #ffc107;
        }

        .badge-subetapas {
          background: #e7f3ff;
          color: #004085;
          border: 1px solid #b8daff;
        }

        .etapa-acoes {
          display: flex;
          gap: 0.5rem;
          flex-shrink: 0;
        }

        .btn-acao {
          display: flex;
          align-items: center;
          gap: 0.375rem;
          padding: 0.5rem 0.75rem;
          border: none;
          border-radius: 6px;
          font-weight: 500;
          font-size: 0.85rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-editar {
          background: #007bff;
          color: white;
        }

        .btn-editar:hover {
          background: #0056b3;
          transform: translateY(-1px);
        }

        .btn-deletar {
          background: #dc3545;
          color: white;
        }

        .btn-deletar:hover {
          background: #c82333;
          transform: translateY(-1px);
        }

        .etapa-detalhes {
          padding: 0 1rem 1rem 1rem;
          border-top: 1px solid #dee2e6;
          background: white;
        }

        .recursos-preview {
          padding: 0.75rem;
          background: #f8f9fa;
          border-radius: 6px;
          margin-top: 0.75rem;
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .recurso-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.85rem;
          color: #495057;
        }

        .recurso-icone {
          font-size: 1rem;
        }

        .recurso-texto {
          flex: 1;
          word-break: break-word;
        }

        .subetapas-preview,
        .cenarios-preview {
          margin-top: 0.75rem;
          padding: 0.75rem;
          background: #e9ecef;
          border-radius: 6px;
          border-left: 4px solid #007bff;
        }

        .cenarios-preview {
          border-left-color: #ffc107;
          background: #fff3cd;
        }

        .subetapas-header,
        .cenarios-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
        }

        .subetapas-icone {
          font-size: 0.9rem;
          color: #6c757d;
          font-weight: bold;
        }

        .subetapas-titulo,
        .cenarios-titulo {
          font-size: 0.85rem;
          font-weight: 600;
          color: #495057;
        }

        .cenarios-icone {
          color: #856404;
        }

        .subetapas-lista,
        .cenarios-lista {
          display: flex;
          flex-direction: column;
          gap: 0.375rem;
          margin-left: 1rem;
        }

        .subetapa-item,
        .cenario-item {
          display: flex;
          align-items: flex-start;
          gap: 0.5rem;
          font-size: 0.85rem;
          color: #495057;
        }

        .subetapa-numero,
        .cenario-bullet {
          font-weight: 600;
          flex-shrink: 0;
        }

        .subetapa-texto,
        .cenario-texto {
          flex: 1;
          word-break: break-word;
        }

        .subetapa-mais,
        .cenario-mais {
          color: #6c757d;
          font-style: italic;
        }

        .adicionar-nova-section {
          margin-top: 1rem;
          padding-top: 1rem;
          border-top: 2px dashed #dee2e6;
          display: flex;
          justify-content: center;
        }

        .btn-adicionar-nova {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1.5rem;
          background: #28a745;
          color: white;
          border: none;
          border-radius: 6px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-adicionar-nova:hover {
          background: #218838;
          transform: translateY(-1px);
        }

        .etapas-footer {
          margin-top: 1.5rem;
          padding-top: 1rem;
          border-top: 2px solid #e9ecef;
          display: flex;
          gap: 1rem;
          justify-content: flex-end;
        }

        .btn-etapas {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 6px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          font-size: 0.95rem;
        }

        .btn-cancelar {
          background: #6c757d;
          color: white;
        }

        .btn-cancelar:hover {
          background: #5a6268;
          transform: translateY(-1px);
        }

        .btn-salvar {
          background: #28a745;
          color: white;
        }

        .btn-salvar:hover:not(:disabled) {
          background: #218838;
          transform: translateY(-1px);
        }

        .btn-salvar:disabled {
          background: #ced4da;
          color: #6c757d;
          cursor: not-allowed;
        }

        /* Scroll customizado */
        .interface-editar-etapas::-webkit-scrollbar {
          width: 8px;
        }

        .interface-editar-etapas::-webkit-scrollbar-track {
          background: #f1f1f1;
          border-radius: 4px;
        }

        .interface-editar-etapas::-webkit-scrollbar-thumb {
          background: #888;
          border-radius: 4px;
        }

        .interface-editar-etapas::-webkit-scrollbar-thumb:hover {
          background: #555;
        }

        /* Responsividade */
        @media (max-width: 768px) {
          .etapa-header-card {
            flex-direction: column;
            align-items: flex-start;
          }

          .etapa-acoes {
            width: 100%;
            justify-content: flex-end;
          }

          .etapas-footer {
            flex-direction: column;
          }

          .btn-etapas {
            width: 100%;
            justify-content: center;
          }
        }
      `}</style>
    </div>
  );
};

export default InterfaceEditarEtapas;
