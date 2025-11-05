/**
 * Wrapper Page para Artefatos do Domínio 1
 * Fornece layout consistente com navegação
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import './ArtefatoPage.css';

interface ArtefatoPageProps {
  children: React.ReactNode;
}

export const ArtefatoPage: React.FC<ArtefatoPageProps> = ({ children }) => {
  const navigate = useNavigate();

  return (
    <div className="artefato-page">
      <div className="artefato-page-header">
        <button
          className="btn-voltar-artefato"
          onClick={() => navigate('/planejamento-estrategico')}
        >
          ← Voltar para Planejamento Estratégico
        </button>
      </div>

      <div className="artefato-page-content">
        {children}
      </div>

      <div className="artefato-page-footer">
        <button
          className="btn-footer-secondary"
          onClick={() => navigate('/planejamento-estrategico')}
        >
          ← Voltar
        </button>
        <button
          className="btn-footer-secondary"
          onClick={() => navigate('/dominio1')}
        >
          📖 Ver Domínio Completo
        </button>
      </div>
    </div>
  );
};

export default ArtefatoPage;
