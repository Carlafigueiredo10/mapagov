import React from 'react';
import { CHAT_CMD } from '../../constants/chatCommands';

interface InterfaceConfirmacaoDuplaProps {
  dados: {
    botao_confirmar?: string;
    botao_editar?: string;
    valor_confirmar?: string;
    valor_editar?: string;
  };
  onEnviar: (valor: string) => void;
}

const InterfaceConfirmacaoDupla: React.FC<InterfaceConfirmacaoDuplaProps> = ({ dados, onEnviar }) => {
  const {
    botao_confirmar = 'Confirmar ✅',
    botao_editar = 'Editar ✏️',
    valor_confirmar: valor_backend_confirmar,
    valor_editar: valor_backend_editar,
  } = dados;

  // ✅ FIX: Usar valores do backend quando específicos, tokens só para genéricos
  // Se backend envia "objetiva"/"detalhada"/etc → usa esses valores
  // Se backend envia "CONFIRMAR"/"EDITAR" ou nada → usa tokens determinísticos
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

  return (
    <div className="confirmacao-dupla-container">
      <div className="botoes-confirmacao">
        <button
          className="btn-confirmacao btn-editar"
          onClick={handleEditar}
        >
          {botao_editar}
        </button>
        <button
          className="btn-confirmacao btn-confirmar"
          onClick={handleConfirmar}
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

        .btn-confirmacao:active {
          transform: translateY(0);
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
