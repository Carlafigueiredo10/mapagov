import React, { useState } from "react";

interface InterfaceCenariosMultiplosQuantidadeProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

interface Cenario {
  descricao: string;
}

const InterfaceCenariosMultiplosQuantidade: React.FC<InterfaceCenariosMultiplosQuantidadeProps> = ({ dados, onConfirm }) => {
  const numeroEtapa = (dados as { numero_etapa?: number })?.numero_etapa || 1;
  const antesDecisao = (dados as { antes_decisao?: string })?.antes_decisao || '';
  const quantidadeCenarios = (dados as { quantidade?: number })?.quantidade || 3;

  // Inicializar array de cenários vazios
  const [cenarios, setCenarios] = useState<Cenario[]>(
    Array(quantidadeCenarios).fill(null).map(() => ({ descricao: "" }))
  );

  const handleDescricaoChange = (index: number, descricao: string) => {
    const novosCenarios = [...cenarios];
    novosCenarios[index].descricao = descricao;
    setCenarios(novosCenarios);
  };

  const handleConfirm = () => {
    // Validar que todos os cenários têm descrição
    const cenariosVazios = cenarios.filter(c => !c.descricao.trim());
    if (cenariosVazios.length > 0) {
      alert(`Por favor, preencha a descrição de todos os ${quantidadeCenarios} cenários.`);
      return;
    }

    const resposta = JSON.stringify({
      cenarios: cenarios.map(c => ({ descricao: c.descricao }))
    });

    onConfirm(resposta);
  };

  return (
    <div className="interface-container fade-in">
      <div className="interface-title">🔀 Etapa {numeroEtapa} - Definir {quantidadeCenarios} Cenários</div>

      {antesDecisao && (
        <div className="contexto-section">
          <strong>📌 Antes da decisão:</strong>
          <p className="contexto-texto">"{antesDecisao}"</p>
        </div>
      )}

      <div className="instrucoes-section">
        <p>
          Defina <strong>a descrição de cada um dos {quantidadeCenarios} cenários possíveis</strong>.
          As subetapas serão detalhadas depois.
        </p>
      </div>

      {/* Lista de Cenários */}
      <div className="cenarios-lista">
        {cenarios.map((cenario, index) => (
          <div key={index} className="cenario-card">
            <div className="cenario-header">
              <span className="cenario-numero">{index + 1}</span>
              <h3>Cenário {index + 1}</h3>
            </div>

            <div className="form-group">
              <label htmlFor={`cenario-${index}-desc`}>
                <strong>Descrição do cenário:</strong>
                <span className="label-exemplo">
                  Ex: "Valor acima do limite", "Servidor temporário", "Documentação digital"
                </span>
              </label>
              <input
                id={`cenario-${index}-desc`}
                type="text"
                className="form-input"
                placeholder={`Digite a descrição do cenário ${index + 1}...`}
                value={cenario.descricao}
                onChange={(e) => handleDescricaoChange(index, e.target.value)}
                maxLength={200}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="action-buttons">
        <button className="btn-interface btn-primary" onClick={handleConfirm}>
          Confirmar {quantidadeCenarios} Cenários
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

        .cenarios-lista {
          margin: 1.5rem 0;
          display: flex;
          flex-direction: column;
          gap: 1.25rem;
        }

        .cenario-card {
          border: 2px solid #1351B4;
          border-radius: 8px;
          padding: 1.5rem;
          background: linear-gradient(to right, rgba(19, 81, 180, 0.05), rgba(19, 81, 180, 0.02));
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .cenario-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(19, 81, 180, 0.15);
        }

        .cenario-header {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 1.25rem;
          padding-bottom: 1rem;
          border-bottom: 2px solid rgba(19, 81, 180, 0.2);
        }

        .cenario-numero {
          background: #1351B4;
          color: white;
          width: 2rem;
          height: 2rem;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          font-size: 1rem;
        }

        .cenario-header h3 {
          margin: 0;
          font-size: 1.1rem;
          font-weight: 600;
          color: #212529;
        }

        .form-group {
          margin: 0;
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

export default InterfaceCenariosMultiplosQuantidade;
