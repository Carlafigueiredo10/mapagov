import React from 'react';
import { CHAT_CMD } from '../../constants/chatCommands';
import { useChatStore } from '../../store/chatStore';

interface InterfaceConfirmacaoDuplaProps {
  dados: {
    botao_confirmar?: string;
    botao_editar?: string;
    valor_confirmar?: string;
    valor_editar?: string;
    botao_terceiro?: string;
    valor_terceiro?: string;
  };
  onEnviar: (valor: string) => void;
}

const InterfaceConfirmacaoDupla: React.FC<InterfaceConfirmacaoDuplaProps> = ({ dados, onEnviar }) => {
  const isProcessing = useChatStore((s) => s.isProcessing);
  const {
    botao_confirmar = 'Confirmar ✅',
    botao_editar = 'Editar ✏️',
    valor_confirmar: valor_backend_confirmar,
    valor_editar: valor_backend_editar,
    botao_terceiro,
    valor_terceiro,
  } = dados;

  const valor_confirmar = (valor_backend_confirmar && !['CONFIRMAR', 'SEGUIR'].includes(valor_backend_confirmar))
    ? valor_backend_confirmar
    : CHAT_CMD.CONFIRMAR_DUPLA;
  const valor_editar = (valor_backend_editar && valor_backend_editar !== 'EDITAR')
    ? valor_backend_editar
    : CHAT_CMD.EDITAR_DUPLA;

  const handleConfirmar = () => {
    onEnviar(valor_confirmar);
  };

  const handleEditar = () => {
    onEnviar(valor_editar);
  };

  const handleTerceiro = () => {
    if (valor_terceiro) onEnviar(valor_terceiro);
  };

  return (
    <div className="confirmacao-dupla-container">
      <div className="botoes-confirmacao">
        {botao_terceiro && valor_terceiro && (
          <button
            className="btn-confirmacao btn-terceiro"
            onClick={handleTerceiro}
            disabled={isProcessing}
          >
            {botao_terceiro}
          </button>
        )}
        {dados.botao_editar && (
          <button
            className="btn-confirmacao btn-editar"
            onClick={handleEditar}
            disabled={isProcessing}
          >
            {botao_editar}
          </button>
        )}
        <button
          className="btn-confirmacao btn-confirmar"
          onClick={handleConfirmar}
          disabled={isProcessing}
        >
          {botao_confirmar}
        </button>
      </div>

      <style>{`
        .confirmacao-dupla-container {
          margin: 1.5rem 0;
        }

        .botoes-confirmacao {
          display: flex;
          gap: 1rem;
          justify-content: center;
          flex-wrap: wrap;
        }

        .btn-confirmacao {
          padding: 0.9rem 2rem;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          font-size: 1rem;
          cursor: pointer;
          transition: all 0.3s ease;
          min-width: 150px;
        }

        .btn-confirmar {
          background: #28a745;
          color: white;
        }

        .btn-confirmar:hover {
          background: #218838;
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
        }

        .btn-editar {
          background: #ffc107;
          color: #212529;
        }

        .btn-editar:hover {
          background: #e0a800;
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(255, 193, 7, 0.3);
        }

        .btn-terceiro {
          background: #1351B4;
          color: white;
        }

        .btn-terceiro:hover {
          background: #0c3d8a;
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(19, 81, 180, 0.3);
        }

        .btn-confirmacao:active {
          transform: translateY(0);
        }

        .btn-confirmacao:disabled {
          opacity: 0.5;
          cursor: not-allowed;
          transform: none;
          box-shadow: none;
        }

        @media (max-width: 768px) {
          .botoes-confirmacao {
            flex-direction: column;
          }

          .btn-confirmacao {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
};

export default InterfaceConfirmacaoDupla;
