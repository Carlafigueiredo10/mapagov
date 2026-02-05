/**
 * AnaliseRiscosPage - Pagina dedicada para Analise de Riscos (BETA)
 *
 * Rota: /riscos
 *
 * Fluxo:
 * 1. Exibe landing institucional (enquadramento)
 * 2. Ao clicar em "Iniciar análise de riscos", exibe o wizard
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { WizardAnaliseRiscos, AnaliseRiscosLanding } from '../components/AnaliseRiscos';

const AnaliseRiscosPage: React.FC = () => {
  const navigate = useNavigate();
  const [mostrarWizard, setMostrarWizard] = useState(false);

  const handleIniciarAnalise = () => {
    setMostrarWizard(true);
  };

  // Landing institucional (enquadramento)
  if (!mostrarWizard) {
    return (
      <div style={{ minHeight: '100vh', background: '#f5f5f5', padding: '20px' }}>
        <div style={{ maxWidth: '1140px', margin: '0 auto' }}>
          <button
            onClick={() => navigate(-1)}
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

          <div style={{ background: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <AnaliseRiscosLanding onIniciar={handleIniciarAnalise} />
          </div>
        </div>
      </div>
    );
  }

  // Wizard de análise de riscos
  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5', padding: '20px' }}>
      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        <button
          onClick={() => navigate(-1)}
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

        <div style={{ background: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <WizardAnaliseRiscos />
        </div>
      </div>
    </div>
  );
};

export default AnaliseRiscosPage;
