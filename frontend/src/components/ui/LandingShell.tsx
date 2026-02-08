/**
 * LandingShell - Layout padrão para páginas de landing institucional
 *
 * Encapsula: fundo cinza, card branco com sombra, botão voltar opcional.
 * Reutilizado por todas as landings (Riscos, POP, PE).
 */
import React from 'react';

interface LandingShellProps {
  children: React.ReactNode;
  maxWidth?: string;
  onBack?: () => void;
}

const LandingShell: React.FC<LandingShellProps> = ({ children, maxWidth = '1140px', onBack }) => {
  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5', padding: '20px' }}>
      <div style={{ maxWidth, margin: '0 auto' }}>
        {onBack && (
          <button
            onClick={onBack}
            style={{
              padding: '8px 16px',
              background: '#6b7280',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              marginBottom: '20px',
            }}
          >
            ← Voltar
          </button>
        )}

        <div style={{ background: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          {children}
        </div>
      </div>
    </div>
  );
};

export default LandingShell;
