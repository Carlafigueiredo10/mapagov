/**
 * PainelGestaoPage - Página do Painel de Gestão MapaGov
 *
 * Rota: /painel
 *
 * Fluxo:
 * 1. Exibe landing institucional (enquadramento + KPIs preview)
 * 2. Ao clicar "Acessar Painel", navega para a view do dashboard
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLanding from '../components/Helena/DashboardLanding';
import PainelExecutivo from '../components/Helena/PainelExecutivo';
import LandingShell from '../components/ui/LandingShell';

type ViewMode = 'landing' | 'painel';

const PainelGestaoPage: React.FC = () => {
  const navigate = useNavigate();
  const [viewMode, setViewMode] = useState<ViewMode>('landing');

  if (viewMode === 'painel') {
    return (
      <PainelExecutivo
        onVoltar={() => setViewMode('landing')}
      />
    );
  }

  return (
    <LandingShell onBack={() => navigate(-1)}>
      <DashboardLanding
        onAcessar={() => setViewMode('painel')}
      />
    </LandingShell>
  );
};

export default PainelGestaoPage;
