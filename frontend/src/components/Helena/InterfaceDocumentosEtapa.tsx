import React, { useState } from "react";

interface TipoDocumento {
  tipo: string;
  descricao: string;
  hint_detalhamento: string;
}

interface InterfaceDocumentosEtapaProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

const InterfaceDocumentosEtapa: React.FC<InterfaceDocumentosEtapaProps> = ({ dados, onConfirm }) => {
  const tipos = (dados?.tipos_documentos as TipoDocumento[]) || [];
  const modo = (dados?.modo as string) || 'requeridos'; // 'requeridos' | 'gerados'
  const numeroEtapa = (dados?.numero_etapa as string) || '';

  const [selecionados, setSelecionados] = useState<Record<string, boolean>>({});
  const [detalhamentos, setDetalhamentos] = useState<Record<string, string>>({});
  const [customDoc, setCustomDoc] = useState('');

  const titulo = modo === 'requeridos'
    ? `Etapa ${numeroEtapa} — Documentos ANALISADOS/REQUERIDOS`
    : `Etapa ${numeroEtapa} — Documentos PRODUZIDOS/GERADOS`;

  const emoji = modo === 'requeridos' ? '📄' : '📤';

  const toggleTipo = (tipo: string) => {
    setSelecionados(prev => {
      const novo = { ...prev, [tipo]: !prev[tipo] };
      // Limpar detalhamento se desmarcou
      if (!novo[tipo]) {
        setDetalhamentos(prev2 => {
          const novo2 = { ...prev2 };
          delete novo2[tipo];
          return novo2;
        });
      }
      return novo;
    });
  };

  const setDetalhamento = (tipo: string, valor: string) => {
    setDetalhamentos(prev => ({ ...prev, [tipo]: valor }));
  };

  const adicionarCustom = () => {
    const doc = customDoc.trim();
    if (!doc) return;
    // Adicionar como tipo "custom" selecionado
    setSelecionados(prev => ({ ...prev, [`__custom__${doc}`]: true }));
    setDetalhamentos(prev => ({ ...prev, [`__custom__${doc}`]: doc }));
    setCustomDoc('');
  };

  const handleConfirm = () => {
    const docs: string[] = [];

    // Tipos selecionados do CSV
    for (const tipoDoc of tipos) {
      if (selecionados[tipoDoc.tipo]) {
        const detalhe = detalhamentos[tipoDoc.tipo]?.trim();
        if (detalhe) {
          docs.push(`${tipoDoc.tipo}: ${detalhe}`);
        } else {
          docs.push(tipoDoc.tipo);
        }
      }
    }

    // Custom entries
    for (const key of Object.keys(selecionados)) {
      if (key.startsWith('__custom__') && selecionados[key]) {
        docs.push(key.replace('__custom__', ''));
      }
    }

    if (docs.length === 0) {
      // Tratar como nenhum
      onConfirm('nenhum');
      return;
    }

    const chave = modo === 'requeridos' ? 'docs_requeridos' : 'docs_gerados';
    onConfirm(JSON.stringify({ [chave]: docs }));
  };

  const handleNenhum = () => {
    onConfirm('nenhum');
  };

  const qtdSelecionados = Object.values(selecionados).filter(Boolean).length;

  return (
    <div className="interface-container fade-in">
      <div className="interface-title">{emoji} {titulo}</div>

      <div className="docs-etapa-lista">
        {tipos.map((tipoDoc) => {
          // Não mostrar "Outro" na lista de checkboxes - já temos campo custom
          if (tipoDoc.tipo === 'Outro') return null;

          const checked = !!selecionados[tipoDoc.tipo];
          return (
            <div key={tipoDoc.tipo} className={`doc-tipo-item ${checked ? 'doc-tipo-selecionado' : ''}`}>
              <label className="doc-tipo-label">
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() => toggleTipo(tipoDoc.tipo)}
                />
                <div className="doc-tipo-info">
                  <span className="doc-tipo-nome">{tipoDoc.tipo}</span>
                  <span className="doc-tipo-desc">{tipoDoc.descricao}</span>
                </div>
              </label>

              {checked && tipoDoc.hint_detalhamento && (
                <div className="doc-tipo-detalhe">
                  <input
                    type="text"
                    placeholder={tipoDoc.hint_detalhamento}
                    value={detalhamentos[tipoDoc.tipo] || ''}
                    onChange={(e) => setDetalhamento(tipoDoc.tipo, e.target.value)}
                    className="doc-detalhe-input"
                  />
                </div>
              )}
            </div>
          );
        })}

        {/* Campo para documento personalizado */}
        <div className="doc-tipo-item doc-tipo-custom">
          <div className="doc-custom-header">Outro documento:</div>
          <div className="doc-custom-row">
            <input
              type="text"
              placeholder="Digite o nome do documento..."
              value={customDoc}
              onChange={(e) => setCustomDoc(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  adicionarCustom();
                }
              }}
              className="doc-detalhe-input"
            />
            <button
              type="button"
              className="btn-add-custom"
              onClick={adicionarCustom}
              disabled={!customDoc.trim()}
            >
              + Adicionar
            </button>
          </div>

          {/* Lista de custom docs adicionados */}
          {Object.keys(selecionados)
            .filter(k => k.startsWith('__custom__') && selecionados[k])
            .map(key => {
              const nome = key.replace('__custom__', '');
              return (
                <div key={key} className="doc-custom-item">
                  <span>{nome}</span>
                  <button
                    type="button"
                    className="btn-remover-custom"
                    onClick={() => {
                      setSelecionados(prev => {
                        const novo = { ...prev };
                        delete novo[key];
                        return novo;
                      });
                    }}
                  >
                    ✕
                  </button>
                </div>
              );
            })}
        </div>
      </div>

      {/* Ações */}
      <div className="docs-etapa-actions">
        <button className="btn-interface btn-secondary" onClick={handleNenhum}>
          Nenhum documento
        </button>
        <button className="btn-interface btn-primary" onClick={handleConfirm}>
          Confirmar ({qtdSelecionados} selecionado{qtdSelecionados !== 1 ? 's' : ''})
        </button>
      </div>

      <style>{`
        .docs-etapa-lista {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          margin: 1rem 0;
          max-height: 400px;
          overflow-y: auto;
          padding-right: 0.5rem;
        }

        .doc-tipo-item {
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 0.75rem 1rem;
          transition: all 0.15s;
        }

        .doc-tipo-item:hover {
          border-color: #1351B4;
        }

        .doc-tipo-selecionado {
          background: #e8f0fe;
          border-color: #1351B4;
        }

        .doc-tipo-label {
          display: flex;
          align-items: flex-start;
          gap: 0.75rem;
          cursor: pointer;
          margin: 0;
        }

        .doc-tipo-label input[type="checkbox"] {
          margin-top: 0.25rem;
          width: 18px;
          height: 18px;
          cursor: pointer;
          accent-color: #1351B4;
        }

        .doc-tipo-info {
          display: flex;
          flex-direction: column;
          gap: 0.15rem;
        }

        .doc-tipo-nome {
          font-weight: 600;
          color: #333;
          font-size: 0.95rem;
        }

        .doc-tipo-desc {
          color: #666;
          font-size: 0.8rem;
        }

        .doc-tipo-detalhe {
          margin-top: 0.5rem;
          padding-left: 2.5rem;
        }

        .doc-detalhe-input {
          width: 100%;
          padding: 0.5rem 0.75rem;
          border: 1px solid #ced4da;
          border-radius: 4px;
          font-size: 0.85rem;
        }

        .doc-detalhe-input:focus {
          outline: none;
          border-color: #1351B4;
          box-shadow: 0 0 0 2px rgba(19, 81, 180, 0.15);
        }

        .doc-tipo-custom {
          border-style: dashed;
          background: #fafafa;
        }

        .doc-custom-header {
          font-weight: 500;
          color: #495057;
          margin-bottom: 0.5rem;
          font-size: 0.9rem;
        }

        .doc-custom-row {
          display: flex;
          gap: 0.5rem;
        }

        .btn-add-custom {
          padding: 0.5rem 1rem;
          background: #1351B4;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 0.85rem;
          cursor: pointer;
          white-space: nowrap;
        }

        .btn-add-custom:disabled {
          background: #adb5bd;
          cursor: not-allowed;
        }

        .doc-custom-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-top: 0.5rem;
          padding: 0.4rem 0.75rem;
          background: #e8f0fe;
          border-radius: 4px;
          font-size: 0.85rem;
        }

        .btn-remover-custom {
          background: none;
          border: none;
          color: #dc3545;
          cursor: pointer;
          font-size: 1rem;
          padding: 0 0.25rem;
        }

        .docs-etapa-actions {
          display: flex;
          gap: 1rem;
          margin-top: 1rem;
        }

        .docs-etapa-actions .btn-interface {
          flex: 1;
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 6px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .docs-etapa-actions .btn-secondary {
          background: #6c757d;
          color: white;
        }

        .docs-etapa-actions .btn-secondary:hover {
          background: #5a6268;
        }

        .docs-etapa-actions .btn-primary {
          background: #1351B4;
          color: white;
        }

        .docs-etapa-actions .btn-primary:hover {
          background: #0f3d8a;
        }
      `}</style>
    </div>
  );
};

export default InterfaceDocumentosEtapa;
