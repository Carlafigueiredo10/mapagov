import React from 'react';
import ArtefatoPage from './ArtefatoPage';
import CronogramaTimeline from '../components/Helena/artefatos/CronogramaTimeline';

export const CronogramaPage: React.FC = () => {
  return (
    <ArtefatoPage>
      <CronogramaTimeline />
    </ArtefatoPage>
  );
};

export default CronogramaPage;
