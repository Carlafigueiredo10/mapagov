import React from 'react';
import ArtefatoPage from './ArtefatoPage';
import MapaPapeisRaci from '../components/Helena/artefatos/MapaPapeisRaci';

export const MapaPapeisPage: React.FC = () => {
  return (
    <ArtefatoPage>
      <MapaPapeisRaci />
    </ArtefatoPage>
  );
};

export default MapaPapeisPage;
