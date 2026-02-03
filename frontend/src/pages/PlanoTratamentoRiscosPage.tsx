/**
 * PlanoTratamentoRiscosPage - Placeholder
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';

const PlanoTratamentoRiscosPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div style={{ padding: '40px', textAlign: 'center' }}>
      <h2>Plano de Tratamento de Riscos</h2>
      <p style={{ color: '#666' }}>Em construcao...</p>
      <button
        onClick={() => navigate(-1)}
        style={{ marginTop: '20px', padding: '10px 20px', cursor: 'pointer' }}
      >
        ← Voltar
      </button>
    </div>
  );
};

export default PlanoTratamentoRiscosPage;
