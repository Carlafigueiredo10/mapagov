/**
 * Etapa3_Analise - Analisar probabilidade e impacto dos riscos identificados
 */
import React, { useState, useMemo } from 'react';
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
  const [probTemp, setProbTemp] = useState<number | undefined>(undefined);
  const [impactoTemp, setImpactoTemp] = useState<number | undefined>(undefined);

  const riscos = currentAnalise?.riscos || [];

  // Validacao: todos os riscos devem ter P/I preenchidos para avancar
  const riscosSemPI = useMemo(() => {
    return riscos.filter(r => r.probabilidade == null || r.impacto == null);
  }, [riscos]);

  const podeAvancar = riscos.length > 0 && riscosSemPI.length === 0;

  const handleIniciarEdicao = (
    riscoId: string,
    prob: number | undefined,
    impacto: number | undefined
  ) => {
    setEditando(riscoId);
    setProbTemp(prob);
    setImpactoTemp(impacto);
  };

  const handleSalvarEdicao = async (riscoId: string) => {
    if (probTemp === undefined || impactoTemp === undefined) {
      alert('Selecione probabilidade e impacto antes de salvar');
      return;
    }
    await analisarRisco(riscoId, probTemp, impactoTemp);
    setEditando(null);
  };

  const handleCancelarEdicao = () => {
    setEditando(null);
  };

  const handleAvancar = () => {
    if (!podeAvancar) {
      alert(`${riscosSemPI.length} risco(s) ainda sem Probabilidade/Impacto. Preencha todos para avancar.`);
      return;
    }
    onAvancar();
  };

  const getCorNivel = (nivel: NivelRisco): string => {
    return CORES_NIVEL[nivel] || '#6b7280';
  };

  return (
    <div>
      <h3 style={{ marginBottom: '8px' }}>Análise de Probabilidade e Impacto</h3>

      <p style={{ color: '#555', marginBottom: '12px', lineHeight: '1.6' }}>
        Nesta etapa, cada risco identificado deve ser classificado quanto à probabilidade e ao impacto, em escala de 1 a 5.
      </p>
      <p style={{ color: '#555', marginBottom: '20px', lineHeight: '1.6' }}>
        O avanço da análise exige que todos os riscos estejam classificados.
        Para registrar a avaliação, selecione o risco desejado e clique em{' '}
        <span style={{
          display: 'inline-block',
          padding: '2px 8px',
          background: '#3b82f6',
          color: 'white',
          borderRadius: '4px',
          fontSize: '12px',
          fontWeight: '500',
        }}>Editar</span>.
      </p>

      {/* Lista de riscos para análise */}
      <div
        style={{
          padding: '15px',
          background: '#f9fafb',
          borderRadius: '8px',
          marginBottom: '20px',
        }}
      >
        <h4 style={{ marginTop: 0 }}>Riscos para Análise ({riscos.length})</h4>

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
                      background: risco.nivel_risco ? getCorNivel(risco.nivel_risco) : '#9ca3af',
                      color: 'white',
                      fontWeight: 'bold',
                    }}
                  >
                    {risco.nivel_risco ? `${risco.nivel_risco} (${risco.score_risco})` : 'Pendente'}
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
                          Probabilidade (1-5): *
                        </label>
                        <select
                          value={probTemp ?? ''}
                          onChange={(e) => setProbTemp(e.target.value ? Number(e.target.value) : undefined)}
                          style={{ width: '100%', padding: '8px' }}
                        >
                          <option value="">-- Selecione --</option>
                          {[1, 2, 3, 4, 5].map((n) => (
                            <option key={n} value={n}>
                              {n} - {n === 1 ? 'Muito Baixa' : n === 2 ? 'Baixa' : n === 3 ? 'Media' : n === 4 ? 'Alta' : 'Muito Alta'}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div style={{ flex: 1 }}>
                        <label style={{ display: 'block', marginBottom: '5px' }}>
                          Impacto (1-5): *
                        </label>
                        <select
                          value={impactoTemp ?? ''}
                          onChange={(e) => setImpactoTemp(e.target.value ? Number(e.target.value) : undefined)}
                          style={{ width: '100%', padding: '8px' }}
                        >
                          <option value="">-- Selecione --</option>
                          {[1, 2, 3, 4, 5].map((n) => (
                            <option key={n} value={n}>
                              {n} - {n === 1 ? 'Muito Baixo' : n === 2 ? 'Baixo' : n === 3 ? 'Medio' : n === 4 ? 'Alto' : 'Muito Alto'}
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
                      <strong>P:</strong> {risco.probabilidade ?? '--'}
                    </span>
                    <span style={{ marginRight: '20px' }}>
                      <strong>I:</strong> {risco.impacto ?? '--'}
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

      {/* Alerta de riscos pendentes */}
      {riscosSemPI.length > 0 && (
        <div
          style={{
            padding: '12px 15px',
            background: '#fef3c7',
            border: '1px solid #f59e0b',
            borderRadius: '8px',
            marginBottom: '20px',
            color: '#92400e',
          }}
        >
          <strong>{riscosSemPI.length} risco(s) pendente(s):</strong> Preencha Probabilidade e Impacto de todos os riscos para avancar.
        </div>
      )}

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
          <h4 style={{ marginTop: 0 }}>Resumo da Análise</h4>
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
          disabled={!podeAvancar}
          title={!podeAvancar ? `${riscosSemPI.length} risco(s) sem P/I` : ''}
          style={{
            padding: '10px 30px',
            background: !podeAvancar ? '#d1d5db' : '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: !podeAvancar ? 'not-allowed' : 'pointer',
          }}
        >
          Ver Matriz →
        </button>
      </div>
    </div>
  );
};

export default Etapa3Analise;
