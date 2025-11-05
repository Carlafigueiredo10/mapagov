/**
 * Página do Mapa de Exclusões e Restrições
 * Domínio 2 - Escopo e Valor
 */
import React from 'react';
import ArtefatoPage from './ArtefatoPage';
import MapaExclusoes from '../components/Helena/artefatos/MapaExclusoes';

export const MapaExclusoesPage: React.FC = () => {
  return (
    <ArtefatoPage>
      <MapaExclusoes />
    </ArtefatoPage>
  );
};

export default MapaExclusoesPage;
