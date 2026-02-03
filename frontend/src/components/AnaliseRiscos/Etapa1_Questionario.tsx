/**
 * Etapa1_Questionario - Criar analise e preencher questionario
 */
import React, { useState, useEffect } from 'react';
import { useAnaliseRiscosStore } from '../../store/analiseRiscosStore';
import { AREAS_DECIPEX } from '../../types/analiseRiscos.types';

interface Props {
  tipoOrigem?: string;
  origemId?: string;
  onAvancar: () => void;
}

const Etapa1Questionario: React.FC<Props> = ({
  tipoOrigem: tipoOrigemProp,
  origemId: origemIdProp,
  onAvancar,
}) => {
  const {
    currentAnaliseId,
    currentAnalise,
    criarAnalise,
    salvarQuestionario,
    carregarAnalise,
  } = useAnaliseRiscosStore();

  // Estado local do form
  const [tipoOrigem, setTipoOrigem] = useState(tipoOrigemProp || 'POP');
  const [origemId, setOrigemId] = useState(origemIdProp || '');
  const [areaDecipex, setAreaDecipex] = useState('');

  // Carregar dados existentes se tiver analise
  useEffect(() => {
    if (currentAnalise) {
      setAreaDecipex(currentAnalise.area_decipex || '');
    }
  }, [currentAnalise]);

  const handleCriarAnalise = async () => {
    if (!origemId.trim()) {
      alert('Informe o ID da origem');
      return;
    }
    const novoId = await criarAnalise(tipoOrigem, origemId);
    if (novoId) {
      await carregarAnalise(novoId);
    }
  };

  const handleSalvarQuestionario = async () => {
    if (!areaDecipex) {
      alert('Selecione a area DECIPEX');
      return;
    }
    await salvarQuestionario({ Q_CONTEXTO_01: areaDecipex }, areaDecipex, 2);
  };

  const handleAvancar = async () => {
    // Se nao tem analise, criar
    if (!currentAnaliseId) {
      if (!origemId.trim()) {
        alert('Informe o ID da origem para criar a analise');
        return;
      }
      const novoId = await criarAnalise(tipoOrigem, origemId);
      if (!novoId) return;
      await carregarAnalise(novoId);
    }

    // Salvar questionario se tiver area
    if (areaDecipex) {
      await salvarQuestionario({ Q_CONTEXTO_01: areaDecipex }, areaDecipex, 2);
    }

    onAvancar();
  };

  return (
    <div>
      <h3>Etapa 1: Questionario de Contexto</h3>

      {/* Se nao tem analise, mostrar form de criacao */}
      {!currentAnaliseId && (
        <div
          style={{
            padding: '15px',
            background: '#f9fafb',
            borderRadius: '8px',
            marginBottom: '20px',
          }}
        >
          <h4 style={{ marginTop: 0 }}>Criar Nova Analise</h4>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>
              Tipo de Origem:
            </label>
            <select
              value={tipoOrigem}
              onChange={(e) => setTipoOrigem(e.target.value)}
              style={{ width: '100%', padding: '8px' }}
            >
              <option value="POP">POP</option>
              <option value="PROCESSO">Processo</option>
              <option value="PROJETO">Projeto</option>
            </select>
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>
              ID da Origem (UUID):
            </label>
            <input
              type="text"
              value={origemId}
              onChange={(e) => setOrigemId(e.target.value)}
              placeholder="Ex: 550e8400-e29b-41d4-a716-446655440000"
              style={{ width: '100%', padding: '8px' }}
            />
          </div>

          <button
            onClick={handleCriarAnalise}
            style={{
              padding: '10px 20px',
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Criar Analise
          </button>
        </div>
      )}

      {/* Questionario */}
      <div
        style={{
          padding: '15px',
          background: '#f9fafb',
          borderRadius: '8px',
          marginBottom: '20px',
        }}
      >
        <h4 style={{ marginTop: 0 }}>Questionario</h4>

        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px' }}>
            Area DECIPEX Responsavel: *
          </label>
          <select
            value={areaDecipex}
            onChange={(e) => setAreaDecipex(e.target.value)}
            style={{ width: '100%', padding: '8px' }}
          >
            <option value="">Selecione...</option>
            {AREAS_DECIPEX.map((area) => (
              <option key={area.codigo} value={area.codigo}>
                {area.codigo} - {area.nome}
              </option>
            ))}
          </select>
        </div>

        {currentAnaliseId && (
          <button
            onClick={handleSalvarQuestionario}
            style={{
              padding: '8px 16px',
              background: '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              marginRight: '10px',
            }}
          >
            Salvar Questionario
          </button>
        )}
      </div>

      {/* Botao avancar */}
      <div style={{ textAlign: 'right' }}>
        <button
          onClick={handleAvancar}
          style={{
            padding: '10px 30px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '16px',
          }}
        >
          Avancar →
        </button>
      </div>
    </div>
  );
};

export default Etapa1Questionario;
