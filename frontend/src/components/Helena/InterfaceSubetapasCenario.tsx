import React, { useState } from "react";

interface InterfaceSubetapasCenarioProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

interface Subetapa {
  id: string;
  descricao: string;
}

const InterfaceSubetapasCenario: React.FC<InterfaceSubetapasCenarioProps> = ({ dados, onConfirm }) => {
  const [subetapas, setSubetapas] = useState<Subetapa[]>([
    { id: crypto.randomUUID(), descricao: "" }
  ]);

  // Dados do cenário atual vindos do backend
  const numeroCenario = (dados as { numero_cenario?: string })?.numero_cenario || "1.1.1";
  const descricaoCenario = (dados as { descricao_cenario?: string })?.descricao_cenario || "";
  const todosOsCenarios = (dados as { todos_cenarios?: Array<{ numero: string; descricao: string }> })?.todos_cenarios || [];
  const cenarioAtualIndex = (dados as { cenario_atual_index?: number })?.cenario_atual_index || 0;

  const handleAddSubetapa = () => {
    setSubetapas([...subetapas, { id: crypto.randomUUID(), descricao: "" }]);
  };

  const handleRemoveSubetapa = (id: string) => {
    if (subetapas.length > 1) {
      setSubetapas(subetapas.filter(sub => sub.id !== id));
    }
  };

  const handleChangeSubetapa = (id: string, valor: string) => {
    setSubetapas(subetapas.map(sub =>
      sub.id === id ? { ...sub, descricao: valor } : sub
    ));
  };

  const handlePular = () => {
    // Enviar array vazio ou mensagem "pular"
    onConfirm("pular");
  };

  const handleConfirm = () => {
    // Filtrar subetapas vazias
    const subetapasPreenchidas = subetapas
      .map(s => s.descricao.trim())
      .filter(desc => desc.length > 0);

    if (subetapasPreenchidas.length === 0) {
      alert("Por favor, preencha pelo menos uma subetapa ou clique em 'Pular'.");
      return;
    }

    // Enviar como texto separado por quebra de linha (formato esperado pelo backend)
    const resposta = subetapasPreenchidas.join('\n');
    onConfirm(resposta);
  };

  return (
    <div className="interface-container fade-in">
      <div className="interface-title">📋 Detalhando Cenário {numeroCenario}</div>

      {/* Lista de TODOS os cenários */}
      {todosOsCenarios.length > 0 && (
        <div className="todos-cenarios-section">
          <strong>✅ Cenários registrados:</strong>
          <ul className="lista-cenarios">
            {todosOsCenarios.map((cen, idx) => (
              <li key={idx} className={idx === cenarioAtualIndex ? 'cenario-atual' : ''}>
                <span className="numero-cenario">Cenário {cen.numero}:</span> {cen.descricao}
                {idx === cenarioAtualIndex && <span className="badge-atual">← Detalhando agora</span>}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Contexto do cenário atual */}
      <div className="contexto-cenario">
        <strong>📌 Cenário {numeroCenario}:</strong>
        <p className="descricao-cenario">"{descricaoCenario}"</p>
      </div>

      <div className="instrucoes">
        <p>
          O que acontece quando você está neste cenário?<br />
          Qual a <strong>PRIMEIRA</strong> coisa que você faz?
        </p>
        <p className="exemplo">
          Ex: "Abro o SEI", "Faço despacho de deferimento", "Verifico o sistema"
        </p>
      </div>

      <div className="separador">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</div>

      {/* Campos dinâmicos de subetapas */}
      <div className="subetapas-container">
        {subetapas.map((subetapa, index) => (
          <div key={subetapa.id} className="subetapa-row">
            <div className="subetapa-numero">{numeroCenario}.{index + 1}</div>
            <input
              type="text"
              className="subetapa-input"
              placeholder={`Ex: Abrir SEI, Fazer despacho, Inserir dados no SIAPE...`}
              value={subetapa.descricao}
              onChange={(e) => handleChangeSubetapa(subetapa.id, e.target.value)}
              maxLength={300}
            />
            {subetapas.length > 1 && (
              <button
                className="btn-remove"
                onClick={() => handleRemoveSubetapa(subetapa.id)}
                title="Remover subetapa"
              >
                ✕
              </button>
            )}
          </div>
        ))}

        <button className="btn-add-subetapa" onClick={handleAddSubetapa}>
          ➕ Nova Subetapa
        </button>
      </div>

      <div className="action-buttons">
        <button className="btn-interface btn-secondary" onClick={handlePular}>
          Pular (sem subetapas)
        </button>
        <button className="btn-interface btn-primary" onClick={handleConfirm}>
          Confirmar e Avançar
        </button>
      </div>

      <style>{`
        .todos-cenarios-section {
          background: #e8f4e8;
          padding: 1rem;
          border-radius: 6px;
          border-left: 4px solid #28a745;
          margin: 1.5rem 0;
        }

        .todos-cenarios-section strong {
          color: #28a745;
          display: block;
          margin-bottom: 0.75rem;
        }

        .lista-cenarios {
          list-style: none;
          padding: 0;
          margin: 0;
        }

        .lista-cenarios li {
          padding: 0.5rem;
          margin: 0.5rem 0;
          border-radius: 4px;
          background: white;
          border: 1px solid #d1e7dd;
          font-size: 0.9rem;
          line-height: 1.6;
        }

        .lista-cenarios li.cenario-atual {
          border: 2px solid #1351B4;
          background: #e8f0ff;
          font-weight: 500;
        }

        .numero-cenario {
          font-weight: 600;
          color: #1351B4;
        }

        .badge-atual {
          margin-left: 0.5rem;
          padding: 0.15rem 0.5rem;
          background: #1351B4;
          color: white;
          border-radius: 12px;
          font-size: 0.75rem;
          font-weight: 500;
        }

        .contexto-cenario {
          background: #fff3cd;
          padding: 1rem;
          border-radius: 6px;
          border-left: 4px solid #ffc107;
          margin: 1.5rem 0;
        }

        .contexto-cenario strong {
          color: #856404;
          display: block;
          margin-bottom: 0.5rem;
        }

        .descricao-cenario {
          margin: 0;
          font-size: 0.95rem;
          color: #212529;
          font-style: italic;
        }

        .instrucoes {
          background: #f8f9fa;
          padding: 1rem;
          border-radius: 6px;
          margin: 1.5rem 0;
          text-align: center;
        }

        .instrucoes p {
          margin: 0.5rem 0;
          font-size: 0.95rem;
          color: #495057;
          line-height: 1.6;
        }

        .instrucoes strong {
          color: #1351B4;
          font-weight: 600;
        }

        .exemplo {
          font-size: 0.85rem !important;
          color: #6c757d !important;
          font-style: italic;
        }

        .separador {
          text-align: center;
          color: #dee2e6;
          margin: 1.5rem 0;
          font-size: 0.8rem;
        }

        .subetapas-container {
          margin: 1.5rem 0;
        }

        .subetapa-row {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 1rem;
          animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .subetapa-numero {
          min-width: 70px;
          padding: 0.5rem 0.75rem;
          background: #1351B4;
          color: white;
          border-radius: 6px;
          font-weight: 600;
          font-size: 0.9rem;
          text-align: center;
        }

        .subetapa-input {
          flex: 1;
          padding: 0.75rem;
          border: 2px solid #dee2e6;
          border-radius: 6px;
          font-size: 0.95rem;
          transition: border-color 0.2s;
        }

        .subetapa-input:focus {
          outline: none;
          border-color: #1351B4;
          box-shadow: 0 0 0 3px rgba(19, 81, 180, 0.1);
        }

        .subetapa-input::placeholder {
          color: #adb5bd;
        }

        .btn-remove {
          min-width: 40px;
          height: 40px;
          border: 2px solid #dc3545;
          background: white;
          color: #dc3545;
          border-radius: 6px;
          cursor: pointer;
          font-size: 1.2rem;
          font-weight: bold;
          transition: all 0.2s;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .btn-remove:hover {
          background: #dc3545;
          color: white;
        }

        .btn-add-subetapa {
          width: 100%;
          padding: 0.75rem;
          border: 2px dashed #28a745;
          background: white;
          color: #28a745;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.95rem;
          font-weight: 500;
          transition: all 0.2s;
          margin-top: 0.5rem;
        }

        .btn-add-subetapa:hover {
          background: #28a745;
          color: white;
          border-style: solid;
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

        .btn-secondary {
          background: #6c757d;
          color: white;
        }

        .btn-secondary:hover {
          background: #5a6268;
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(108, 117, 125, 0.3);
        }
      `}</style>
    </div>
  );
};

export default InterfaceSubetapasCenario;
