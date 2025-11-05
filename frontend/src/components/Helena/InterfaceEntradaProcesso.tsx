// InterfaceEntradaProcesso.tsx - REESCRITO DO ZERO (SIMPLES)

import React, { useState } from 'react';

interface InterfaceEntradaProcessoProps {
  dados?: {
    areas_organizacionais?: Array<{ nome: string; sigla?: string }>;
    orgaos_centralizados?: Array<{ nome: string; sigla?: string }>;
    orgaos_controle?: Array<{ nome: string; sigla: string }>;
    orgaos_judiciarios?: Array<{ nome: string; sigla: string }>;
    canais_usuario?: Array<{ nome: string; sigla: string }>;
  };
  onConfirm: (resposta: string) => void;
}

const InterfaceEntradaProcesso: React.FC<InterfaceEntradaProcessoProps> = ({ dados, onConfirm }) => {
  const [selecionados, setSelecionados] = useState<string[]>([]);

  // Combinar todas as opções
  const todasOpcoes = [
    ...(dados?.areas_organizacionais || []),
    ...(dados?.orgaos_centralizados || []),
    ...(dados?.orgaos_controle || []),
    ...(dados?.orgaos_judiciarios || []),
    ...(dados?.canais_usuario || [])
  ];

  // DEBUG: Ver o que está chegando
  console.log('🔍 InterfaceEntradaProcesso - dados recebidos:', dados);
  console.log('🔍 InterfaceEntradaProcesso - areas_organizacionais:', dados?.areas_organizacionais);
  console.log('🔍 InterfaceEntradaProcesso - todasOpcoes:', todasOpcoes);

  const toggleItem = (nome: string) => {
    if (selecionados.includes(nome)) {
      setSelecionados(selecionados.filter(s => s !== nome));
    } else {
      setSelecionados([...selecionados, nome]);
    }
  };

  const handleConfirmar = () => {
    const resposta = selecionados.length > 0
      ? selecionados.join(' | ')
      : 'nenhum';

    console.log('📤 Enviando entradas:', resposta);
    onConfirm(resposta);
  };

  return (
    <div className="interface-container">
      <div className="interface-title">📥 De onde vem o processo?</div>

      <div className="entradas-info">
        {selecionados.length} origem(ns) selecionada(s)
      </div>

      <div className="entradas-grid">
        {todasOpcoes.map((item) => (
          <button
            key={item.nome}
            onClick={() => toggleItem(item.nome)}
            className={`entrada-card ${selecionados.includes(item.nome) ? 'selected' : ''}`}
          >
            {item.sigla && <div className="sigla">{item.sigla}</div>}
            <div className="nome">{item.nome}</div>
          </button>
        ))}
      </div>

      <div className="action-buttons">
        <button className="btn-secondary" onClick={() => onConfirm('nenhum')}>
          Nenhum
        </button>
        <button className="btn-primary" onClick={handleConfirmar}>
          Confirmar ({selecionados.length})
        </button>
      </div>

      <style>{`
        .entradas-info {
          margin-bottom: 16px;
          padding: 12px;
          background: #f0f0f0;
          border-radius: 6px;
          text-align: center;
          font-weight: 500;
        }

        .entradas-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
          gap: 12px;
          margin-bottom: 20px;
        }

        .entrada-card {
          padding: 12px;
          border: 2px solid #ddd;
          border-radius: 8px;
          background: white;
          cursor: pointer;
          transition: all 0.2s;
          text-align: center;
        }

        .entrada-card:hover {
          border-color: #1351B4;
          background: #f8f9fa;
        }

        .entrada-card.selected {
          border-color: #1351B4;
          background: #e3f2fd;
        }

        .sigla {
          font-weight: 700;
          font-size: 16px;
          color: #1351B4;
          margin-bottom: 4px;
        }

        .nome {
          font-size: 13px;
          color: #666;
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

export default InterfaceEntradaProcesso;
