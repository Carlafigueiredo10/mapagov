/**
 * PEModeloGrid - Grid de seleção de modelos do Planejamento Estratégico
 *
 * Componente presentacional: recebe modelos e callbacks, sem estado próprio.
 */

import React, { useState } from 'react';
import Card from '../ui/Card';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import type { ModeloPlanejamento } from '../../types/planejamento';

interface PEModeloGridProps {
  modelos: Record<string, ModeloPlanejamento>;
  loading: boolean;
  onSelecionarModelo: (modeloId: string) => void;
  onAbrirInfo: (modeloId: string) => void;
  onVoltar: () => void;
}

export const PEModeloGrid: React.FC<PEModeloGridProps> = ({
  modelos,
  loading,
  onSelecionarModelo,
  onAbrirInfo,
  onVoltar,
}) => {
  const [hover, setHover] = useState<string | null>(null);

  return (
    <div style={{ maxWidth: '1400px', width: '100%', zIndex: 1 }}>
      <h1 style={{ fontSize: '42px', fontWeight: 'bold', marginBottom: '20px', textAlign: 'center' }}>
        Escolha seu modelo de planejamento
      </h1>
      <p style={{ fontSize: '20px', opacity: 0.95, marginBottom: '56px', textAlign: 'center' }}>
        Cada modelo foi criado para um tipo diferente de desafio.
      </p>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '36px',
        marginBottom: '48px'
      }}>
        {Object.values(modelos).map((modelo) => (
          <div key={modelo.id} style={{ position: 'relative' }}>
            <Card
              variant="glass"
              onClick={() => onSelecionarModelo(modelo.id)}
              style={{
                cursor: loading ? 'wait' : 'pointer',
                transform: hover === modelo.id ? 'scale(1.06) translateY(-8px)' : 'scale(1)',
                transition: 'all 0.35s ease',
                boxShadow: hover === modelo.id ? '0 24px 48px rgba(0,0,0,0.35)' : '0 10px 20px rgba(0,0,0,0.25)',
                minHeight: '280px',
                opacity: loading ? 0.6 : 1
              }}
              onMouseEnter={() => !loading && setHover(modelo.id)}
              onMouseLeave={() => setHover(null)}
            >
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onAbrirInfo(modelo.id);
                }}
                style={{
                  position: 'absolute',
                  top: '16px',
                  right: '16px',
                  background: 'rgba(52, 152, 219, 0.9)',
                  border: 'none',
                  borderRadius: '50%',
                  width: '36px',
                  height: '36px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  fontSize: '18px',
                  color: '#ffffff',
                  boxShadow: '0 4px 12px rgba(52, 152, 219, 0.4)',
                  transition: 'all 0.2s ease',
                  zIndex: 10
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'scale(1.1)';
                  e.currentTarget.style.background = 'rgba(52, 152, 219, 1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'scale(1)';
                  e.currentTarget.style.background = 'rgba(52, 152, 219, 0.9)';
                }}
                title={`Saiba mais sobre ${modelo.nome}`}
              >
                ℹ️
              </button>

              <div style={{ fontSize: '64px', marginBottom: '20px' }}>{modelo.icone}</div>
              <h3 style={{ fontSize: '26px', fontWeight: 'bold', marginBottom: '12px' }}>
                {modelo.nome}
              </h3>
              <p style={{ fontSize: '15px', opacity: 0.9, marginBottom: '20px', minHeight: '70px' }}>
                {modelo.descricao}
              </p>
              <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '16px' }}>
                {modelo.tags.map((tag) => (
                  <Badge key={tag} variant="outline">{tag}</Badge>
                ))}
              </div>
              <div style={{ fontSize: '13px', opacity: 0.75, borderTop: '1px solid rgba(255,255,255,0.2)', paddingTop: '12px' }}>
                📊 {modelo.complexidade} | ⏱️ {modelo.prazo}
              </div>
            </Card>
          </div>
        ))}
      </div>

      {loading && (
        <div style={{ textAlign: 'center', marginBottom: '24px', fontSize: '18px' }}>
          ⏳ Iniciando sessão com Helena...
        </div>
      )}

      <div style={{ textAlign: 'center' }}>
        <Button variant="outline" onClick={onVoltar} size="lg" disabled={loading}>
          ← Voltar
        </Button>
      </div>
    </div>
  );
};

export default PEModeloGrid;
