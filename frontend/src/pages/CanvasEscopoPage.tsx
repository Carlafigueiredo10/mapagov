/**
 * Página do Canvas de Escopo e Valor
 * Domínio 2 - Escopo e Valor
 */
import React from 'react';
import ArtefatoPage from './ArtefatoPage';
import CanvasEscopoValor from '../components/Helena/artefatos/CanvasEscopoValor';

export const CanvasEscopoPage: React.FC = () => {
  return (
    <ArtefatoPage>
      <CanvasEscopoValor />
    </ArtefatoPage>
  );
};

export default CanvasEscopoPage;
