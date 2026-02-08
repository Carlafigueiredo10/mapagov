/**
 * MapeamentoProcessosPage - Página dedicada para Mapeamento de Atividades (POP)
 *
 * Rota: /chat
 *
 * Fluxo:
 * 1. Exibe landing institucional (enquadramento)
 * 2. Ao clicar em "Iniciar mapeamento da atividade", exibe o chat
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MapeamentoProcessosLanding from '../components/Helena/MapeamentoProcessosLanding';
import ChatContainer from '../components/Helena/ChatContainer';
import FormularioPOP from '../components/Helena/FormularioPOP';

const MapeamentoProcessosPage: React.FC = () => {
  const navigate = useNavigate();
  const [mostrarChat, setMostrarChat] = useState(false);

  const handleIniciarMapeamento = () => {
    setMostrarChat(true);
  };

  // Landing institucional (enquadramento)
  if (!mostrarChat) {
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
            <MapeamentoProcessosLanding onIniciar={handleIniciarMapeamento} />
          </div>
        </div>
      </div>
    );
  }

  // Chat de mapeamento
  return (
    <div className="app-container">
      <div className="chat-section">
        <ChatContainer />
      </div>
      <FormularioPOP />
    </div>
  );
};

export default MapeamentoProcessosPage;
