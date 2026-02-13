/**
 * PEDiagnostico - Tela de diagnóstico guiado do Planejamento Estratégico
 *
 * Componente presentacional: recebe estado e callbacks, sem lógica própria.
 */

import React from 'react';
import Card from '../ui/Card';
import Button from '../ui/Button';
import type { PerguntaDiagnostico } from '../../types/planejamento';

interface PEDiagnosticoProps {
  perguntas: PerguntaDiagnostico[];
  perguntaAtual: number;
  loading: boolean;
  onResponder: (opcaoSelecionada: string) => void;
  onCancelar: () => void;
}

export const PEDiagnostico: React.FC<PEDiagnosticoProps> = ({
  perguntas,
  perguntaAtual,
  loading,
  onResponder,
  onCancelar,
}) => {
  const pergunta = perguntas[perguntaAtual];

  return (
    <div style={{ maxWidth: '800px', width: '100%', zIndex: 1 }}>
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <div style={{ fontSize: '64px', marginBottom: '24px' }}>🩺</div>
        <h1 style={{ fontSize: '36px', fontWeight: 'bold', marginBottom: '16px' }}>
          Diagnóstico Guiado
        </h1>
        <p style={{ fontSize: '18px', opacity: 0.9 }}>
          Pergunta {perguntaAtual + 1} de {perguntas.length}
        </p>
      </div>

      <Card variant="glass" style={{ marginBottom: '32px', textAlign: 'center' }}>
        <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '32px', lineHeight: 1.5 }}>
          {pergunta.texto}
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {pergunta.opcoes.map((opcao) => (
            <Button
              key={opcao.valor}
              variant="outline"
              onClick={() => onResponder(opcao.valor)}
              disabled={loading}
              size="lg"
              style={{
                fontSize: '16px',
                padding: '20px 24px',
                textAlign: 'left',
                justifyContent: 'flex-start',
                opacity: loading ? 0.6 : 1
              }}
            >
              {opcao.texto}
            </Button>
          ))}
        </div>
      </Card>

      {loading && (
        <div style={{ textAlign: 'center', fontSize: '18px', marginBottom: '24px' }}>
          ⏳ Processando diagnóstico...
        </div>
      )}

      {/* Barra de Progresso */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.1)',
        borderRadius: '12px',
        height: '8px',
        overflow: 'hidden',
        marginBottom: '24px'
      }}>
        <div style={{
          background: 'linear-gradient(90deg, #3498DB, #27AE60)',
          height: '100%',
          width: `${((perguntaAtual + 1) / perguntas.length) * 100}%`,
          transition: 'width 0.3s ease'
        }} />
      </div>

      <div style={{ textAlign: 'center' }}>
        <Button
          variant="outline"
          onClick={onCancelar}
          size="md"
          disabled={loading}
        >
          ← Cancelar
        </Button>
      </div>
    </div>
  );
};

export default PEDiagnostico;
