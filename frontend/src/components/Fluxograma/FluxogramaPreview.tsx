import { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import './FluxogramaPreview.css';

interface FluxogramaPreviewProps {
  code: string;
  isEmpty: boolean;
  defaultTitulo?: string;
}

export default function FluxogramaPreview({ code, isEmpty, defaultTitulo }: FluxogramaPreviewProps) {
  const mermaidRef = useRef<HTMLDivElement>(null);
  const [showHeader, setShowHeader] = useState(true);
  const [titulo, setTitulo] = useState('');
  const [unidade, setUnidade] = useState('');
  const [versao, setVersao] = useState('1.0');

  useEffect(() => {
    mermaid.initialize({
      startOnLoad: true,
      theme: 'default',
      securityLevel: 'loose',
      flowchart: {
        useMaxWidth: true,
        htmlLabels: true,
        curve: 'basis',
      },
    });
  }, []);

  useEffect(() => {
    if (code && mermaidRef.current) {
      mermaidRef.current.innerHTML = code;
      mermaid.contentLoaded();
    }
  }, [code]);

  useEffect(() => {
    if (defaultTitulo && !titulo) {
      setTitulo(defaultTitulo);
    }
  }, [defaultTitulo]);

  if (isEmpty) {
    return (
      <div className="fluxograma-preview empty">
        <div className="empty-state">
          <div className="empty-icon">📈</div>
          <p>O fluxograma aparecerá aqui após a conversa com Helena</p>
        </div>
      </div>
    );
  }

  const dataAtual = new Date().toLocaleDateString('pt-BR');

  return (
    <div className="fluxograma-preview">
      {/* Configuração do cabeçalho (não imprime) */}
      <div className="pdf-config no-print">
        <label className="toggle-header">
          <input
            type="checkbox"
            checked={showHeader}
            onChange={(e) => setShowHeader(e.target.checked)}
          />
          Incluir cabeçalho no PDF
        </label>
        {showHeader && (
          <div className="header-fields">
            <input
              type="text"
              value={titulo}
              onChange={(e) => setTitulo(e.target.value)}
              placeholder="Título do processo"
            />
            <input
              type="text"
              value={unidade}
              onChange={(e) => setUnidade(e.target.value)}
              placeholder="Unidade / Órgão (opcional)"
            />
            <input
              type="text"
              value={versao}
              onChange={(e) => setVersao(e.target.value)}
              placeholder="Versão"
            />
          </div>
        )}
      </div>

      {/* Área de impressão */}
      <div className="print-area" id="fluxograma-print-area">
        {showHeader && (
          <div className="print-header">
            <h2>{titulo || 'Fluxograma de Processo'}</h2>
            <div className="print-header-meta">
              {unidade && <span>Unidade: {unidade}</span>}
              <span>Versão: {versao}</span>
              <span>Data: {dataAtual}</span>
            </div>
          </div>
        )}

        <div className="fluxograma-content">
          <div className="mermaid" ref={mermaidRef}>
            {code}
          </div>
        </div>
      </div>

      {/* Botões (não imprime) */}
      <div className="fluxograma-actions no-print">
        <button
          className="action-btn action-btn-primary"
          onClick={() => window.print()}
        >
          Exportar PDF
        </button>
        <button
          className="action-btn"
          onClick={() => {
            const svgElement = mermaidRef.current?.querySelector('svg');
            if (svgElement) {
              const svgData = new XMLSerializer().serializeToString(svgElement);
              const blob = new Blob([svgData], { type: 'image/svg+xml' });
              const url = URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.download = 'fluxograma.svg';
              link.click();
              URL.revokeObjectURL(url);
            }
          }}
        >
          Baixar SVG
        </button>
        <button
          className="action-btn"
          onClick={() => {
            navigator.clipboard.writeText(code);
            alert('Código Mermaid copiado!');
          }}
        >
          Copiar Código
        </button>
      </div>
    </div>
  );
}
