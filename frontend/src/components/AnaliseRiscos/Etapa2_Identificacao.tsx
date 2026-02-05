/**
 * Etapa2_Identificacao - Identificar e listar riscos
 */
import React, { useState } from 'react';
import { useAnaliseRiscosStore } from '../../store/analiseRiscosStore';
import {
  CategoriaRisco,
  DESCRICOES_CATEGORIA,
} from '../../types/analiseRiscos.types';

interface Props {
  onAvancar: () => void;
  onVoltar: () => void;
}

const CATEGORIAS: CategoriaRisco[] = [
  'OPERACIONAL',
  'FINANCEIRO',
  'LEGAL',
  'REPUTACIONAL',
  'TECNOLOGICO',
  'IMPACTO_DESIGUAL',
];

const Etapa2Identificacao: React.FC<Props> = ({ onAvancar, onVoltar }) => {
  const { currentAnalise, adicionarRisco, removerRisco } =
    useAnaliseRiscosStore();

  // Estado do form
  const [titulo, setTitulo] = useState('');
  const [categoria, setCategoria] = useState<CategoriaRisco>('OPERACIONAL');
  const [probabilidade, setProbabilidade] = useState<number | undefined>(undefined);
  const [impacto, setImpacto] = useState<number | undefined>(undefined);

  const riscos = currentAnalise?.riscos || [];

  const handleAdicionarRisco = async () => {
    if (!titulo.trim()) {
      alert('Informe o titulo do risco');
      return;
    }
    if (probabilidade === undefined || impacto === undefined) {
      alert('Selecione probabilidade e impacto antes de adicionar');
      return;
    }
    await adicionarRisco(titulo, undefined, categoria, probabilidade, impacto);
    // Limpar form
    setTitulo('');
    setCategoria('OPERACIONAL');
    setProbabilidade(undefined);
    setImpacto(undefined);
  };

  const handleRemoverRisco = async (riscoId: string) => {
    if (confirm('Remover este risco?')) {
      await removerRisco(riscoId);
    }
  };

  return (
    <div>
      <h3>Etapa 2: Identificacao de Riscos</h3>

      {/* Form para adicionar risco */}
      <div
        style={{
          padding: '15px',
          background: '#f9fafb',
          borderRadius: '8px',
          marginBottom: '20px',
        }}
      >
        <h4 style={{ marginTop: 0 }}>Adicionar Risco</h4>

        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px' }}>
            Titulo do Risco: *
          </label>
          <input
            type="text"
            value={titulo}
            onChange={(e) => setTitulo(e.target.value)}
            placeholder="Ex: Falha no sistema de pagamentos"
            style={{ width: '100%', padding: '8px' }}
          />
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px' }}>
            Categoria:
          </label>
          <select
            value={categoria}
            onChange={(e) => setCategoria(e.target.value as CategoriaRisco)}
            style={{ width: '100%', padding: '8px' }}
          >
            {CATEGORIAS.map((cat) => (
              <option key={cat} value={cat}>
                {cat} - {DESCRICOES_CATEGORIA[cat]}
              </option>
            ))}
          </select>
        </div>

        <div style={{ display: 'flex', gap: '15px', marginBottom: '15px' }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>
              Probabilidade (1-5): *
            </label>
            <select
              value={probabilidade ?? ''}
              onChange={(e) => setProbabilidade(e.target.value ? Number(e.target.value) : undefined)}
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
              value={impacto ?? ''}
              onChange={(e) => setImpacto(e.target.value ? Number(e.target.value) : undefined)}
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

        <button
          onClick={handleAdicionarRisco}
          style={{
            padding: '10px 20px',
            background: '#10b981',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          + Adicionar Risco
        </button>
      </div>

      {/* Lista de riscos */}
      <div
        style={{
          padding: '15px',
          background: '#f9fafb',
          borderRadius: '8px',
          marginBottom: '20px',
        }}
      >
        <h4 style={{ marginTop: 0 }}>
          Riscos Identificados ({riscos.length})
        </h4>

        {riscos.length === 0 ? (
          <p style={{ color: '#666' }}>Nenhum risco adicionado ainda.</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #ddd' }}>
                <th style={{ textAlign: 'left', padding: '8px' }}>Titulo</th>
                <th style={{ textAlign: 'left', padding: '8px' }}>Categoria</th>
                <th style={{ textAlign: 'center', padding: '8px' }}>P</th>
                <th style={{ textAlign: 'center', padding: '8px' }}>I</th>
                <th style={{ textAlign: 'center', padding: '8px' }}>Score</th>
                <th style={{ textAlign: 'center', padding: '8px' }}>Nivel</th>
                <th style={{ textAlign: 'center', padding: '8px' }}>Acoes</th>
              </tr>
            </thead>
            <tbody>
              {riscos.map((risco) => (
                <tr key={risco.id} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '8px' }}>{risco.titulo}</td>
                  <td style={{ padding: '8px' }}>{risco.categoria}</td>
                  <td style={{ padding: '8px', textAlign: 'center' }}>
                    {risco.probabilidade}
                  </td>
                  <td style={{ padding: '8px', textAlign: 'center' }}>
                    {risco.impacto}
                  </td>
                  <td style={{ padding: '8px', textAlign: 'center' }}>
                    {risco.score_risco}
                  </td>
                  <td style={{ padding: '8px', textAlign: 'center' }}>
                    <span
                      style={{
                        padding: '2px 8px',
                        borderRadius: '4px',
                        background:
                          risco.nivel_risco === 'CRITICO'
                            ? '#ef4444'
                            : risco.nivel_risco === 'ALTO'
                            ? '#f97316'
                            : risco.nivel_risco === 'MEDIO'
                            ? '#eab308'
                            : '#22c55e',
                        color: 'white',
                        fontSize: '12px',
                      }}
                    >
                      {risco.nivel_risco}
                    </span>
                  </td>
                  <td style={{ padding: '8px', textAlign: 'center' }}>
                    <button
                      onClick={() => handleRemoverRisco(risco.id)}
                      style={{
                        padding: '4px 8px',
                        background: '#ef4444',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '12px',
                      }}
                    >
                      Remover
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
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
          Avancar →
        </button>
      </div>
    </div>
  );
};

export default Etapa2Identificacao;
