/**
 * PEChatIntro - Card de introdução ao modelo selecionado
 *
 * Apresenta o modelo, explica como funciona e oferece 3 opções:
 * Começar, Ver Exemplos, Entender Método.
 */

import React from 'react';
import Button from '../ui/Button';
import type { ModeloPlanejamento } from '../../types/planejamento';

interface PEChatIntroProps {
  modelo: ModeloPlanejamento;
  loading: boolean;
  onIniciarAgente: () => void;
  onVerExemplos: () => void;
  onEntenderMetodo: () => void;
  onVoltar: () => void;
}

export const PEChatIntro: React.FC<PEChatIntroProps> = ({
  modelo,
  loading,
  onIniciarAgente,
  onVerExemplos,
  onEntenderMetodo,
  onVoltar,
}) => {
  return (
    <div style={{ alignSelf: 'flex-start', maxWidth: '85%' }}>
      <div style={{
        padding: '24px',
        borderRadius: '16px',
        background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.9) 100%)',
        backdropFilter: 'blur(10px)',
        border: '2px solid rgba(27, 79, 114, 0.3)',
        boxShadow: '0 8px 24px rgba(27, 79, 114, 0.15)',
        fontSize: '15px',
        lineHeight: 1.7,
        color: '#2C3E50'
      }}>
        <div style={{ fontSize: '48px', marginBottom: '16px', textAlign: 'center' }}>
          {modelo.icone}
        </div>
        <h3 style={{
          fontSize: '22px',
          fontWeight: 'bold',
          marginBottom: '12px',
          color: '#1B4F72',
          textAlign: 'center'
        }}>
          Bem-vindo ao {modelo.nome}!
        </h3>
        <p style={{ marginBottom: '16px', textAlign: 'center', opacity: 0.9 }}>
          {modelo.descricao}
        </p>

        <div style={{
          background: 'rgba(27, 79, 114, 0.08)',
          padding: '16px',
          borderRadius: '12px',
          marginBottom: '20px'
        }}>
          <p style={{ fontWeight: 600, marginBottom: '8px', color: '#1B4F72' }}>
            Como funciona:
          </p>
          <ul style={{ margin: 0, paddingLeft: '20px', listStyleType: 'disc' }}>
            <li>Vou fazer perguntas para entender seu contexto</li>
            <li>Você responde de forma livre e natural</li>
            <li>Juntos, vamos construir seu planejamento estratégico</li>
            <li>Use o workspace ao lado para visualizar o progresso</li>
          </ul>
        </div>

        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
          alignItems: 'center'
        }}>
          <Button
            onClick={onIniciarAgente}
            disabled={loading}
            style={{
              background: loading ? '#ccc' : 'linear-gradient(135deg, #1B4F72 0%, #2874A6 100%)',
              color: '#fff',
              padding: '14px 40px',
              borderRadius: '8px',
              border: 'none',
              fontWeight: 700,
              fontSize: '17px',
              cursor: loading ? 'not-allowed' : 'pointer',
              boxShadow: '0 4px 12px rgba(27, 79, 114, 0.3)',
              width: '100%',
              maxWidth: '300px'
            }}
          >
            {loading ? '⏳ Iniciando...' : '🚀 Começar Construção'}
          </Button>

          <div style={{
            display: 'flex',
            gap: '8px',
            flexWrap: 'wrap',
            justifyContent: 'center'
          }}>
            <Button
              onClick={onVerExemplos}
              disabled={loading}
              style={{
                background: 'rgba(27, 79, 114, 0.1)',
                color: '#1B4F72',
                padding: '10px 20px',
                borderRadius: '6px',
                border: '1px solid rgba(27, 79, 114, 0.3)',
                fontWeight: 600,
                fontSize: '14px',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              📊 Ver Exemplos
            </Button>
            <Button
              onClick={onEntenderMetodo}
              disabled={loading}
              style={{
                background: 'rgba(27, 79, 114, 0.1)',
                color: '#1B4F72',
                padding: '10px 20px',
                borderRadius: '6px',
                border: '1px solid rgba(27, 79, 114, 0.3)',
                fontWeight: 600,
                fontSize: '14px',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              💡 Entender Método
            </Button>
          </div>

          <Button
            onClick={onVoltar}
            disabled={loading}
            style={{
              background: 'transparent',
              color: '#6b7280',
              padding: '8px 20px',
              borderRadius: '6px',
              border: 'none',
              fontWeight: 500,
              fontSize: '14px',
              cursor: loading ? 'not-allowed' : 'pointer',
              marginTop: '8px'
            }}
          >
            ← Escolher outro modelo
          </Button>
        </div>
      </div>
    </div>
  );
};

export default PEChatIntro;
