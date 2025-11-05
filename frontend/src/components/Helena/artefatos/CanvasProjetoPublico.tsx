/**
 * Canvas de Projeto Público
 * Artefato visual e interativo do Domínio 1
 */

import React, { useState } from 'react';
import './Artefatos.css';

interface CanvasData {
  proposito: string;
  valorPublico: string;
  publicoAlvo: string;
  principaisEntregas: string;
  recursos: string;
  riscosIniciais: string;
}

export const CanvasProjetoPublico: React.FC = () => {
  const [dados, setDados] = useState<CanvasData>({
    proposito: '',
    valorPublico: '',
    publicoAlvo: '',
    principaisEntregas: '',
    recursos: '',
    riscosIniciais: ''
  });

  const handleChange = (campo: keyof CanvasData, valor: string) => {
    setDados({ ...dados, [campo]: valor });
  };

  const handleExportar = () => {
    const texto = `
CANVAS DE PROJETO PÚBLICO
========================

🎯 PROPÓSITO
${dados.proposito || '(não preenchido)'}

💎 VALOR PÚBLICO
${dados.valorPublico || '(não preenchido)'}

👥 PÚBLICO-ALVO
${dados.publicoAlvo || '(não preenchido)'}

📦 PRINCIPAIS ENTREGAS
${dados.principaisEntregas || '(não preenchido)'}

🛠️ RECURSOS
${dados.recursos || '(não preenchido)'}

⚠️ RISCOS INICIAIS
${dados.riscosIniciais || '(não preenchido)'}
    `.trim();

    const blob = new Blob([texto], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'canvas-projeto-publico.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="artefato-container">
      <div className="artefato-header">
        <h2>🧰 Canvas de Projeto Público</h2>
        <p className="artefato-descricao">
          Ajuda o gestor a enxergar o projeto em uma única tela, respondendo às perguntas essenciais:
          <strong>Por quê? Para quem? O quê? Como? Com quem?</strong>
        </p>
      </div>

      <div className="canvas-grid">
        {/* Propósito */}
        <div className="canvas-card canvas-proposito">
          <label>
            <span className="canvas-icone">🎯</span>
            <strong>Propósito</strong>
            <span className="canvas-hint">Qual o problema que estamos resolvendo?</span>
          </label>
          <textarea
            value={dados.proposito}
            onChange={(e) => handleChange('proposito', e.target.value)}
            placeholder='Ex: "Baixa adesão de servidores ao PGD."'
            rows={3}
          />
        </div>

        {/* Valor Público */}
        <div className="canvas-card canvas-valor">
          <label>
            <span className="canvas-icone">💎</span>
            <strong>Valor Público</strong>
            <span className="canvas-hint">Que benefício concreto o projeto gera?</span>
          </label>
          <textarea
            value={dados.valorPublico}
            onChange={(e) => handleChange('valorPublico', e.target.value)}
            placeholder='Ex: "Maior eficiência e qualidade de vida no trabalho."'
            rows={3}
          />
        </div>

        {/* Público-Alvo */}
        <div className="canvas-card canvas-publico">
          <label>
            <span className="canvas-icone">👥</span>
            <strong>Público-Alvo</strong>
            <span className="canvas-hint">Quem será impactado diretamente?</span>
          </label>
          <textarea
            value={dados.publicoAlvo}
            onChange={(e) => handleChange('publicoAlvo', e.target.value)}
            placeholder='Ex: "Servidores ativos do DECIPEX."'
            rows={3}
          />
        </div>

        {/* Principais Entregas */}
        <div className="canvas-card canvas-entregas">
          <label>
            <span className="canvas-icone">📦</span>
            <strong>Principais Entregas</strong>
            <span className="canvas-hint">O que o projeto vai entregar?</span>
          </label>
          <textarea
            value={dados.principaisEntregas}
            onChange={(e) => handleChange('principaisEntregas', e.target.value)}
            placeholder='Ex: "Sistema, manual, capacitação."'
            rows={3}
          />
        </div>

        {/* Recursos */}
        <div className="canvas-card canvas-recursos">
          <label>
            <span className="canvas-icone">🛠️</span>
            <strong>Recursos</strong>
            <span className="canvas-hint">O que já temos e o que falta?</span>
          </label>
          <textarea
            value={dados.recursos}
            onChange={(e) => handleChange('recursos', e.target.value)}
            placeholder='Ex: "Equipe técnica, orçamento, apoio da direção."'
            rows={3}
          />
        </div>

        {/* Riscos Iniciais */}
        <div className="canvas-card canvas-riscos">
          <label>
            <span className="canvas-icone">⚠️</span>
            <strong>Riscos Iniciais</strong>
            <span className="canvas-hint">O que pode atrapalhar?</span>
          </label>
          <textarea
            value={dados.riscosIniciais}
            onChange={(e) => handleChange('riscosIniciais', e.target.value)}
            placeholder='Ex: "Mudança de prioridades institucionais."'
            rows={3}
          />
        </div>
      </div>

      <div className="artefato-footer">
        <button className="btn-exportar" onClick={handleExportar}>
          📥 Exportar Canvas
        </button>
        <p className="footer-hint">
          💡 <strong>Dica:</strong> Preencha todos os campos para ter uma visão completa do seu projeto.
        </p>
      </div>
    </div>
  );
};

export default CanvasProjetoPublico;
