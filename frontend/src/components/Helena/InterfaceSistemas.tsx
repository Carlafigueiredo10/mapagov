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

  // Extrair lista flat de todos os sistemas
  const todosSistemas = dados?.sistemas_por_categoria
    ? Object.values(dados.sistemas_por_categoria).flat()
    : [];

  const toggleSistema = (sistema: string) => {
    if (sistemasSelecionados.includes(sistema)) {
      setSistemasSelecionados(sistemasSelecionados.filter(s => s !== sistema));
    } else {
      setSistemasSelecionados([...sistemasSelecionados, sistema]);
    }
  };

  const handleConfirmar = () => {
    const resposta = sistemasSelecionados.length > 0
      ? JSON.stringify(sistemasSelecionados)
      : 'nenhum';

    console.log('📤 Enviando sistemas:', resposta);
    onConfirm(resposta);
  };

  return (
    <div className="interface-container">
      <div className="interface-title">💻 Quais sistemas você utiliza?</div>

      <div className="sistemas-info">
        {sistemasSelecionados.length} de {todosSistemas.length} selecionados
      </div>

      <div className="sistemas-grid">
        {todosSistemas.map((sistema) => (
          <button
            key={sistema}
            onClick={() => toggleSistema(sistema)}
            className={`sistema-card ${sistemasSelecionados.includes(sistema) ? 'selected' : ''}`}
          >
            {sistema}
          </button>
        ))}
      </div>

      <div className="action-buttons">
        <button className="btn-secondary" onClick={() => onConfirm('nenhum')}>
          Nenhum
        </button>
        <button className="btn-primary" onClick={handleConfirmar}>
          Confirmar ({sistemasSelecionados.length})
        </button>
      </div>

      <style>{`
        .sistemas-info {
          margin-bottom: 16px;
          padding: 12px;
          background: #f0f0f0;
          border-radius: 6px;
          text-align: center;
          font-weight: 500;
        }

        .sistemas-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
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
