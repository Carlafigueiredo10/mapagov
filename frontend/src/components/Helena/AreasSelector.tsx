import React, { useState } from 'react';
import './InterfaceDinamica.css';
import { useChatStore } from '../../store/chatStore';

interface Area {
  codigo: string;
  nome: string;
}

interface AreasData {
  opcoes_areas: Record<string, Area>;
}

interface AreasSelectorProps {
  data: AreasData;
  onConfirm: (areaId: string) => void;
}

const AreasSelector: React.FC<AreasSelectorProps> = ({ data, onConfirm }) => {
  const [selectedAreaId, setSelectedAreaId] = useState<string>('');
  const { updateDadosPOP } = useChatStore();

  // Debug: ver dados recebidos
  console.log('🏢 AreasSelector - Dados recebidos:', data);
  console.log('🏢 AreasSelector - opcoes_areas:', data?.opcoes_areas);

  // 🔍 DEBUG DETALHADO: Mostrar CADA área recebida
  if (data?.opcoes_areas) {
    console.log('🔍 DETALHAMENTO DAS ÁREAS RECEBIDAS:');
    Object.entries(data.opcoes_areas).forEach(([id, area]) => {
      console.log(`   ${id}: ${area.codigo} - ${area.nome}`);
    });
  }

  const handleAreaClick = (areaId: string) => {
    setSelectedAreaId(areaId);
  };

  const handleConfirm = () => {
    if (!selectedAreaId) {
      alert('Por favor, selecione uma área.');
      return;
    }
    
    // Atualizar dados do POP com área selecionada
    const areaSelecionada = data.opcoes_areas[selectedAreaId];
    updateDadosPOP({
      area: {
        codigo: areaSelecionada.codigo,
        nome: areaSelecionada.nome
      }
    });
    
    onConfirm(selectedAreaId);
  };

  // Verificar se há áreas disponíveis
  const areasDisponiveis = data?.opcoes_areas ? Object.entries(data.opcoes_areas) : [];

  if (areasDisponiveis.length === 0) {
    return (
      <div className="interface-container fade-in">
        <div className="interface-title">⚠️ Erro ao carregar áreas</div>
        <div className="interface-content">
          <p style={{ color: '#ef4444' }}>Nenhuma área foi encontrada. Dados recebidos:</p>
          <pre style={{ fontSize: '12px', background: '#f3f4f6', padding: '12px', borderRadius: '8px', overflow: 'auto' }}>
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      </div>
    );
  }

  return (
    <div className="interface-container fade-in areas-selector-horizontal">
      <div className="interface-title">Vamos começar pela identificação da área responsável. Informe a área da DECIPEX onde a atividade é executada.</div>

      <div className="areas-grid">
        {areasDisponiveis.map(([id, area]) => (
          <div
            key={id}
            className={`area-option ${selectedAreaId === id ? 'selected' : ''}`}
            onClick={() => handleAreaClick(id)}
          >
            <div className="area-codigo">{area.codigo}</div>
            <div className="area-nome">{area.nome}</div>
          </div>
        ))}
      </div>

      <div className="action-buttons">
        <button
          className="btn-interface btn-primary"
          onClick={handleConfirm}
        >
          Confirmar Área
        </button>
      </div>
    </div>
  );
};

export default AreasSelector;