import React from "react";

interface InterfaceCondicionaisAjudaProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

const InterfaceCondicionaisAjuda: React.FC<InterfaceCondicionaisAjudaProps> = ({ dados, onConfirm }) => {
  const numeroEtapa = (dados as { numero_etapa?: number })?.numero_etapa || 1;
  const descricaoEtapa = (dados as { descricao_etapa?: string })?.descricao_etapa || '';

  return (
    <div className="interface-container fade-in">
      <div className="interface-title">💡 Ajuda - Decisões Condicionais</div>

      <div className="ajuda-section">
        <div className="ajuda-header">
          <span className="icone-ajuda">🔀</span>
          <h3>O que são decisões condicionais?</h3>
        </div>

        <div className="ajuda-conteudo">
          <p>
            <strong>Decisões condicionais</strong> são pontos no processo onde você precisa avaliar
            algo e seguir caminhos diferentes dependendo do resultado.
          </p>

          <div className="exemplos-section">
            <h4>📋 Exemplos práticos:</h4>
            <ul>
              <li>
                <strong>Análise de documentação:</strong>
                <br />
                • <em>Completa</em> → Prosseguir para análise
                <br />
                • <em>Incompleta</em> → Solicitar complementação
              </li>
              <li>
                <strong>Verificar valor:</strong>
                <br />
                • <em>Aprovação automática</em> (valor baixo)
                <br />
                • <em>Análise manual</em> (valor alto)
              </li>
              <li>
                <strong>Conferir elegibilidade:</strong>
                <br />
                • <em>Apto</em> → Continuar processo
                <br />
                • <em>Inapto</em> → Indeferir pedido
              </li>
            </ul>
          </div>

          {descricaoEtapa && (
            <div className="contexto-etapa">
              <h4>📌 Sobre a etapa atual:</h4>
              <p className="descricao-etapa">
                <strong>Etapa {numeroEtapa}:</strong> {descricaoEtapa}
              </p>
              <p className="pergunta-destaque">
                Esta etapa tem esse tipo de decisão/condição?
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="action-buttons">
        <button
          className="btn-interface btn-primary"
          onClick={() => onConfirm('entendi')}
        >
          ✓ Entendi, continuar
        </button>
      </div>

      <style>{`
        .ajuda-section {
          margin: 1.5rem 0;
          padding: 1.5rem;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 12px;
          color: white;
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }

        .ajuda-header {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 1.25rem;
          padding-bottom: 1rem;
          border-bottom: 2px solid rgba(255, 255, 255, 0.2);
        }

        .icone-ajuda {
          font-size: 2rem;
        }

        .ajuda-header h3 {
          margin: 0;
          font-size: 1.3rem;
          font-weight: 600;
        }

        .ajuda-conteudo {
          font-size: 1rem;
          line-height: 1.6;
        }

        .ajuda-conteudo p {
          margin-bottom: 1.25rem;
        }

        .ajuda-conteudo strong {
          font-weight: 600;
          color: #fff;
        }

        .exemplos-section {
          background: rgba(255, 255, 255, 0.15);
          padding: 1.25rem;
          border-radius: 8px;
          margin: 1.5rem 0;
          border-left: 4px solid rgba(255, 255, 255, 0.5);
        }

        .exemplos-section h4 {
          margin: 0 0 1rem 0;
          font-size: 1.1rem;
          font-weight: 600;
        }

        .exemplos-section ul {
          list-style: none;
          padding: 0;
          margin: 0;
        }

        .exemplos-section li {
          margin-bottom: 1.25rem;
          padding-left: 1rem;
        }

        .exemplos-section li:last-child {
          margin-bottom: 0;
        }

        .exemplos-section em {
          color: #ffd700;
          font-style: normal;
          font-weight: 500;
        }

        .contexto-etapa {
          background: rgba(255, 255, 255, 0.2);
          padding: 1.25rem;
          border-radius: 8px;
          margin-top: 1.5rem;
        }

        .contexto-etapa h4 {
          margin: 0 0 1rem 0;
          font-size: 1.1rem;
          font-weight: 600;
        }

        .descricao-etapa {
          background: rgba(255, 255, 255, 0.15);
          padding: 0.75rem;
          border-radius: 6px;
          margin-bottom: 1rem;
          font-size: 0.95rem;
        }

        .pergunta-destaque {
          font-size: 1.05rem;
          font-weight: 600;
          color: #ffd700;
          margin: 0;
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
          font-size: 1rem;
        }

        .btn-primary {
          background: #28a745;
          color: white;
        }

        .btn-primary:hover {
          background: #218838;
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
        }
      `}</style>
    </div>
  );
};

export default InterfaceCondicionaisAjuda;
