import React, { useState } from "react";
import DocumentoSelector, { TipoDocumento } from "./DocumentoSelector";

interface InterfaceDocumentosEtapaProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

/**
 * Interface standalone para coleta de documentos por etapa (fluxo conversacional).
 * Usa DocumentoSelector internamente + botoes Confirmar/Nenhum.
 */
const InterfaceDocumentosEtapa: React.FC<InterfaceDocumentosEtapaProps> = ({ dados, onConfirm }) => {
  const tipos = (dados?.tipos_documentos as TipoDocumento[]) || [];
  const modo = (dados?.modo as string) || 'requeridos';
  const numeroEtapa = (dados?.numero_etapa as string) || '';

  const [docs, setDocs] = useState<string[]>([]);

  const titulo = modo === 'requeridos'
    ? `Etapa ${numeroEtapa} — Documentos ANALISADOS/REQUERIDOS`
    : `Etapa ${numeroEtapa} — Documentos PRODUZIDOS/GERADOS`;

  const emoji = modo === 'requeridos' ? '\u{1F4C4}' : '\u{1F4E4}';

  const handleConfirm = () => {
    if (docs.length === 0) {
      onConfirm('nenhum');
      return;
    }
    const chave = modo === 'requeridos' ? 'docs_requeridos' : 'docs_gerados';
    onConfirm(JSON.stringify({ [chave]: docs }));
  };

  return (
    <div className="interface-container fade-in">
      <div className="interface-title">{emoji} {titulo}</div>

      <div style={{ margin: '1rem 0' }}>
        <DocumentoSelector
          tipos={tipos}
          value={docs}
          onChange={setDocs}
        />
      </div>

      <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
        <button
          onClick={() => onConfirm('nenhum')}
          style={{ flex: 1, padding: '0.75rem', border: 'none', borderRadius: '6px', fontWeight: 500, cursor: 'pointer', background: '#6c757d', color: 'white' }}
        >
          Nenhum documento
        </button>
        <button
          onClick={handleConfirm}
          style={{ flex: 1, padding: '0.75rem', border: 'none', borderRadius: '6px', fontWeight: 500, cursor: 'pointer', background: '#1351B4', color: 'white' }}
        >
          Confirmar ({docs.length} selecionado{docs.length !== 1 ? 's' : ''})
        </button>
      </div>
    </div>
  );
};

export default InterfaceDocumentosEtapa;
