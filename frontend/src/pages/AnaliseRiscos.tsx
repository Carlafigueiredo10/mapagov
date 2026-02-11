/**
 * AnaliseRiscosPage - Pagina dedicada para Analise de Riscos (BETA)
 *
 * Rota: /riscos
 *
 * Fluxo:
 * 1. Exibe landing institucional (enquadramento)
 * 2. Ao clicar em "Iniciar análise de riscos", exibe o wizard
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { WizardAnaliseRiscos, AnaliseRiscosLanding } from '../components/AnaliseRiscos';
import LandingShell from '../components/ui/LandingShell';
import { useRequireAuth } from '../hooks/useRequireAuth';

const AnaliseRiscosPage: React.FC = () => {
  const navigate = useNavigate();
  const requireAuth = useRequireAuth();
  const [mostrarWizard, setMostrarWizard] = useState(false);

  // Landing institucional (enquadramento)
  if (!mostrarWizard) {
    return (
      <LandingShell onBack={() => navigate(-1)}>
        <AnaliseRiscosLanding onIniciar={() => { if (requireAuth()) setMostrarWizard(true); }} />
      </LandingShell>
    );
  }

  // Wizard de análise de riscos
  return (
    <LandingShell maxWidth="900px" onBack={() => navigate(-1)}>
      <WizardAnaliseRiscos />
    </LandingShell>
  );
};

export default AnaliseRiscosPage;
