/**
 * Página da Matriz RACI
 * Domínio 2 - Escopo e Valor
 */
import React from 'react';
import ArtefatoPage from './ArtefatoPage';
import MatrizRACI from '../components/Helena/artefatos/MatrizRACI';

export const MatrizRACIPage: React.FC = () => {
  return (
    <ArtefatoPage>
      <MatrizRACI />
    </ArtefatoPage>
  );
};

export default MatrizRACIPage;
