import React, { useState } from "react";

interface InterfaceTipoCondicionalProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

interface Opcao {
  id: string;
  label: string;
}

const InterfaceTipoCondicional: React.FC<InterfaceTipoCondicionalProps> = ({ dados, onConfirm }) => {
  const [tipoSelecionado, setTipoSelecionado] = useState<string>("");

  const numeroEtapa = (dados as { numero_etapa?: number })?.numero_etapa || 1;
  const opcoes = (dados as { opcoes?: Opcao[] })?.opcoes || [
    { id: "binario", label: "2 cenários (Sim/Não, Aprovado/Reprovado, Completo/Incompleto, etc)" },
    { id: "multiplos", label: "Múltiplos cenários (3 ou mais opções diferentes)" }
  ];

  const handleConfirm = () => {
    if (!tipoSelecionado) {
      alert("Por favor, selecione o tipo de decisão.");
      return;
    }
    onConfirm(tipoSelecionado);
  };

  return (
    <div className="interface-container fade-in">
      <div className="interface-title">🔢 Etapa {numeroEtapa} - Tipo de Decisão</div>

      <div className="pergunta-section">
        <p className="pergunta-texto">
          <strong>Quantos cenários possíveis existem nessa decisão?</strong>
        </p>
        <p className="pergunta-explicacao">
          Isso nos ajuda a mapear todos os caminhos que o processo pode seguir.
        </p>
      </div>

      <div className="opcoes-tipo">
        {opcoes.map((opcao) => (
          <div
            key={opcao.id}
            className={`opcao-card ${tipoSelecionado === opcao.id ? 'selected' : ''}`}
            onClick={() => setTipoSelecionado(opcao.id)}
          >
            <input
              type="radio"
              name="tipo_condicional"
              value={opcao.id}
              checked={tipoSelecionado === opcao.id}
              readOnly
            />
            <div className="opcao-conteudo">
              <div className="opcao-icone">
                {opcao.id === 'binario' ? '⚖️' : '🔀'}
              </div>
              <div className="opcao-texto">
                <div className="opcao-titulo">
                  {opcao.id === 'binario' ? '2 Cenários' : 'Múltiplos Cenários'}
                </div>
                <div className="opcao-descricao">{opcao.label}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="exemplos-rapidos">
        <h4>💡 Exemplos rápidos:</h4>
        <div className="exemplo-item">
          <span className="exemplo-badge binario">2 cenários</span>
          <span className="exemplo-texto">
            Documento completo/incompleto • Aprovado/Reprovado • Dentro/Fora do prazo
          </span>
        </div>
        <div className="exemplo-item">
          <span className="exemplo-badge multiplos">Múltiplos</span>
          <span className="exemplo-texto">
            Prioridade (Baixa/Média/Alta/Urgente) • Status (Pendente/Em análise/Aprovado/Rejeitado)
          </span>
        </div>
      </div>

      <div className="action-buttons">
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
          margin-bottom: 0.75rem;
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

        .opcoes-tipo {
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
          margin-top: 0.5rem;
          cursor: pointer;
          width: 20px;
          height: 20px;
          flex-shrink: 0;
        }

        .opcao-conteudo {
          display: flex;
          align-items: center;
          gap: 1rem;
          flex: 1;
        }

        .opcao-icone {
          font-size: 2rem;
          flex-shrink: 0;
        }

        .opcao-texto {
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

        .exemplos-rapidos {
          background: #fff3cd;
          padding: 1.25rem;
          border-radius: 8px;
          border-left: 4px solid #ffc107;
          margin: 1.5rem 0;
        }

        .exemplos-rapidos h4 {
          margin: 0 0 1rem 0;
          font-size: 1rem;
          font-weight: 600;
          color: #856404;
        }

        .exemplo-item {
          display: flex;
          align-items: flex-start;
          gap: 0.75rem;
          margin-bottom: 0.75rem;
        }

        .exemplo-item:last-child {
          margin-bottom: 0;
        }

        .exemplo-badge {
          display: inline-block;
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
          white-space: nowrap;
          flex-shrink: 0;
        }

        .exemplo-badge.binario {
          background: #d1ecf1;
          color: #0c5460;
        }

        .exemplo-badge.multiplos {
          background: #d4edda;
          color: #155724;
        }

        .exemplo-texto {
          font-size: 0.85rem;
          color: #856404;
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
      `}</style>
    </div>
  );
};

export default InterfaceTipoCondicional;
