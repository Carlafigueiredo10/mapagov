import React, { useState, useMemo } from "react";

interface InterfaceOperadoresEtapaProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

const InterfaceOperadoresEtapa: React.FC<InterfaceOperadoresEtapaProps> = ({ dados, onConfirm }) => {
  const [operadorSelecionado, setOperadorSelecionado] = useState<string>("");

  // Extrair dados do backend
  const numeroEtapa = (dados as { numero_etapa?: number })?.numero_etapa || 1;
  const listaOperadores = useMemo(() => {
    const opcoes = (dados as { opcoes?: string[] })?.opcoes;
    if (opcoes && Array.isArray(opcoes)) {
      return opcoes;
    }
    console.warn("InterfaceOperadoresEtapa: opcoes ausentes ou inválidas");
    return [];
  }, [dados]);

  const selecionarOperador = (operador: string) => {
    setOperadorSelecionado(operador);
  };

  const handleConfirm = () => {
    if (!operadorSelecionado) {
      alert("Por favor, selecione um operador para esta etapa.");
      return;
    }
    onConfirm(operadorSelecionado);
  };

  return (
    <div className="interface-container fade-in">
      <div className="interface-title">👤 Quem realiza a Etapa {numeroEtapa}?</div>
      <p className="interface-subtitle">
        Selecione apenas UM responsável por executar esta etapa:
      </p>

      {listaOperadores.length > 0 ? (
        <>
          <div className="selecao-info">
            <span className="contador-selecao">
              {operadorSelecionado ? '1 operador selecionado' : 'Nenhum operador selecionado'}
            </span>
          </div>

          <div className="operadores-grid">
            {listaOperadores.map((operador, idx) => (
              <div
                key={idx}
                className={`operador-card ${operadorSelecionado === operador ? 'selected' : ''}`}
                onClick={() => selecionarOperador(operador)}
              >
                <input
                  type="radio"
                  name="operador-etapa"
                  readOnly
                  checked={operadorSelecionado === operador}
                />
                <label>{operador}</label>
              </div>
            ))}
          </div>
        </>
      ) : (
        <div className="aviso-sem-dados">
          <p>Nenhum operador disponível para seleção.</p>
        </div>
      )}

      <div className="action-buttons">
        <button className="btn-interface btn-primary" onClick={handleConfirm}>
          Confirmar
        </button>
      </div>

      <style>{`
        .interface-subtitle {
          margin: 0.5rem 0 1.5rem 0;
          color: #6c757d;
          font-size: 0.95rem;
        }

        .selecao-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
          padding: 0.75rem;
          background: #f8f9fa;
          border-radius: 6px;
        }

        .contador-selecao {
          font-size: 0.9rem;
          color: #495057;
          font-weight: 500;
        }

        .operadores-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          gap: 0.75rem;
          margin: 1.5rem 0;
        }

        .operador-card {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 1rem;
          background: white;
          border: 2px solid #dee2e6;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .operador-card:hover {
          border-color: #1351B4;
          box-shadow: 0 2px 8px rgba(19, 81, 180, 0.1);
          transform: translateY(-2px);
        }

        .operador-card.selected {
          border-color: #1351B4;
          background: #e8f0ff;
        }

        .operador-card input[type="radio"] {
          cursor: pointer;
          width: 18px;
          height: 18px;
        }

        .operador-card label {
          cursor: pointer;
          flex: 1;
          font-size: 0.95rem;
          font-weight: 500;
          color: #495057;
          margin: 0;
        }

        .operador-card.selected label {
          color: #1351B4;
        }

        .aviso-sem-dados {
          padding: 2rem;
          text-align: center;
          color: #6c757d;
          background: #f8f9fa;
          border-radius: 8px;
          margin: 1rem 0;
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
      `}</style>
    </div>
  );
};

export default InterfaceOperadoresEtapa;