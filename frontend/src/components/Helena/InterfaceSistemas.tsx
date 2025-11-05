// InterfaceSistemas.tsx - REESCRITO DO ZERO (SIMPLES)

import React, { useState } from 'react';

interface InterfaceSistemasProps {
  dados?: {
    sistemas_por_categoria?: Record<string, string[]>;
  };
  onConfirm: (resposta: string) => void;
}

const InterfaceSistemas: React.FC<InterfaceSistemasProps> = ({ dados, onConfirm }) => {
  const [sistemasSelecionados, setSistemasSelecionados] = useState<string[]>([]);
  const [sistemasDigitados, setSistemasDigitados] = useState<string[]>([]);
  const [sistemaManual, setSistemaManual] = useState<string>('');

  // Extrair lista flat de todos os sistemas
  const todosSistemas = dados?.sistemas_por_categoria
    ? Object.values(dados.sistemas_por_categoria).flat()
    : [];

  // Combinar sistemas selecionados (checkboxes) + digitados
  const todosSistemasSelecionados = [...sistemasSelecionados, ...sistemasDigitados];

  const toggleSistema = (sistema: string) => {
    if (sistemasSelecionados.includes(sistema)) {
      setSistemasSelecionados(sistemasSelecionados.filter(s => s !== sistema));
    } else {
      setSistemasSelecionados([...sistemasSelecionados, sistema]);
    }
  };

  const adicionarSistemaManual = () => {
    const sistema = sistemaManual.trim();
    if (sistema && !todosSistemasSelecionados.includes(sistema)) {
      setSistemasDigitados([...sistemasDigitados, sistema]);
      setSistemaManual('');
    }
  };

  const removerSistemaDigitado = (sistema: string) => {
    setSistemasDigitados(sistemasDigitados.filter(s => s !== sistema));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      adicionarSistemaManual();
    }
  };

  const handleConfirmar = () => {
    const resposta = todosSistemasSelecionados.length > 0
      ? JSON.stringify(todosSistemasSelecionados)
      : 'nenhum';

    console.log('📤 Enviando sistemas:', resposta);
    onConfirm(resposta);
  };

  return (
    <div className="interface-container">
      <div className="sistemas-info">
        {todosSistemasSelecionados.length} sistema(s) selecionado(s) ({sistemasSelecionados.length} checkboxes + {sistemasDigitados.length} digitados)
      </div>

      <div className="sistemas-grid">
        {todosSistemas.map((sistema) => (
          <button
            key={sistema}
            onClick={() => toggleSistema(sistema)}
            className={`sistema-card ${sistemasSelecionados.includes(sistema) ? 'selected' : ''}`}
          >
            <div className="checkbox-circle">
              {sistemasSelecionados.includes(sistema) && <div className="checkbox-inner" />}
            </div>
            <span className="sistema-nome">{sistema}</span>
          </button>
        ))}
      </div>

      {/* Mostrar sistemas digitados manualmente */}
      {sistemasDigitados.length > 0 && (
        <div className="sistemas-digitados">
          <div className="sistemas-digitados-label">
            📝 Sistemas adicionados manualmente:
          </div>
          <div className="sistemas-digitados-lista">
            {sistemasDigitados.map((sistema, idx) => (
              <div key={idx} className="sistema-digitado-card">
                <span className="sistema-digitado-nome">{sistema}</span>
                <button
                  className="btn-remover"
                  onClick={() => removerSistemaDigitado(sistema)}
                  title="Remover"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="campo-manual">
        <div className="campo-manual-label">
          Não achou algum sistema? ✍️ Digite manualmente no campo abaixo.
        </div>
        <div className="campo-manual-input-group">
          <input
            type="text"
            className="campo-manual-input"
            placeholder="Ex: SIAPE, SISAC, etc."
            value={sistemaManual}
            onChange={(e) => setSistemaManual(e.target.value)}
            onKeyPress={handleKeyPress}
          />
          <button
            className="btn-adicionar"
            onClick={adicionarSistemaManual}
            disabled={!sistemaManual.trim()}
          >
            + Adicionar
          </button>
        </div>
      </div>

      <div className="action-buttons">
        <button className="btn-secondary" onClick={() => onConfirm('nenhum')}>
          Nenhum
        </button>
        <button className="btn-primary" onClick={handleConfirmar}>
          Confirmar ({todosSistemasSelecionados.length})
        </button>
      </div>

      <style>{`
        .sistemas-info {
          margin-bottom: 16px;
          padding: 12px;
          background: #e3f2fd;
          border-radius: 6px;
          text-align: center;
          font-weight: 500;
          color: #1351B4;
        }

        .sistemas-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
          margin-bottom: 20px;
        }

        .sistema-card {
          padding: 12px 16px;
          border: 2px solid #ddd;
          border-radius: 8px;
          background: white;
          cursor: pointer;
          transition: all 0.2s;
          font-size: 14px;
          text-align: left;
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .checkbox-circle {
          width: 20px;
          height: 20px;
          min-width: 20px;
          border: 2px solid #ddd;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }

        .sistema-card:hover .checkbox-circle {
          border-color: #1351B4;
        }

        .sistema-card.selected .checkbox-circle {
          border-color: #1351B4;
          background: #1351B4;
        }

        .checkbox-inner {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: white;
        }

        .sistema-nome {
          flex: 1;
        }

        .sistema-card:hover {
          border-color: #1351B4;
          background: #f8f9fa;
        }

        .sistema-card.selected {
          border-color: #1351B4;
          background: #e3f2fd;
          font-weight: 600;
        }

        .sistemas-digitados {
          margin: 20px 0;
          padding: 16px;
          background: #e8f5e9;
          border-radius: 8px;
          border: 2px solid #4caf50;
        }

        .sistemas-digitados-label {
          margin-bottom: 12px;
          font-size: 14px;
          color: #2e7d32;
          font-weight: 600;
        }

        .sistemas-digitados-lista {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .sistema-digitado-card {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 12px;
          background: white;
          border: 2px solid #4caf50;
          border-radius: 20px;
          font-size: 14px;
          font-weight: 500;
          color: #2e7d32;
        }

        .sistema-digitado-nome {
          flex: 1;
        }

        .btn-remover {
          width: 20px;
          height: 20px;
          padding: 0;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #f44336;
          color: white;
          border: none;
          border-radius: 50%;
          cursor: pointer;
          font-size: 12px;
          line-height: 1;
          transition: all 0.2s;
        }

        .btn-remover:hover {
          background: #d32f2f;
          transform: scale(1.1);
        }

        .campo-manual {
          margin: 24px 0;
          padding: 20px;
          background: #fff9e6;
          border-radius: 8px;
          border: 2px dashed #ffc107;
        }

        .campo-manual-label {
          margin-bottom: 12px;
          font-size: 14px;
          color: #856404;
          font-weight: 500;
        }

        .campo-manual-input-group {
          display: flex;
          gap: 8px;
        }

        .campo-manual-input {
          flex: 1;
          padding: 10px 14px;
          border: 2px solid #ddd;
          border-radius: 6px;
          font-size: 14px;
          transition: all 0.2s;
        }

        .campo-manual-input:focus {
          outline: none;
          border-color: #1351B4;
          background: #f8f9fa;
        }

        .btn-adicionar {
          padding: 10px 20px;
          background: #28a745;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          transition: all 0.2s;
          white-space: nowrap;
        }

        .btn-adicionar:hover:not(:disabled) {
          background: #218838;
        }

        .btn-adicionar:disabled {
          background: #6c757d;
          cursor: not-allowed;
          opacity: 0.5;
        }

        .action-buttons {
          display: flex;
          gap: 12px;
          justify-content: flex-end;
        }

        .btn-primary, .btn-secondary {
          padding: 12px 24px;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 16px;
          font-weight: 500;
          transition: all 0.2s;
        }

        .btn-primary {
          background: #1351B4;
          color: white;
        }

        .btn-primary:hover {
          background: #0c3a7a;
        }

        .btn-secondary {
          background: #6c757d;
          color: white;
        }

        .btn-secondary:hover {
          background: #5a6268;
        }
      `}</style>
    </div>
  );
};

export default InterfaceSistemas;
