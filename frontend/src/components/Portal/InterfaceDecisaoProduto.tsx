import { useState } from 'react';

interface Produto {
  key: string;
  nome: string;
  descricao_curta: string;
}

interface InterfaceDecisaoProdutoProps {
  dados: {
    produtos: Produto[];
    permite_texto: boolean;
    estado: string;
  };
  onConfirm: (produtoKey: string) => void;
}

export default function InterfaceDecisaoProduto({ dados, onConfirm }: InterfaceDecisaoProdutoProps) {
  const [selecionado, setSelecionado] = useState<string | null>(null);

  const { produtos, estado } = dados;
  const mostrarAindaNaoSei = estado === 'DECISAO_OBRIGATORIA';

  const handleConfirm = () => {
    if (!selecionado) return;
    onConfirm(selecionado);
  };

  return (
    <div className="decisao-produto-container">
      <fieldset className="decisao-fieldset">
        <legend className="decisao-legend">
          Selecione o tipo de trabalho que você precisa realizar:
        </legend>

        <div className="decisao-opcoes">
          {produtos.map((produto) => (
            <label
              key={produto.key}
              className={`decisao-card ${selecionado === produto.key ? 'selected' : ''}`}
            >
              <input
                type="radio"
                name="produto"
                value={produto.key}
                checked={selecionado === produto.key}
                onChange={() => setSelecionado(produto.key)}
                className="decisao-radio"
              />
              <div className="decisao-card-content">
                <strong className="decisao-card-nome">{produto.nome}</strong>
                <span className="decisao-card-desc">{produto.descricao_curta}</span>
              </div>
            </label>
          ))}

          {mostrarAindaNaoSei && (
            <label
              className={`decisao-card decisao-card-secundario ${selecionado === 'ainda_nao_sei' ? 'selected' : ''}`}
            >
              <input
                type="radio"
                name="produto"
                value="ainda_nao_sei"
                checked={selecionado === 'ainda_nao_sei'}
                onChange={() => setSelecionado('ainda_nao_sei')}
                className="decisao-radio"
              />
              <div className="decisao-card-content">
                <strong className="decisao-card-nome">Ainda não sei</strong>
                <span className="decisao-card-desc">
                  Veja uma comparação entre os produtos disponíveis.
                </span>
              </div>
            </label>
          )}
        </div>

        <button
          className="decisao-btn-iniciar"
          onClick={handleConfirm}
          disabled={!selecionado}
          type="button"
        >
          {selecionado === 'ainda_nao_sei' ? 'Ver comparação' : 'Iniciar'}
        </button>
      </fieldset>

      <style>{`
        .decisao-produto-container {
          margin-top: 12px;
          animation: decisaoFadeIn 0.4s ease;
        }

        @keyframes decisaoFadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .decisao-fieldset {
          border: none;
          padding: 0;
          margin: 0;
        }

        .decisao-legend {
          font-size: 14px;
          font-weight: 600;
          color: #495057;
          margin-bottom: 12px;
          padding: 0;
        }

        .decisao-opcoes {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .decisao-card {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          padding: 14px 16px;
          background: white;
          border: 2px solid #dee2e6;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .decisao-card:hover {
          border-color: #1351B4;
          box-shadow: 0 2px 8px rgba(19, 81, 180, 0.12);
        }

        .decisao-card:focus-within {
          outline: 2px solid #1351B4;
          outline-offset: 2px;
        }

        .decisao-card.selected {
          border-color: #1351B4;
          background: #e8f0ff;
        }

        .decisao-card-secundario {
          border-style: dashed;
        }

        .decisao-radio {
          margin-top: 2px;
          accent-color: #1351B4;
          flex-shrink: 0;
          width: 18px;
          height: 18px;
        }

        .decisao-card-content {
          display: flex;
          flex-direction: column;
          gap: 2px;
          min-width: 0;
        }

        .decisao-card-nome {
          font-size: 14px;
          color: #1B4F72;
        }

        .decisao-card-desc {
          font-size: 12px;
          color: #718096;
          line-height: 1.4;
        }

        .decisao-btn-iniciar {
          margin-top: 14px;
          padding: 10px 28px;
          background: #1351B4;
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
          width: 100%;
        }

        .decisao-btn-iniciar:hover:not(:disabled) {
          background: #0C4191;
          box-shadow: 0 4px 12px rgba(19, 81, 180, 0.3);
        }

        .decisao-btn-iniciar:focus-visible {
          outline: 2px solid #1351B4;
          outline-offset: 2px;
        }

        .decisao-btn-iniciar:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }

        @media (max-width: 768px) {
          .decisao-card {
            padding: 12px;
          }
        }
      `}</style>
    </div>
  );
}
