/**
 * Canvas de Escopo e Valor
 * Artefato do Domínio 2 - Escopo e Valor
 */

import React, { useState } from 'react';
import './Artefatos.css';

interface CanvasEscopoData {
  objetivoCentral: string;
  entregasPrincipais: string;
  valorPublico: string;
  indicadores: string;
  restricoes: string;
}

export const CanvasEscopoValor: React.FC = () => {
  const [dados, setDados] = useState<CanvasEscopoData>({
    objetivoCentral: '',
    entregasPrincipais: '',
    valorPublico: '',
    indicadores: '',
    restricoes: ''
  });

  const handleChange = (campo: keyof CanvasEscopoData, valor: string) => {
    setDados({ ...dados, [campo]: valor });
  };

  const handleExportar = () => {
    const texto = `
CANVAS DE ESCOPO E VALOR
========================

🎯 OBJETIVO CENTRAL
${dados.objetivoCentral || '(não preenchido)'}

📦 ENTREGAS PRINCIPAIS
${dados.entregasPrincipais || '(não preenchido)'}

💎 VALOR PÚBLICO ESPERADO
${dados.valorPublico || '(não preenchido)'}

📊 INDICADORES DE SUCESSO
${dados.indicadores || '(não preenchido)'}

⚠️ RESTRIÇÕES E RISCOS
${dados.restricoes || '(não preenchido)'}
    `.trim();

    const blob = new Blob([texto], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'canvas-escopo-valor.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <h2>📋 Canvas de Escopo e Valor</h2>
        <p className="artefato-descricao">
          Consolida, em um só quadro, o que será entregue, para quem e com qual impacto.
          Define produtos, metas, limites e critérios de sucesso.
        </p>
      </div>

      <div className="canvas-grid">
        {/* Objetivo Central */}
        <div className="canvas-card canvas-proposito">
          <label>
            <span className="canvas-icone">🎯</span>
            <strong>Objetivo Central</strong>
            <span className="canvas-hint">O que este projeto busca alcançar?</span>
          </label>
          <textarea
            value={dados.objetivoCentral}
            onChange={(e) => handleChange('objetivoCentral', e.target.value)}
            placeholder='Ex: "Expandir o ecoturismo sustentável."'
            rows={3}
          />
        </div>

        {/* Entregas Principais */}
        <div className="canvas-card canvas-valor">
          <label>
            <span className="canvas-icone">📦</span>
            <strong>Entregas Principais</strong>
            <span className="canvas-hint">Quais produtos tangíveis serão gerados?</span>
          </label>
          <textarea
            value={dados.entregasPrincipais}
            onChange={(e) => handleChange('entregasPrincipais', e.target.value)}
            placeholder='Ex: "Guia de operação, cursos, pilotos."'
            rows={3}
          />
        </div>

        {/* Valor Público Esperado */}
        <div className="canvas-card canvas-publico">
          <label>
            <span className="canvas-icone">💎</span>
            <strong>Valor Público Esperado</strong>
            <span className="canvas-hint">Que benefício social/institucional o projeto gera?</span>
          </label>
          <textarea
            value={dados.valorPublico}
            onChange={(e) => handleChange('valorPublico', e.target.value)}
            placeholder='Ex: "Aumento da renda local, preservação ambiental."'
            rows={3}
          />
        </div>

        {/* Indicadores de Sucesso */}
        <div className="canvas-card canvas-entregas">
          <label>
            <span className="canvas-icone">📊</span>
            <strong>Indicadores de Sucesso</strong>
            <span className="canvas-hint">Como será medida a entrega de valor?</span>
          </label>
          <textarea
            value={dados.indicadores}
            onChange={(e) => handleChange('indicadores', e.target.value)}
            placeholder='Ex: "Número de visitantes e guias formados."'
            rows={3}
          />
        </div>

        {/* Restrições e Riscos */}
        <div className="canvas-card canvas-riscos">
          <label>
            <span className="canvas-icone">⚠️</span>
            <strong>Restrições e Riscos</strong>
            <span className="canvas-hint">Quais limites e ameaças precisam ser registrados?</span>
          </label>
          <textarea
            value={dados.restricoes}
            onChange={(e) => handleChange('restricoes', e.target.value)}
            placeholder='Ex: "Recursos orçamentários e prazos sazonais."'
            rows={3}
          />
        </div>
      </div>

      <div className="artefato-footer">
        <button className="btn-exportar" onClick={handleExportar}>
          📥 Exportar Canvas
        </button>
        <button className="btn-secundario" onClick={() => window.history.back()}>
          ← Voltar
        </button>
      </div>
    </div>
  );
};

export default CanvasEscopoValor;
