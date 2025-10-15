import React, { useState, useMemo } from "react";

interface InterfaceOperadoresProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

const InterfaceOperadores: React.FC<InterfaceOperadoresProps> = ({ dados, onConfirm }) => {
  const [operadoresSelecionados, setOperadoresSelecionados] = useState<string[]>([]);

  // Extrair lista de operadores do backend
  const listaOperadores = useMemo(() => {
    const opcoes = (dados as { opcoes?: string[] })?.opcoes;
    if (opcoes && Array.isArray(opcoes)) {
      return opcoes;
    }
    console.warn("InterfaceOperadores: opcoes ausentes ou inválidas");
    return [];
  }, [dados]);

  const toggleOperador = (operador: string) => {
    setOperadoresSelecionados(prev =>
      prev.includes(operador)
        ? prev.filter(o => o !== operador)
        : [...prev, operador]
    );
  };

  const selecionarTodos = () => {
    if (operadoresSelecionados.length === listaOperadores.length) {
      // Desselecionar todos
      setOperadoresSelecionados([]);
    } else {
      // Selecionar todos
      setOperadoresSelecionados([...listaOperadores]);
    }
  };

  const handleConfirm = () => {
    const resposta = operadoresSelecionados.length > 0
      ? operadoresSelecionados.join(', ')
      : 'nenhum';
    onConfirm(resposta);
  };

  return (
    <div className="interface-container fade-in">
      <div className="interface-title">👥 Quem são os responsáveis?</div>

      {listaOperadores.length > 0 ? (
        <>
          <div className="selecao-info">
            <span className="contador-selecao">
              {operadoresSelecionados.length} de {listaOperadores.length} selecionados
            </span>
            <button
              className="btn-selecionar-todos"
              onClick={selecionarTodos}
              type="button"
            >
              {operadoresSelecionados.length === listaOperadores.length
                ? 'Desmarcar Todos'
                : 'Selecionar Todos'}
            </button>
          </div>

          <div className="operadores-grid">
            {listaOperadores.map((operador, idx) => (
              <div
                key={idx}
                className={`operador-card ${operadoresSelecionados.includes(operador) ? 'selected' : ''}`}
                onClick={() => toggleOperador(operador)}
              >
                <input
                  type="checkbox"
                  readOnly
                  checked={operadoresSelecionados.includes(operador)}
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
        <button className="btn-interface btn-secondary" onClick={() => onConfirm('nao sei')}>
          Não Sei
        </button>
        <button className="btn-interface btn-primary" onClick={handleConfirm}>
          Confirmar
        </button>
      </div>

      <style>{`
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

        .btn-selecionar-todos {
          padding: 0.5rem 1rem;
          background: #17a2b8;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 0.85rem;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.2s;
        }

        .btn-selecionar-todos:hover {
          background: #138496;
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

        .operador-card input[type="checkbox"] {
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

        .btn-secondary {
          background: #6c757d;
          color: white;
        }

        .btn-secondary:hover {
          background: #5a6268;
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

export default InterfaceOperadores;