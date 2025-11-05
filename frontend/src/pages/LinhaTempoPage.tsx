/**
 * Página da Linha do Tempo Inicial
 */
import React from 'react';
import ArtefatoPage from './ArtefatoPage';
import LinhaTempoInicial from '../components/Helena/artefatos/LinhaTempoInicial';

export const LinhaTempoPage: React.FC = () => {
  return (
    <ArtefatoPage>
      <LinhaTempoInicial />
    </ArtefatoPage>
  );
};

export default LinhaTempoPage;
