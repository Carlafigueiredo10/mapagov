/**
 * Etapa3_Analise - Analisar probabilidade e impacto dos riscos
 */
import React, { useState } from 'react';
import { useAnaliseRiscosStore } from '../../store/analiseRiscosStore';
import { CORES_NIVEL, NivelRisco } from '../../types/analiseRiscos.types';

interface Props {
  onAvancar: () => void;
  onVoltar: () => void;
}

const Etapa3Analise: React.FC<Props> = ({ onAvancar, onVoltar }) => {
  const { currentAnalise, analisarRisco } = useAnaliseRiscosStore();

  // Estado para edicao inline
  const [editando, setEditando] = useState<string | null>(null);
  const [probTemp, setProbTemp] = useState(3);
  const [impactoTemp, setImpactoTemp] = useState(3);

  const riscos = currentAnalise?.riscos || [];

  const handleIniciarEdicao = (
    riscoId: string,
    prob: number,
    impacto: number
  ) => {
    setEditando(riscoId);
    setProbTemp(prob);
    setImpactoTemp(impacto);
  };

  const handleSalvarEdicao = async (riscoId: string) => {
    await analisarRisco(riscoId, probTemp, impactoTemp);
    setEditando(null);
  };

  const handleCancelarEdicao = () => {
    setEditando(null);
  };

  const handleAvancar = () => {
    onAvancar();
  };

  const getCorNivel = (nivel: NivelRisco): string => {
    return CORES_NIVEL[nivel] || '#6b7280';
  };

  return (
    <div>
      <h3>Etapa 3: Analise de Probabilidade e Impacto</h3>

      <p style={{ color: '#666', marginBottom: '20px' }}>
        Revise e ajuste a probabilidade e impacto de cada risco identificado.
      </p>

      {/* Lista de riscos para analise */}
      <div
        style={{
          padding: '15px',
          background: '#f9fafb',
          borderRadius: '8px',
          marginBottom: '20px',
        }}
      >
        <h4 style={{ marginTop: 0 }}>Riscos para Analise ({riscos.length})</h4>

        {riscos.length === 0 ? (
          <p style={{ color: '#666' }}>Nenhum risco para analisar.</p>
        ) : (
          <div>
            {riscos.map((risco) => (
              <div
                key={risco.id}
                style={{
                  padding: '15px',
                  background: 'white',
                  borderRadius: '8px',
                  marginBottom: '10px',
                  border: '1px solid #e5e7eb',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                  }}
                >
                  <div>
                    <strong>{risco.titulo}</strong>
                    <br />
                    <span style={{ color: '#666', fontSize: '14px' }}>
                      {risco.categoria}
                    </span>
                  </div>
                  <span
                    style={{
                      padding: '4px 12px',
                      borderRadius: '4px',
                      background: getCorNivel(risco.nivel_risco),
                      color: 'white',
                      fontWeight: 'bold',
                    }}
                  >
                    {risco.nivel_risco} ({risco.score_risco})
                  </span>
                </div>

                {editando === risco.id ? (
                  // Modo edicao
                  <div style={{ marginTop: '15px' }}>
                    <div
                      style={{ display: 'flex', gap: '15px', marginBottom: '10px' }}
                    >
                      <div style={{ flex: 1 }}>
                        <label style={{ display: 'block', marginBottom: '5px' }}>
                          Probabilidade (1-5):
                        </label>
                        <select
                          value={probTemp}
                          onChange={(e) => setProbTemp(Number(e.target.value))}
                          style={{ width: '100%', padding: '8px' }}
                        >
                          {[1, 2, 3, 4, 5].map((n) => (
                            <option key={n} value={n}>
                              {n} -{' '}
                              {n === 1
                                ? 'Muito Baixo'
                                : n === 2
                                ? 'Baixo'
                                : n === 3
                                ? 'Medio'
                                : n === 4
                                ? 'Alto'
                                : 'Muito Alto'}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div style={{ flex: 1 }}>
                        <label style={{ display: 'block', marginBottom: '5px' }}>
                          Impacto (1-5):
                        </label>
                        <select
                          value={impactoTemp}
                          onChange={(e) => setImpactoTemp(Number(e.target.value))}
                          style={{ width: '100%', padding: '8px' }}
                        >
                          {[1, 2, 3, 4, 5].map((n) => (
                            <option key={n} value={n}>
                              {n} -{' '}
                              {n === 1
                                ? 'Muito Baixo'
                                : n === 2
                                ? 'Baixo'
                                : n === 3
                                ? 'Medio'
                                : n === 4
                                ? 'Alto'
                                : 'Muito Alto'}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: '10px' }}>
                      <button
                        onClick={() => handleSalvarEdicao(risco.id)}
                        style={{
                          padding: '8px 16px',
                          background: '#10b981',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                        }}
                      >
                        Salvar
                      </button>
                      <button
                        onClick={handleCancelarEdicao}
                        style={{
                          padding: '8px 16px',
                          background: '#6b7280',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                        }}
                      >
                        Cancelar
                      </button>
                    </div>
                  </div>
                ) : (
                  // Modo visualizacao
                  <div style={{ marginTop: '15px' }}>
                    <span style={{ marginRight: '20px' }}>
                      <strong>P:</strong> {risco.probabilidade}
                    </span>
                    <span style={{ marginRight: '20px' }}>
                      <strong>I:</strong> {risco.impacto}
                    </span>
                    <button
                      onClick={() =>
                        handleIniciarEdicao(
                          risco.id,
                          risco.probabilidade,
                          risco.impacto
                        )
                      }
                      style={{
                        padding: '4px 12px',
                        background: '#3b82f6',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '12px',
                      }}
                    >
                      Editar
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Resumo */}
      {riscos.length > 0 && (
        <div
          style={{
            padding: '15px',
            background: '#e0f2fe',
            borderRadius: '8px',
            marginBottom: '20px',
          }}
        >
          <h4 style={{ marginTop: 0 }}>Resumo da Analise</h4>
          <div style={{ display: 'flex', gap: '20px' }}>
            {(['CRITICO', 'ALTO', 'MEDIO', 'BAIXO'] as NivelRisco[]).map(
              (nivel) => {
                const count = riscos.filter(
                  (r) => r.nivel_risco === nivel
                ).length;
                return (
                  <div key={nivel} style={{ textAlign: 'center' }}>
                    <div
                      style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '50%',
                        background: getCorNivel(nivel),
                        color: 'white',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 'bold',
                        margin: '0 auto 5px',
                      }}
                    >
                      {count}
                    </div>
                    <span style={{ fontSize: '12px' }}>{nivel}</span>
                  </div>
                );
              }
            )}
          </div>
        </div>
      )}

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
          onClick={handleAvancar}
          disabled={riscos.length === 0}
          style={{
            padding: '10px 30px',
            background: riscos.length === 0 ? '#d1d5db' : '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: riscos.length === 0 ? 'not-allowed' : 'pointer',
          }}
        >
          Ver Matriz →
        </button>
      </div>
    </div>
  );
};

export default Etapa3Analise;
