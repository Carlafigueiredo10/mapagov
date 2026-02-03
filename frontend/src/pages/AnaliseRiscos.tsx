/**
 * AnaliseRiscosPage - Pagina dedicada para Analise de Riscos (BETA)
 *
 * Rota: /riscos
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { WizardAnaliseRiscos } from '../components/AnaliseRiscos';

const AnaliseRiscosPage: React.FC = () => {
  const navigate = useNavigate();

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
