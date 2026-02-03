/**
 * Etapa4_Matriz - Visualizacao da matriz de riscos 5x5
 */
import React from 'react';
import { useAnaliseRiscosStore } from '../../store/analiseRiscosStore';
import { CORES_NIVEL, NivelRisco } from '../../types/analiseRiscos.types';

interface Props {
  onAvancar: () => void;
  onVoltar: () => void;
}

const Etapa4Matriz: React.FC<Props> = ({ onAvancar, onVoltar }) => {
  const { currentAnalise } = useAnaliseRiscosStore();

  const riscos = currentAnalise?.riscos || [];

  // Contar riscos em cada celula da matriz
  const getCount = (prob: number, imp: number) => {
    return riscos.filter(
      (r) => r.probabilidade === prob && r.impacto === imp
    ).length;
  };

  // Cor da celula baseada no score
  const getCellColor = (prob: number, imp: number) => {
    const score = prob * imp;
    if (score >= 20) return '#ef4444'; // CRITICO
    if (score >= 12) return '#f97316'; // ALTO
    if (score >= 6) return '#eab308'; // MEDIO
    return '#22c55e'; // BAIXO
  };

  // Riscos por nivel
  const riscosAgrupados = {
    CRITICO: riscos.filter((r) => r.nivel_risco === 'CRITICO'),
    ALTO: riscos.filter((r) => r.nivel_risco === 'ALTO'),
    MEDIO: riscos.filter((r) => r.nivel_risco === 'MEDIO'),
    BAIXO: riscos.filter((r) => r.nivel_risco === 'BAIXO'),
  };

  return (
    <div>
      <h3>Etapa 4: Matriz de Riscos</h3>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Visualize os riscos na matriz Probabilidade x Impacto.
      </p>

      {/* Matriz 5x5 */}
      <div
        style={{
          display: 'flex',
          gap: '30px',
          marginBottom: '30px',
          flexWrap: 'wrap',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'flex-end' }}>
            {/* Label Y */}
            <div
              style={{
                writingMode: 'vertical-rl',
                transform: 'rotate(180deg)',
                textAlign: 'center',
                marginRight: '10px',
                fontWeight: 'bold',
                color: '#666',
              }}
            >
              PROBABILIDADE
            </div>

            {/* Matriz */}
            <div>
              {[5, 4, 3, 2, 1].map((prob) => (
                <div key={prob} style={{ display: 'flex' }}>
                  <div
                    style={{
                      width: '30px',
                      height: '50px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 'bold',
                      color: '#666',
                    }}
                  >
                    {prob}
                  </div>
                  {[1, 2, 3, 4, 5].map((imp) => {
                    const count = getCount(prob, imp);
                    return (
                      <div
                        key={imp}
                        style={{
                          width: '50px',
                          height: '50px',
                          background: getCellColor(prob, imp),
                          border: '1px solid white',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: 'white',
                          fontWeight: 'bold',
                          fontSize: '18px',
                          opacity: count > 0 ? 1 : 0.4,
                        }}
                        title={`P=${prob}, I=${imp}: ${count} risco(s)`}
                      >
                        {count > 0 ? count : ''}
                      </div>
                    );
                  })}
                </div>
              ))}
              {/* Label X */}
              <div style={{ display: 'flex', marginTop: '5px' }}>
                <div style={{ width: '30px' }}></div>
                {[1, 2, 3, 4, 5].map((imp) => (
                  <div
                    key={imp}
                    style={{
                      width: '50px',
                      textAlign: 'center',
                      fontWeight: 'bold',
                      color: '#666',
                    }}
                  >
                    {imp}
                  </div>
                ))}
              </div>
              <div
                style={{
                  textAlign: 'center',
                  marginTop: '5px',
                  fontWeight: 'bold',
                  color: '#666',
                  marginLeft: '30px',
                }}
              >
                IMPACTO
              </div>
            </div>
          </div>
        </div>

        {/* Legenda */}
        <div style={{ flex: 1, minWidth: '200px' }}>
          <h4 style={{ marginTop: 0 }}>Legenda</h4>
          {(['CRITICO', 'ALTO', 'MEDIO', 'BAIXO'] as NivelRisco[]).map((nivel) => (
            <div
              key={nivel}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                marginBottom: '8px',
              }}
            >
              <div
                style={{
                  width: '20px',
                  height: '20px',
                  background: CORES_NIVEL[nivel],
                  borderRadius: '4px',
                }}
              />
              <span>
                {nivel} ({riscosAgrupados[nivel].length})
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Lista de riscos por nivel */}
      <div style={{ marginBottom: '20px' }}>
        <h4>Riscos por Nivel</h4>
        {(['CRITICO', 'ALTO', 'MEDIO', 'BAIXO'] as NivelRisco[]).map((nivel) => {
          const riscosNivel = riscosAgrupados[nivel];
          if (riscosNivel.length === 0) return null;

          return (
            <div
              key={nivel}
              style={{
                marginBottom: '15px',
                padding: '15px',
                background: '#f9fafb',
                borderRadius: '8px',
                borderLeft: `4px solid ${CORES_NIVEL[nivel]}`,
              }}
            >
              <h5 style={{ margin: '0 0 10px 0', color: CORES_NIVEL[nivel] }}>
                {nivel} ({riscosNivel.length})
              </h5>
              {riscosNivel.map((risco) => (
                <div
                  key={risco.id}
                  style={{
                    padding: '8px',
                    background: 'white',
                    borderRadius: '4px',
                    marginBottom: '5px',
                  }}
                >
                  <strong>{risco.titulo}</strong>
                  <span style={{ marginLeft: '10px', color: '#666', fontSize: '13px' }}>
                    (P={risco.probabilidade} x I={risco.impacto} = {risco.score_risco})
                  </span>
                </div>
              ))}
            </div>
          );
        })}
      </div>

      {/* Navegacao */}
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <button
          onClick={onVoltar}
          style={{
            padding: '10px 30px',
            background: '#6b7280',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          ← Voltar
        </button>
        <button
          onClick={onAvancar}
          style={{
            padding: '12px 30px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Definir Respostas →
        </button>
      </div>
    </div>
  );
};

export default Etapa4Matriz;
