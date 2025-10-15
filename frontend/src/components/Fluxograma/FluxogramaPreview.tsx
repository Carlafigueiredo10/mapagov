import { useEffect, useRef } from 'react';
import mermaid from 'mermaid';
import './FluxogramaPreview.css';

interface FluxogramaPreviewProps {
  code: string;
  isEmpty: boolean;
}

export default function FluxogramaPreview({ code, isEmpty }: FluxogramaPreviewProps) {
  const mermaidRef = useRef<HTMLDivElement>(null);

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

  return (
    <div className="fluxograma-preview">
      <div className="fluxograma-content">
        <div className="mermaid" ref={mermaidRef}>
          {code}
        </div>
      </div>

      <div className="fluxograma-actions">
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
          📥 Baixar SVG
        </button>

        <button
          className="action-btn"
          onClick={() => {
            navigator.clipboard.writeText(code);
            alert('Código Mermaid copiado para a área de transferência!');
          }}
        >
          📋 Copiar Código
        </button>

        <button
          className="action-btn"
          onClick={() => {
            window.print();
          }}
        >
          🖨️ Imprimir
        </button>
      </div>
    </div>
  );
}
