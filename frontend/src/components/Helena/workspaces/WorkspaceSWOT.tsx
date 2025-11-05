/**
 * Workspace SWOT - Análise de Forças, Fraquezas, Oportunidades e Ameaças
 * Baseado em metodologias do MGI para setor público
 */
import React, { useState, CSSProperties } from 'react';
import { Button } from '../../ui/Button';

export interface ItemSWOT {
  id: string;
  texto: string;
}

export interface DadosSWOT {
  forcas: ItemSWOT[];
  fraquezas: ItemSWOT[];
  oportunidades: ItemSWOT[];
  ameacas: ItemSWOT[];
}

interface WorkspaceSWOTProps {
  dados?: DadosSWOT;
  onSalvar?: (dados: DadosSWOT) => void;
  readonly?: boolean;
}

export const WorkspaceSWOT: React.FC<WorkspaceSWOTProps> = ({
  dados,
  onSalvar,
  readonly = false
}) => {
  const [swotData, setSwotData] = useState<DadosSWOT>(dados || {
    forcas: [],
    fraquezas: [],
    oportunidades: [],
    ameacas: []
  });

  const [novoItem, setNovoItem] = useState({
    forcas: '',
    fraquezas: '',
    oportunidades: '',
    ameacas: ''
  });

  const adicionarItem = (quadrante: keyof DadosSWOT) => {
    if (!novoItem[quadrante].trim()) return;

    const novosDados = {
      ...swotData,
      [quadrante]: [
        ...swotData[quadrante],
        {
          id: Date.now().toString(),
          texto: novoItem[quadrante]
        }
      ]
    };

    setSwotData(novosDados);
    setNovoItem({ ...novoItem, [quadrante]: '' });

    if (onSalvar) {
      onSalvar(novosDados);
    }
  };

  const removerItem = (quadrante: keyof DadosSWOT, id: string) => {
    const novosDados = {
      ...swotData,
      [quadrante]: swotData[quadrante].filter(item => item.id !== id)
    };

    setSwotData(novosDados);

    if (onSalvar) {
      onSalvar(novosDados);
    }
  };

  const renderQuadrante = (
    titulo: string,
    quadrante: keyof DadosSWOT,
    cor: string,
    icone: string
  ) => {
    const quadranteStyle: CSSProperties = {
      flex: 1,
      minWidth: '300px',
      display: 'flex',
      flexDirection: 'column',
      gap: '16px'
    };

    const headerStyle: CSSProperties = {
      background: cor,
      color: '#ffffff',
      padding: '16px',
      borderRadius: '12px 12px 0 0',
      fontWeight: 'bold',
      fontSize: '18px',
      display: 'flex',
      alignItems: 'center',
      gap: '12px'
    };

    const contentStyle: CSSProperties = {
      background: '#ffffff',
      border: `2px solid ${cor}`,
      borderRadius: '0 0 12px 12px',
      padding: '16px',
      minHeight: '200px',
      display: 'flex',
      flexDirection: 'column',
      gap: '12px'
    };

    const itemStyle: CSSProperties = {
      background: '#f8f9fa',
      padding: '12px',
      borderRadius: '8px',
      border: `1px solid ${cor}40`,
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      fontSize: '14px',
      lineHeight: 1.5
    };

    const inputStyle: CSSProperties = {
      width: '100%',
      padding: '10px',
      borderRadius: '8px',
      border: `2px solid ${cor}40`,
      fontSize: '14px',
      outline: 'none',
      transition: 'border-color 0.2s'
    };

    return (
      <div style={quadranteStyle}>
        <div style={headerStyle}>
          <span style={{ fontSize: '24px' }}>{icone}</span>
          {titulo}
        </div>
        <div style={contentStyle}>
          {swotData[quadrante].map(item => (
            <div key={item.id} style={itemStyle}>
              <span style={{ flex: 1 }}>{item.texto}</span>
              {!readonly && (
                <button
                  onClick={() => removerItem(quadrante, item.id)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: '#dc2626',
                    cursor: 'pointer',
                    fontSize: '18px',
                    padding: '4px 8px',
                    marginLeft: '8px'
                  }}
                >
                  ×
                </button>
              )}
            </div>
          ))}

          {!readonly && (
            <div style={{ marginTop: '8px' }}>
              <input
                type="text"
                placeholder={`Adicionar ${titulo.toLowerCase()}...`}
                value={novoItem[quadrante]}
                onChange={(e) => setNovoItem({ ...novoItem, [quadrante]: e.target.value })}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    adicionarItem(quadrante);
                  }
                }}
                style={inputStyle}
              />
              <Button
                variant="outline"
                size="sm"
                onClick={() => adicionarItem(quadrante)}
                style={{ marginTop: '8px', width: '100%', borderColor: cor, color: cor }}
              >
                + Adicionar
              </Button>
            </div>
          )}
        </div>
      </div>
    );
  };

  const containerStyle: CSSProperties = {
    width: '100%',
    padding: '24px'
  };

  const gridStyle: CSSProperties = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '24px',
    marginTop: '24px'
  };

  const titleStyle: CSSProperties = {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#1B4F72',
    marginBottom: '8px'
  };

  const subtitleStyle: CSSProperties = {
    fontSize: '16px',
    color: '#6b7280',
    marginBottom: '24px'
  };

  return (
    <div style={containerStyle}>
      <div style={titleStyle}>Análise SWOT</div>
      <div style={subtitleStyle}>
        Identifique fatores internos (Forças e Fraquezas) e externos (Oportunidades e Ameaças)
      </div>

      <div style={gridStyle}>
        {renderQuadrante('Forças', 'forcas', '#27AE60', '💪')}
        {renderQuadrante('Fraquezas', 'fraquezas', '#E74C3C', '⚠️')}
        {renderQuadrante('Oportunidades', 'oportunidades', '#3498DB', '🎯')}
        {renderQuadrante('Ameaças', 'ameacas', '#E67E22', '⚡')}
      </div>
    </div>
  );
};

export default WorkspaceSWOT;
