/**
 * Página do Canvas de Projeto Público
 */
import React from 'react';
import ArtefatoPage from './ArtefatoPage';
import CanvasProjetoPublico from '../components/Helena/artefatos/CanvasProjetoPublico';

export const CanvasPage: React.FC = () => {
  return (
    <ArtefatoPage>
      <CanvasProjetoPublico />
    </ArtefatoPage>
  );
};

export default CanvasPage;
