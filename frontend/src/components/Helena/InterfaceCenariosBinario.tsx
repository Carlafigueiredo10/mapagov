import React, { useState } from "react";

interface InterfaceCenariosBinarioProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

const InterfaceCenariosBinario: React.FC<InterfaceCenariosBinarioProps> = ({ dados, onConfirm }) => {
  const [cenario1Descricao, setCenario1Descricao] = useState("");
  const [cenario2Descricao, setCenario2Descricao] = useState("");

  const numeroEtapa = (dados as { numero_etapa?: number })?.numero_etapa || 1;
  const antesDecisao = (dados as { antes_decisao?: string })?.antes_decisao || '';

  // Numeração hierárquica: 1.1.1, 1.1.2
  const cenario1Label = `Cenário ${numeroEtapa}.1.1`;
  const cenario2Label = `Cenário ${numeroEtapa}.1.2`;

  const handleConfirm = () => {
    if (!cenario1Descricao.trim() || !cenario2Descricao.trim()) {
      alert("Por favor, preencha a descrição dos dois cenários.");
      return;
    }

    const resposta = JSON.stringify({
      cenarios: [
        { descricao: cenario1Descricao },
        { descricao: cenario2Descricao }
      ]
    });

    onConfirm(resposta);
  };

  return (
    <div className="interface-container fade-in">
      <div className="interface-title">⚖️ Etapa {numeroEtapa} - Definir 2 Cenários</div>

      {antesDecisao && (
        <div className="contexto-section">
          <strong>📌 Antes da decisão:</strong>
          <p className="contexto-texto">"{antesDecisao}"</p>
        </div>
      )}

      <div className="instrucoes-section">
        <p>
          Defina <strong>a descrição de cada cenário</strong>. As subetapas serão detalhadas depois.
        </p>
      </div>

      {/* CENÁRIO 1 */}
      <div className="cenario-card cenario-positivo">
        <div className="cenario-header">
          <span className="cenario-icone">✅</span>
          <h3>{cenario1Label}</h3>
        </div>

        <div className="form-group">
          <label htmlFor="cenario1-desc">
            <strong>O que caracteriza este cenário?</strong>
            <span className="label-exemplo">Ex: "Documentação está completa", "Pedido aprovado"</span>
          </label>
          <input
            id="cenario1-desc"
            type="text"
            className="form-input"
            placeholder="Digite a descrição do cenário positivo..."
            value={cenario1Descricao}
            onChange={(e) => setCenario1Descricao(e.target.value)}
            maxLength={200}
          />
        </div>
      </div>

      {/* CENÁRIO 2 */}
      <div className="cenario-card cenario-negativo">
        <div className="cenario-header">
          <span className="cenario-icone">❌</span>
          <h3>{cenario2Label}</h3>
        </div>

        <div className="form-group">
          <label htmlFor="cenario2-desc">
            <strong>O que caracteriza este cenário?</strong>
            <span className="label-exemplo">Ex: "Documentação incompleta", "Pedido reprovado"</span>
          </label>
          <input
            id="cenario2-desc"
            type="text"
            className="form-input"
            placeholder="Digite a descrição do cenário negativo..."
            value={cenario2Descricao}
            onChange={(e) => setCenario2Descricao(e.target.value)}
            maxLength={200}
          />
        </div>
      </div>

      <div className="action-buttons">
        <button className="btn-interface btn-primary" onClick={handleConfirm}>
          Confirmar Cenários
        </button>
      </div>

      <style>{`
        .contexto-section {
          background: #e8f0ff;
          padding: 1rem;
          border-radius: 6px;
          border-left: 4px solid #1351B4;
          margin: 1.5rem 0;
        }

        .contexto-section strong {
          color: #1351B4;
          display: block;
          margin-bottom: 0.5rem;
        }

        .contexto-texto {
          font-size: 0.95rem;
          color: #212529;
          margin: 0;
          font-style: italic;
        }

        .instrucoes-section {
          background: #f8f9fa;
          padding: 1rem;
          border-radius: 6px;
          margin: 1.5rem 0;
          text-align: center;
        }

        .instrucoes-section p {
          margin: 0;
          font-size: 0.95rem;
          color: #495057;
          line-height: 1.6;
        }

        .instrucoes-section strong {
          color: #1351B4;
        }

        .cenario-card {
          border: 2px solid;
          border-radius: 8px;
          padding: 1.5rem;
          margin: 1.5rem 0;
        }

        .cenario-positivo {
          border-color: #28a745;
          background: linear-gradient(to right, rgba(40, 167, 69, 0.05), rgba(40, 167, 69, 0.02));
        }

        .cenario-negativo {
          border-color: #dc3545;
          background: linear-gradient(to right, rgba(220, 53, 69, 0.05), rgba(220, 53, 69, 0.02));
        }

        .cenario-header {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 1.25rem;
          padding-bottom: 1rem;
          border-bottom: 2px solid rgba(0, 0, 0, 0.1);
        }

        .cenario-icone {
          font-size: 1.75rem;
        }

        .cenario-header h3 {
          margin: 0;
          font-size: 1.1rem;
          font-weight: 600;
          color: #212529;
        }

        .form-group {
          margin-bottom: 1.25rem;
        }

        .form-group:last-child {
          margin-bottom: 0;
        }

        .form-group label {
          display: block;
          font-size: 0.95rem;
          color: #495057;
          margin-bottom: 0.5rem;
        }

        .form-group label strong {
          color: #212529;
        }

        .label-exemplo {
          display: block;
          font-size: 0.8rem;
          color: #6c757d;
          font-weight: normal;
          margin-top: 0.25rem;
        }

        .form-input {
          width: 100%;
          padding: 0.75rem;
          border: 2px solid #dee2e6;
          border-radius: 6px;
          font-size: 0.95rem;
          transition: border-color 0.2s;
        }

        .form-input:focus {
          outline: none;
          border-color: #1351B4;
        }

        .form-input::placeholder {
          color: #adb5bd;
        }

        .action-buttons {
          display: flex;
          gap: 1rem;
          margin-top: 2rem;
        }

        .btn-interface {
          flex: 1;
          padding: 0.85rem 1.5rem;
          border: none;
          border-radius: 6px;
          font-weight: 500;
          font-size: 1rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-primary {
          background: #007bff;
          color: white;
        }

        .btn-primary:hover {
          background: #0056b3;
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
        }
      `}</style>
    </div>
  );
};

export default InterfaceCenariosBinario;
