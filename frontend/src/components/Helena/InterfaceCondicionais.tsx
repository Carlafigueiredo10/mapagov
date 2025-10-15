import React, { useState } from "react";

interface InterfaceCondicionaisProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

const InterfaceCondicionais: React.FC<InterfaceCondicionaisProps> = ({ dados, onConfirm }) => {
  const [respostaSelecionada, setRespostaSelecionada] = useState<string>("");

  const numeroEtapa = (dados as { numero_etapa?: number })?.numero_etapa || 1;

  const handleResposta = (resposta: string) => {
    setRespostaSelecionada(resposta);
  };

  const handleConfirm = () => {
    if (!respostaSelecionada) {
      alert("Por favor, selecione uma opção.");
      return;
    }
    onConfirm(respostaSelecionada);
  };

  return (
    <div className="interface-container fade-in">
      <div className="interface-title">🔀 Etapa {numeroEtapa} - Decisões Condicionais</div>

      <div className="pergunta-section">
        <p className="pergunta-texto">
          Esta etapa envolve uma <strong>decisão que leva a caminhos diferentes</strong>?
        </p>
        <p className="pergunta-explicacao">
          Por exemplo: "Verificar se documentação está completa" pode ter dois caminhos:
          <br />• <strong>SIM (completa)</strong> → Prosseguir para análise
          <br />• <strong>NÃO (incompleta)</strong> → Solicitar complementação
        </p>
      </div>

      <div className="opcoes-condicionais">
        <div
          className={`opcao-card ${respostaSelecionada === 'sim' ? 'selected' : ''}`}
          onClick={() => handleResposta('sim')}
        >
          <input
            type="radio"
            name="condicional"
            value="sim"
            checked={respostaSelecionada === 'sim'}
            readOnly
          />
          <div className="opcao-conteudo">
            <div className="opcao-titulo">✅ SIM, tem decisões</div>
            <div className="opcao-descricao">
              Esta etapa tem um ponto de decisão com caminhos diferentes (sim/não, aprovado/reprovado, etc.)
            </div>
          </div>
        </div>

        <div
          className={`opcao-card ${respostaSelecionada === 'não' ? 'selected' : ''}`}
          onClick={() => handleResposta('não')}
        >
          <input
            type="radio"
            name="condicional"
            value="não"
            checked={respostaSelecionada === 'não'}
            readOnly
          />
          <div className="opcao-conteudo">
            <div className="opcao-titulo">➡️ NÃO, é linear</div>
            <div className="opcao-descricao">
              Esta etapa segue sempre o mesmo fluxo, sem decisões ou caminhos alternativos
            </div>
          </div>
        </div>
      </div>

      <div className="action-buttons">
        <button
          className="btn-interface btn-help"
          onClick={() => onConfirm('ajuda')}
        >
          ❓ Preciso de Ajuda
        </button>
        <button className="btn-interface btn-primary" onClick={handleConfirm}>
          Confirmar
        </button>
      </div>

      <style>{`
        .pergunta-section {
          margin: 1.5rem 0;
          padding: 1.25rem;
          background: #f8f9fa;
          border-left: 4px solid #1351B4;
          border-radius: 6px;
        }

        .pergunta-texto {
          font-size: 1.1rem;
          color: #212529;
          margin-bottom: 1rem;
          line-height: 1.5;
        }

        .pergunta-texto strong {
          color: #1351B4;
        }

        .pergunta-explicacao {
          font-size: 0.9rem;
          color: #6c757d;
          margin: 0;
          line-height: 1.6;
        }

        .opcoes-condicionais {
          display: flex;
          flex-direction: column;
          gap: 1rem;
          margin: 2rem 0;
        }

        .opcao-card {
          display: flex;
          align-items: flex-start;
          gap: 1rem;
          padding: 1.25rem;
          background: white;
          border: 2px solid #dee2e6;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .opcao-card:hover {
          border-color: #1351B4;
          box-shadow: 0 2px 8px rgba(19, 81, 180, 0.15);
          transform: translateY(-2px);
        }

        .opcao-card.selected {
          border-color: #1351B4;
          background: #e8f0ff;
        }

        .opcao-card input[type="radio"] {
          margin-top: 0.25rem;
          cursor: pointer;
          width: 20px;
          height: 20px;
          flex-shrink: 0;
        }

        .opcao-conteudo {
          flex: 1;
        }

        .opcao-titulo {
          font-size: 1.05rem;
          font-weight: 600;
          color: #212529;
          margin-bottom: 0.5rem;
        }

        .opcao-card.selected .opcao-titulo {
          color: #1351B4;
        }

        .opcao-descricao {
          font-size: 0.9rem;
          color: #6c757d;
          line-height: 1.5;
        }

        .action-buttons {
          display: flex;
          gap: 1rem;
          margin-top: 1.5rem;
        }

        .btn-interface {
          flex: 1;
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 6px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-primary {
          background: #007bff;
          color: white;
        }

        .btn-primary:hover {
          background: #0056b3;
        }

        .btn-help {
          background: #ffc107;
          color: #212529;
        }

        .btn-help:hover {
          background: #e0a800;
        }
      `}</style>
    </div>
  );
};

export default InterfaceCondicionais;