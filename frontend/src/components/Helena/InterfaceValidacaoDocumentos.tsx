import React, { useState } from "react";

interface InterfaceValidacaoDocumentosProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

interface Opcao {
  id: string;
  label: string;
}

const InterfaceValidacaoDocumentos: React.FC<InterfaceValidacaoDocumentosProps> = ({ dados, onConfirm }) => {
  const [opcaoSelecionada, setOpcaoSelecionada] = useState<string>("");

  const numeroEtapa = (dados as { numero_etapa?: number })?.numero_etapa || 1;
  const textoMencao = (dados as { texto_mencao?: string })?.texto_mencao || '';
  const opcoes = (dados as { opcoes?: Opcao[] })?.opcoes || [
    { id: "sim", label: "Sim, já está listada" },
    { id: "adicionar", label: "Não, quero adicionar agora" },
    { id: "pular", label: "Pular validação" }
  ];

  const handleConfirm = () => {
    if (!opcaoSelecionada) {
      alert("Por favor, selecione uma opção.");
      return;
    }
    onConfirm(opcaoSelecionada);
  };

  return (
    <div className="interface-container fade-in">
      <div className="interface-title">📄 Etapa {numeroEtapa} - Validação de Documentos</div>

      <div className="mencao-section">
        <div className="mencao-header">
          <span className="icone-mencao">📌</span>
          <h3>Você mencionou documentação:</h3>
        </div>
        <div className="mencao-conteudo">
          "{textoMencao}"
        </div>
      </div>

      <div className="pergunta-section">
        <p className="pergunta-texto">
          Essa documentação <strong>já está listada</strong> na seção "Documentos Necessários"?
        </p>
        <p className="pergunta-explicacao">
          Queremos evitar duplicatas e garantir que todos os documentos estão organizados.
        </p>
      </div>

      <div className="opcoes-validacao">
        {opcoes.map((opcao) => (
          <div
            key={opcao.id}
            className={`opcao-card ${opcaoSelecionada === opcao.id ? 'selected' : ''}`}
            onClick={() => setOpcaoSelecionada(opcao.id)}
          >
            <input
              type="radio"
              name="validacao_doc"
              value={opcao.id}
              checked={opcaoSelecionada === opcao.id}
              readOnly
            />
            <div className="opcao-conteudo">
              <div className="opcao-icone">
                {opcao.id === 'sim' && '✅'}
                {opcao.id === 'adicionar' && '➕'}
                {opcao.id === 'pular' && '⏭️'}
              </div>
              <div className="opcao-texto">
                <div className="opcao-titulo">{opcao.label}</div>
                {opcao.id === 'sim' && (
                  <div className="opcao-descricao">
                    Este documento já foi adicionado anteriormente
                  </div>
                )}
                {opcao.id === 'adicionar' && (
                  <div className="opcao-descricao">
                    Abrir interface para adicionar este documento à lista
                  </div>
                )}
                {opcao.id === 'pular' && (
                  <div className="opcao-descricao">
                    Continuar sem validar agora (pode adicionar depois)
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="dica-section">
        <strong>💡 Dica:</strong> Manter os documentos organizados facilita a revisão final
        e evita confusão no mapeamento do processo.
      </div>

      <div className="action-buttons">
        <button className="btn-interface btn-primary" onClick={handleConfirm}>
          Confirmar
        </button>
      </div>

      <style>{`
        .mencao-section {
          margin: 1.5rem 0;
          padding: 1.25rem;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 8px;
          color: white;
        }

        .mencao-header {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 1rem;
        }

        .icone-mencao {
          font-size: 1.5rem;
        }

        .mencao-header h3 {
          margin: 0;
          font-size: 1rem;
          font-weight: 600;
        }

        .mencao-conteudo {
          background: rgba(255, 255, 255, 0.2);
          padding: 1rem;
          border-radius: 6px;
          font-size: 1.05rem;
          line-height: 1.6;
          border-left: 4px solid rgba(255, 255, 255, 0.5);
          font-style: italic;
        }

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

        .opcoes-validacao {
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
          font-size: 1.75rem;
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

        .dica-section {
          background: #fff3cd;
          padding: 1rem;
          border-radius: 6px;
          border-left: 4px solid #ffc107;
          font-size: 0.9rem;
          color: #856404;
          line-height: 1.6;
        }

        .dica-section strong {
          color: #856404;
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

export default InterfaceValidacaoDocumentos;
