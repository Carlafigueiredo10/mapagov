import React, { useState, useCallback, useEffect } from "react";

export interface TipoDocumento {
  tipo: string;
  descricao: string;
  hint_detalhamento: string;
}

interface DocumentoSelectorProps {
  tipos: TipoDocumento[];
  value: string[];
  onChange: (docs: string[]) => void;
  titulo?: string;
}

/**
 * Seletor reutilizavel de documentos (sem botoes de submit).
 * Expoe estado via onChange(docs: string[]).
 *
 * Cada doc selecionado gera "Tipo: detalhe" (se houver detalhe) ou "Tipo".
 * Docs customizados sao strings puras.
 */
const DocumentoSelector: React.FC<DocumentoSelectorProps> = ({ tipos, value, onChange, titulo }) => {
  // Parsear value inicial em selecionados + detalhamentos
  const parseValue = useCallback((docs: string[]) => {
    const sel: Record<string, boolean> = {};
    const det: Record<string, string> = {};
    const custom: string[] = [];

    for (const doc of docs) {
      // Tentar match com tipos conhecidos
      const tipoMatch = tipos.find(t => doc === t.tipo || doc.startsWith(`${t.tipo}: `));
      if (tipoMatch) {
        sel[tipoMatch.tipo] = true;
        if (doc.startsWith(`${tipoMatch.tipo}: `)) {
          det[tipoMatch.tipo] = doc.slice(tipoMatch.tipo.length + 2);
        }
      } else {
        custom.push(doc);
      }
    }

    return { sel, det, custom };
  }, [tipos]);

  const parsed = parseValue(value);
  const [selecionados, setSelecionados] = useState<Record<string, boolean>>(parsed.sel);
  const [detalhamentos, setDetalhamentos] = useState<Record<string, string>>(parsed.det);
  const [customDocs, setCustomDocs] = useState<string[]>(parsed.custom);
  const [customInput, setCustomInput] = useState('');

  // Build output and notify parent
  const emitChange = useCallback((sel: Record<string, boolean>, det: Record<string, string>, custom: string[]) => {
    const docs: string[] = [];

    for (const tipoDoc of tipos) {
      if (sel[tipoDoc.tipo]) {
        const detalhe = det[tipoDoc.tipo]?.trim();
        docs.push(detalhe ? `${tipoDoc.tipo}: ${detalhe}` : tipoDoc.tipo);
      }
    }

    for (const doc of custom) {
      docs.push(doc);
    }

    onChange(docs);
  }, [tipos, onChange]);

  const toggleTipo = (tipo: string) => {
    setSelecionados(prev => {
      const novo = { ...prev, [tipo]: !prev[tipo] };
      const novoDet = { ...detalhamentos };
      if (!novo[tipo]) {
        delete novoDet[tipo];
        setDetalhamentos(novoDet);
      }
      // Emit with updated state
      setTimeout(() => emitChange(novo, novoDet, customDocs), 0);
      return novo;
    });
  };

  const updateDetalhamento = (tipo: string, valor: string) => {
    setDetalhamentos(prev => {
      const novo = { ...prev, [tipo]: valor };
      setTimeout(() => emitChange(selecionados, novo, customDocs), 0);
      return novo;
    });
  };

  const adicionarCustom = () => {
    const doc = customInput.trim();
    if (!doc || customDocs.includes(doc)) return;
    const novoCustom = [...customDocs, doc];
    setCustomDocs(novoCustom);
    setCustomInput('');
    emitChange(selecionados, detalhamentos, novoCustom);
  };

  const removerCustom = (doc: string) => {
    const novoCustom = customDocs.filter(d => d !== doc);
    setCustomDocs(novoCustom);
    emitChange(selecionados, detalhamentos, novoCustom);
  };

  const qtd = Object.values(selecionados).filter(Boolean).length + customDocs.length;

  return (
    <div className="doc-selector">
      {titulo && (
        <div className="doc-selector-titulo">{titulo} {qtd > 0 && <span className="doc-selector-badge">{qtd}</span>}</div>
      )}

      <div className="doc-selector-lista">
        {tipos.map((tipoDoc) => {
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
                    onChange={(e) => updateDetalhamento(tipoDoc.tipo, e.target.value)}
                    className="doc-detalhe-input"
                  />
                </div>
              )}
            </div>
          );
        })}

        {/* Custom doc input */}
        <div className="doc-tipo-item doc-tipo-custom">
          <div className="doc-custom-header">Outro documento:</div>
          <div className="doc-custom-row">
            <input
              type="text"
              placeholder="Digite o nome do documento..."
              value={customInput}
              onChange={(e) => setCustomInput(e.target.value)}
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
              disabled={!customInput.trim()}
            >
              + Adicionar
            </button>
          </div>
          {customDocs.map(doc => (
            <div key={doc} className="doc-custom-item">
              <span>{doc}</span>
              <button type="button" className="btn-remover-custom" onClick={() => removerCustom(doc)}>
                ✕
              </button>
            </div>
          ))}
        </div>
      </div>

      <style>{`
        .doc-selector { width: 100%; }
        .doc-selector-titulo {
          font-weight: 600;
          color: #333;
          font-size: 0.95rem;
          margin-bottom: 0.5rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        .doc-selector-badge {
          background: #1351B4;
          color: white;
          border-radius: 10px;
          padding: 0.1rem 0.5rem;
          font-size: 0.75rem;
        }
        .doc-selector-lista {
          display: flex;
          flex-direction: column;
          gap: 0.4rem;
          max-height: 280px;
          overflow-y: auto;
          padding-right: 0.25rem;
        }
        .doc-tipo-item {
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 6px;
          padding: 0.5rem 0.75rem;
          transition: all 0.15s;
        }
        .doc-tipo-item:hover { border-color: #1351B4; }
        .doc-tipo-selecionado { background: #e8f0fe; border-color: #1351B4; }
        .doc-tipo-label {
          display: flex;
          align-items: flex-start;
          gap: 0.5rem;
          cursor: pointer;
          margin: 0;
        }
        .doc-tipo-label input[type="checkbox"] {
          margin-top: 0.2rem;
          width: 16px;
          height: 16px;
          cursor: pointer;
          accent-color: #1351B4;
        }
        .doc-tipo-info { display: flex; flex-direction: column; gap: 0.1rem; }
        .doc-tipo-nome { font-weight: 600; color: #333; font-size: 0.85rem; }
        .doc-tipo-desc { color: #666; font-size: 0.75rem; }
        .doc-tipo-detalhe { margin-top: 0.4rem; padding-left: 1.75rem; }
        .doc-detalhe-input {
          width: 100%;
          padding: 0.4rem 0.6rem;
          border: 1px solid #ced4da;
          border-radius: 4px;
          font-size: 0.8rem;
        }
        .doc-detalhe-input:focus {
          outline: none;
          border-color: #1351B4;
          box-shadow: 0 0 0 2px rgba(19, 81, 180, 0.15);
        }
        .doc-tipo-custom { border-style: dashed; background: #fafafa; }
        .doc-custom-header { font-weight: 500; color: #495057; margin-bottom: 0.4rem; font-size: 0.85rem; }
        .doc-custom-row { display: flex; gap: 0.5rem; }
        .btn-add-custom {
          padding: 0.4rem 0.75rem;
          background: #1351B4;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 0.8rem;
          cursor: pointer;
          white-space: nowrap;
        }
        .btn-add-custom:disabled { background: #adb5bd; cursor: not-allowed; }
        .doc-custom-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-top: 0.4rem;
          padding: 0.3rem 0.6rem;
          background: #e8f0fe;
          border-radius: 4px;
          font-size: 0.8rem;
        }
        .btn-remover-custom {
          background: none;
          border: none;
          color: #dc3545;
          cursor: pointer;
          font-size: 0.9rem;
          padding: 0 0.25rem;
        }
      `}</style>
    </div>
  );
};

export default DocumentoSelector;
