/**
 * MatrizRiscosControlesPage - Placeholder
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';

const MatrizRiscosControlesPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div style={{ padding: '40px', textAlign: 'center' }}>
      <h2>Matriz de Riscos e Controles</h2>
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

export default MatrizRiscosControlesPage;
