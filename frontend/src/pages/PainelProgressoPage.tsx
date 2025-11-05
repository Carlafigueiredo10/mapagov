import React from 'react';
import ArtefatoPage from './ArtefatoPage';
import PainelProgressoOperacional from '../components/Helena/artefatos/PainelProgressoOperacional';

export const PainelProgressoPage: React.FC = () => {
  return (
    <ArtefatoPage>
      <PainelProgressoOperacional />
    </ArtefatoPage>
  );
};

export default PainelProgressoPage;
