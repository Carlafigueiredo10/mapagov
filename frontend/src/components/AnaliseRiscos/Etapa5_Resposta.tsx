/**
 * Etapa5_Resposta - Definir estrategias de resposta aos riscos
 */
import React, { useState } from 'react';
import { useAnaliseRiscosStore } from '../../store/analiseRiscosStore';
import {
  CORES_NIVEL,
  DESCRICOES_ESTRATEGIA,
  EstrategiaResposta,
  NivelRisco,
  CategoriaRisco,
} from '../../types/analiseRiscos.types';
import { getSugestoes } from '../../data/sugestoesRespostaRisco';

interface Props {
  onVoltar: () => void;
  onFinalizar: () => void;
}

const ESTRATEGIAS: EstrategiaResposta[] = ['MITIGAR', 'EVITAR', 'COMPARTILHAR', 'ACEITAR', 'RESGUARDAR'];

const Etapa5Resposta: React.FC<Props> = ({ onVoltar, onFinalizar }) => {
  const { currentAnalise, adicionarResposta, finalizarAnalise, loading } = useAnaliseRiscosStore();

  const riscos = currentAnalise?.riscos || [];

  // Estado local para respostas em edicao
  const [respostasLocal, setRespostasLocal] = useState<
    Record<string, { estrategia: EstrategiaResposta; acao: string; responsavel: string }>
  >({});
  const [riscoExpandido, setRiscoExpandido] = useState<string | null>(null);

  const handleSetResposta = (riscoId: string, campo: string, valor: string) => {
    setRespostasLocal((prev) => ({
      ...prev,
      [riscoId]: {
        ...prev[riscoId],
        [campo]: valor,
      },
    }));
  };

  const handleSalvarResposta = async (riscoId: string) => {
    const resp = respostasLocal[riscoId];
    if (!resp?.estrategia) {
      alert('Selecione uma estrategia');
      return;
    }

    await adicionarResposta(
      riscoId,
      resp.estrategia,
      resp.acao || '',
      resp.responsavel || '',
      '', // responsavel_area
      undefined // prazo
    );

    setRiscoExpandido(null);
  };

  const handleFinalizar = async () => {
    // Verificar se todos os riscos CRITICOS e ALTOS tem resposta definida
    const riscosAltos = riscos.filter(
      (r) => r.nivel_risco === 'CRITICO' || r.nivel_risco === 'ALTO'
    );

    const semResposta = riscosAltos.filter((r) => !respostasLocal[r.id]?.estrategia);

    if (semResposta.length > 0) {
      const confirmar = window.confirm(
        `Existem ${semResposta.length} risco(s) de nivel ALTO/CRITICO sem resposta definida. Deseja finalizar mesmo assim?`
      );
      if (!confirmar) return;
    }

    // Salvar todas as respostas pendentes
    for (const [riscoId, resp] of Object.entries(respostasLocal)) {
      if (resp.estrategia) {
        await adicionarResposta(
          riscoId,
          resp.estrategia,
          resp.acao || '',
          resp.responsavel || '',
          '',
          undefined
        );
      }
    }

    await finalizarAnalise();
    onFinalizar();
  };

  // Ordenar riscos por nivel (CRITICO primeiro)
  const riscosOrdenados = [...riscos].sort((a, b) => {
    const ordem: Record<NivelRisco, number> = { CRITICO: 0, ALTO: 1, MEDIO: 2, BAIXO: 3 };
    return ordem[a.nivel_risco] - ordem[b.nivel_risco];
  });

  return (
    <div>
      <h3>Etapa 5: Estrategias de Resposta</h3>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Defina como tratar cada risco identificado. Priorize os riscos CRITICOS e ALTOS.
      </p>

      {/* Legenda de estrategias */}
      <div
        style={{
          padding: '15px',
          background: '#f0f9ff',
          borderRadius: '8px',
          marginBottom: '20px',
        }}
      >
        <h4 style={{ marginTop: 0, marginBottom: '10px' }}>Estrategias Disponiveis</h4>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '15px' }}>
          {ESTRATEGIAS.map((est) => (
            <div key={est} style={{ flex: '1 1 180px' }}>
              <strong>{est}</strong>
              <div style={{ fontSize: '13px', color: '#666' }}>
                {DESCRICOES_ESTRATEGIA[est]}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Lista de riscos para definir resposta */}
      <div style={{ marginBottom: '20px' }}>
        {riscosOrdenados.map((risco) => {
          const respLocal = respostasLocal[risco.id] || {};
          const isExpandido = riscoExpandido === risco.id;

          return (
            <div
              key={risco.id}
              style={{
                marginBottom: '10px',
                padding: '15px',
                background: 'white',
                borderRadius: '8px',
                border: '1px solid #e5e7eb',
                borderLeft: `4px solid ${CORES_NIVEL[risco.nivel_risco]}`,
              }}
            >
              {/* Header do risco */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  cursor: 'pointer',
                }}
                onClick={() => setRiscoExpandido(isExpandido ? null : risco.id)}
              >
                <div>
                  <strong>{risco.titulo}</strong>
                  <div style={{ fontSize: '13px', color: '#666' }}>
                    {risco.categoria} | Score: {risco.score_risco}
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  {respLocal.estrategia && (
                    <span
                      style={{
                        padding: '4px 8px',
                        background: '#dbeafe',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: 'bold',
                      }}
                    >
                      {respLocal.estrategia}
                    </span>
                  )}
                  <span
                    style={{
                      padding: '4px 12px',
                      background: CORES_NIVEL[risco.nivel_risco],
                      color: 'white',
                      borderRadius: '4px',
                      fontSize: '12px',
                      fontWeight: 'bold',
                    }}
                  >
                    {risco.nivel_risco}
                  </span>
                  <span>{isExpandido ? '▼' : '▶'}</span>
                </div>
              </div>

              {/* Formulario de resposta */}
              {isExpandido && (
                <div style={{ marginTop: '15px', paddingTop: '15px', borderTop: '1px solid #e5e7eb' }}>
                  <div style={{ marginBottom: '15px' }}>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                      Estrategia de Resposta *
                    </label>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
                      {ESTRATEGIAS.map((est) => (
                        <button
                          key={est}
                          onClick={() => handleSetResposta(risco.id, 'estrategia', est)}
                          style={{
                            padding: '8px 16px',
                            border: respLocal.estrategia === est ? '2px solid #3b82f6' : '1px solid #ddd',
                            borderRadius: '4px',
                            background: respLocal.estrategia === est ? '#eff6ff' : 'white',
                            cursor: 'pointer',
                            fontWeight: respLocal.estrategia === est ? 'bold' : 'normal',
                          }}
                        >
                          {est}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div style={{ marginBottom: '15px' }}>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                      Acao Planejada
                    </label>
                    <textarea
                      value={respLocal.acao || ''}
                      onChange={(e) => handleSetResposta(risco.id, 'acao', e.target.value)}
                      placeholder="Descreva a acao a ser tomada..."
                      rows={2}
                      style={{ width: '100%', padding: '8px' }}
                    />

                    {/* Sugestoes de acao */}
                    {respLocal.estrategia && (
                      <div style={{ marginTop: '10px' }}>
                        <span style={{ fontSize: '13px', color: '#666', marginBottom: '5px', display: 'block' }}>
                          Sugestoes (clique para usar):
                        </span>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                          {getSugestoes(risco.categoria as CategoriaRisco, respLocal.estrategia).map((sug, idx) => (
                            <button
                              key={idx}
                              type="button"
                              onClick={() => {
                                const acaoAtual = respLocal.acao || '';
                                const novaAcao = acaoAtual ? `${acaoAtual}; ${sug}` : sug;
                                handleSetResposta(risco.id, 'acao', novaAcao);
                              }}
                              style={{
                                padding: '4px 10px',
                                fontSize: '12px',
                                background: '#f3f4f6',
                                border: '1px solid #d1d5db',
                                borderRadius: '12px',
                                cursor: 'pointer',
                                color: '#374151',
                              }}
                              title={`Clique para adicionar: "${sug}"`}
                            >
                              + {sug}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  <div style={{ marginBottom: '15px' }}>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                      Responsavel
                    </label>
                    <input
                      type="text"
                      value={respLocal.responsavel || ''}
                      onChange={(e) => handleSetResposta(risco.id, 'responsavel', e.target.value)}
                      placeholder="Nome ou cargo do responsavel..."
                      style={{ width: '100%', padding: '8px' }}
                    />
                  </div>

                  <button
                    onClick={() => handleSalvarResposta(risco.id)}
                    disabled={!respLocal.estrategia}
                    style={{
                      padding: '8px 16px',
                      background: respLocal.estrategia ? '#10b981' : '#d1d5db',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: respLocal.estrategia ? 'pointer' : 'not-allowed',
                    }}
                  >
                    Confirmar Resposta
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Resumo */}
      <div
        style={{
          padding: '15px',
          background: '#f0fdf4',
          borderRadius: '8px',
          marginBottom: '20px',
        }}
      >
        <h4 style={{ marginTop: 0 }}>Resumo</h4>
        <p>
          Total de riscos: <strong>{riscos.length}</strong>
        </p>
        <p>
          Com resposta definida:{' '}
          <strong>
            {Object.values(respostasLocal).filter((r) => r.estrategia).length}
          </strong>
        </p>
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
          onClick={handleFinalizar}
          disabled={loading}
          style={{
            padding: '12px 30px',
            background: loading ? '#9ca3af' : '#10b981',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontWeight: 'bold',
          }}
        >
          {loading ? 'Finalizando...' : 'Finalizar Analise ✓'}
        </button>
      </div>
    </div>
  );
};

export default Etapa5Resposta;
