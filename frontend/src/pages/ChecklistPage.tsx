/**
 * Página do Checklist de Governança
 */
import React from 'react';
import ArtefatoPage from './ArtefatoPage';
import ChecklistGovernanca from '../components/Helena/artefatos/ChecklistGovernanca';

export const ChecklistPage: React.FC = () => {
  return (
    <ArtefatoPage>
      <ChecklistGovernanca />
    </ArtefatoPage>
  );
};

export default ChecklistPage;
