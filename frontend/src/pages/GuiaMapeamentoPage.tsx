/**
 * GuiaMapeamentoPage - Página educacional do módulo de Mapeamento de Atividades
 *
 * Rota: /pop
 * Pública — explica o que é o mapeamento antes de exigir login.
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import GuiaMapeamentoLanding from '../components/Helena/GuiaMapeamentoLanding';
import LandingShell from '../components/ui/LandingShell';

const GuiaMapeamentoPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <LandingShell onBack={() => navigate('/')}>
      <GuiaMapeamentoLanding />
    </LandingShell>
  );
};

export default GuiaMapeamentoPage;
