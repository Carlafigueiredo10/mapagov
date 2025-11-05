/**
 * Página do Painel de Indicadores
 * Domínio 2 - Escopo e Valor
 */
import React from 'react';
import ArtefatoPage from './ArtefatoPage';
import PainelIndicadores from '../components/Helena/artefatos/PainelIndicadores';

export const PainelIndicadoresPage: React.FC = () => {
  return (
    <ArtefatoPage>
      <PainelIndicadores />
    </ArtefatoPage>
  );
};

export default PainelIndicadoresPage;
