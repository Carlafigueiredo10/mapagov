import React, { useState } from 'react';
import './InterfaceDinamica.css';
import { useChatStore } from '../../store/chatStore';

interface Subarea {
  codigo: string;
  nome: string;
  nome_completo: string;
  prefixo: string;
}

interface SubareasData {
  area_pai: {
    codigo: string;
    nome: string;
  };
  subareas: Subarea[];
}

interface SubareasSelectorProps {
  data: SubareasData;
  onConfirm: (subareaIndex: string) => void;
}

const SubareasSelector: React.FC<SubareasSelectorProps> = ({ data, onConfirm }) => {
  const [selectedSubareaIndex, setSelectedSubareaIndex] = useState<number>(-1);
  const { updateDadosPOP } = useChatStore();

  // Debug: ver dados recebidos
  console.log('🏢 SubareasSelector - Dados recebidos:', data);

  const handleSubareaClick = (index: number) => {
    setSelectedSubareaIndex(index);
  };

  const handleConfirm = () => {
    if (selectedSubareaIndex === -1) {
      alert('Por favor, selecione uma subárea.');
      return;
    }

    // Atualizar dados do POP com subárea selecionada
    const subareaSelecionada = data.subareas[selectedSubareaIndex];
    updateDadosPOP({
      subarea: {
        codigo: subareaSelecionada.codigo,
        nome: subareaSelecionada.nome_completo,
        prefixo: subareaSelecionada.prefixo
      }
    });

    // Enviar índice 1-based (1, 2, 3) para o backend
    onConfirm((selectedSubareaIndex + 1).toString());
  };

  // Verificar se há subáreas disponíveis
  if (!data?.subareas || data.subareas.length === 0) {
    return (
      <div className="interface-container fade-in">
        <div className="interface-title">⚠️ Erro ao carregar subáreas</div>
        <div className="interface-content">
          <p style={{ color: '#ef4444' }}>Nenhuma subárea foi encontrada. Dados recebidos:</p>
          <pre style={{ fontSize: '12px', background: '#f3f4f6', padding: '12px', borderRadius: '8px', overflow: 'auto' }}>
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      </div>
    );
  }

  return (
    <div className="interface-container fade-in areas-selector-horizontal">
      <div className="interface-title">Agora me diga, suas atividades estão vinculadas a qual DIGEP?</div>

      <div className="areas-grid">
        {data.subareas.map((subarea, index) => (
          <div
            key={subarea.codigo}
            className={`area-option ${selectedSubareaIndex === index ? 'selected' : ''}`}
            onClick={() => handleSubareaClick(index)}
          >
            <div className="area-codigo">{subarea.prefixo}</div>
            <div className="area-nome">{subarea.nome}</div>
          </div>
        ))}
      </div>

      <div className="action-buttons">
        <button
          className="btn-interface btn-primary"
          onClick={handleConfirm}
        >
          Confirmar Ex-Território
        </button>
      </div>
    </div>
  );
};

export default SubareasSelector;
