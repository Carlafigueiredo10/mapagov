import React from "react";

interface InterfaceEtapasTempoRealProps {
  dados?: Record<string, unknown>;
  onConfirm: (resposta: string) => void;
}

const InterfaceEtapasTempoReal: React.FC<InterfaceEtapasTempoRealProps> = ({ dados, onConfirm }) => (
  <div className="interface-container fade-in">
    <div className="interface-title">⏱️ Interface de Etapas em Tempo Real</div>
    <div className="interface-content">
      <pre>{JSON.stringify(dados, null, 2)}</pre>
    </div>
    <div className="action-buttons">
      <button className="btn-interface btn-primary" onClick={() => onConfirm("mock_resposta_etapas_tempo_real")}>
        Continuar
      </button>
    </div>
  </div>
);

export default InterfaceEtapasTempoReal;