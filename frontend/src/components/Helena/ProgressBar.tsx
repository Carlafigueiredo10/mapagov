/**
 * ProgressBar - Barra de progresso animada
 *
 * Exibe percentual de conclusão com indicadores visuais e marcos
 */

import React from 'react';
import './ProgressBar.css';

interface ProgressBarProps {
  percentual: number; // 0-100
  altura?: number; // em pixels
  mostrarLabel?: boolean;
  mostrarMarcos?: boolean;
  cor?: 'padrao' | 'sucesso' | 'aviso' | 'erro';
  className?: string;
}

const MARCOS = [
  { percentual: 0, label: 'Início' },
  { percentual: 25, label: 'Diagnóstico' },
  { percentual: 50, label: 'Construção' },
  { percentual: 75, label: 'Refinamento' },
  { percentual: 100, label: 'Concluído' }
];

export const ProgressBar: React.FC<ProgressBarProps> = ({
  percentual,
  altura = 24,
  mostrarLabel = true,
  mostrarMarcos = false,
  cor = 'padrao',
  className = ''
}) => {
  // Garantir que percentual está entre 0-100
  const percentualSeguro = Math.min(100, Math.max(0, percentual));

  // Determinar cor baseada em percentual se cor === 'padrao'
  const obterCor = () => {
    if (cor !== 'padrao') return cor;
    if (percentualSeguro < 25) return 'erro';
    if (percentualSeguro < 50) return 'aviso';
    if (percentualSeguro < 100) return 'padrao';
    return 'sucesso';
  };

  const corFinal = obterCor();

  return (
    <div className={`progress-bar-container ${className}`}>
      {/* Barra principal */}
      <div className="progress-bar-wrapper" style={{ height: `${altura}px` }}>
        <div className="progress-bar-track">
          <div
            className={`progress-bar-fill ${corFinal}`}
            style={{ width: `${percentualSeguro}%` }}
          >
            {/* Label interno */}
            {mostrarLabel && percentualSeguro > 10 && (
              <span className="progress-label-interno">{percentualSeguro}%</span>
            )}

            {/* Shimmer effect */}
            <div className="progress-shimmer" />
          </div>
        </div>

        {/* Label externo (quando percentual muito baixo) */}
        {mostrarLabel && percentualSeguro <= 10 && (
          <span className="progress-label-externo">{percentualSeguro}%</span>
        )}
      </div>

      {/* Marcos */}
      {mostrarMarcos && (
        <div className="progress-marcos">
          {MARCOS.map(marco => (
            <div
              key={marco.percentual}
              className={`progress-marco ${
                percentualSeguro >= marco.percentual ? 'atingido' : 'pendente'
              }`}
              style={{ left: `${marco.percentual}%` }}
            >
              {/* Indicador visual */}
              <div className="marco-indicador">
                {percentualSeguro >= marco.percentual ? '✓' : '○'}
              </div>

              {/* Label */}
              <div className="marco-label">{marco.label}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProgressBar;
