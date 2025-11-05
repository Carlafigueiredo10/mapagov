/**
 * Workspace OKR - Objectives and Key Results
 * Baseado na metodologia do MPO/MGI para setor público
 * Promove transparência e alinhamento organizacional
 */
import React, { useState, CSSProperties } from 'react';
import { Button } from '../../ui/Button';
import { Badge } from '../../ui/Badge';

export interface KeyResult {
  id: string;
  descricao: string;
  metaInicial: number;
  metaFinal: number;
  valorAtual: number;
  unidade: string;
}

export interface Objetivo {
  id: string;
  titulo: string;
  descricao: string;
  prazo: string;
  keyResults: KeyResult[];
}

export interface DadosOKR {
  objetivos: Objetivo[];
}

interface WorkspaceOKRProps {
  dados?: DadosOKR;
  onSalvar?: (dados: DadosOKR) => void;
  readonly?: boolean;
}

export const WorkspaceOKR: React.FC<WorkspaceOKRProps> = ({
  dados,
  onSalvar,
  readonly = false
}) => {
  const [okrData, setOkrData] = useState<DadosOKR>(dados || {
    objetivos: []
  });

  const [expandido, setExpandido] = useState<string | null>(null);

  const adicionarObjetivo = () => {
    const novoObjetivo: Objetivo = {
      id: Date.now().toString(),
      titulo: 'Novo Objetivo',
      descricao: 'Descreva o objetivo estratégico...',
      prazo: 'T1 2025',
      keyResults: []
    };

    const novosDados = {
      objetivos: [...okrData.objetivos, novoObjetivo]
    };

    setOkrData(novosDados);
    setExpandido(novoObjetivo.id);

    if (onSalvar) {
      onSalvar(novosDados);
    }
  };

  const adicionarKeyResult = (objetivoId: string) => {
    const novoKR: KeyResult = {
      id: Date.now().toString(),
      descricao: 'Novo Resultado-Chave',
      metaInicial: 0,
      metaFinal: 100,
      valorAtual: 0,
      unidade: '%'
    };

    const novosDados = {
      objetivos: okrData.objetivos.map(obj =>
        obj.id === objetivoId
          ? { ...obj, keyResults: [...obj.keyResults, novoKR] }
          : obj
      )
    };

    setOkrData(novosDados);

    if (onSalvar) {
      onSalvar(novosDados);
    }
  };

  const atualizarObjetivo = (objetivoId: string, campo: keyof Objetivo, valor: any) => {
    const novosDados = {
      objetivos: okrData.objetivos.map(obj =>
        obj.id === objetivoId ? { ...obj, [campo]: valor } : obj
      )
    };

    setOkrData(novosDados);

    if (onSalvar) {
      onSalvar(novosDados);
    }
  };

  const atualizarKeyResult = (objetivoId: string, krId: string, campo: keyof KeyResult, valor: any) => {
    const novosDados = {
      objetivos: okrData.objetivos.map(obj =>
        obj.id === objetivoId
          ? {
              ...obj,
              keyResults: obj.keyResults.map(kr =>
                kr.id === krId ? { ...kr, [campo]: valor } : kr
              )
            }
          : obj
      )
    };

    setOkrData(novosDados);

    if (onSalvar) {
      onSalvar(novosDados);
    }
  };

  const removerObjetivo = (objetivoId: string) => {
    const novosDados = {
      objetivos: okrData.objetivos.filter(obj => obj.id !== objetivoId)
    };

    setOkrData(novosDados);

    if (onSalvar) {
      onSalvar(novosDados);
    }
  };

  const removerKeyResult = (objetivoId: string, krId: string) => {
    const novosDados = {
      objetivos: okrData.objetivos.map(obj =>
        obj.id === objetivoId
          ? { ...obj, keyResults: obj.keyResults.filter(kr => kr.id !== krId) }
          : obj
      )
    };

    setOkrData(novosDados);

    if (onSalvar) {
      onSalvar(novosDados);
    }
  };

  const calcularProgresso = (kr: KeyResult): number => {
    const range = kr.metaFinal - kr.metaInicial;
    if (range === 0) return 0;
    const progresso = ((kr.valorAtual - kr.metaInicial) / range) * 100;
    return Math.max(0, Math.min(100, progresso));
  };

  const renderKeyResult = (objetivoId: string, kr: KeyResult) => {
    const progresso = calcularProgresso(kr);
    const corProgresso = progresso >= 70 ? '#27AE60' : progresso >= 40 ? '#F39C12' : '#E74C3C';

    const krStyle: CSSProperties = {
      background: '#f8f9fa',
      padding: '16px',
      borderRadius: '8px',
      border: '1px solid #e5e7eb',
      marginBottom: '12px'
    };

    const progressBarContainer: CSSProperties = {
      width: '100%',
      height: '8px',
      background: '#e5e7eb',
      borderRadius: '4px',
      overflow: 'hidden',
      marginTop: '8px'
    };

    const progressBar: CSSProperties = {
      width: `${progresso}%`,
      height: '100%',
      background: corProgresso,
      transition: 'width 0.3s ease'
    };

    const inputStyle: CSSProperties = {
      width: '100%',
      padding: '8px',
      border: '1px solid #d1d5db',
      borderRadius: '6px',
      fontSize: '14px',
      marginTop: '8px'
    };

    const metasContainer: CSSProperties = {
      display: 'flex',
      gap: '12px',
      marginTop: '8px'
    };

    const metaInput: CSSProperties = {
      flex: 1,
      padding: '8px',
      border: '1px solid #d1d5db',
      borderRadius: '6px',
      fontSize: '14px'
    };

    return (
      <div key={kr.id} style={krStyle}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
          <div style={{ flex: 1 }}>
            {readonly ? (
              <strong>{kr.descricao}</strong>
            ) : (
              <input
                type="text"
                value={kr.descricao}
                onChange={(e) => atualizarKeyResult(objetivoId, kr.id, 'descricao', e.target.value)}
                style={inputStyle}
              />
            )}
          </div>
          {!readonly && (
            <button
              onClick={() => removerKeyResult(objetivoId, kr.id)}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#dc2626',
                cursor: 'pointer',
                fontSize: '20px',
                padding: '0 8px',
                marginLeft: '12px'
              }}
            >
              ×
            </button>
          )}
        </div>

        <div style={metasContainer}>
          <div style={{ flex: 1 }}>
            <label style={{ fontSize: '12px', color: '#6b7280', display: 'block' }}>Inicial</label>
            <input
              type="number"
              value={kr.metaInicial}
              onChange={(e) => atualizarKeyResult(objetivoId, kr.id, 'metaInicial', parseFloat(e.target.value))}
              disabled={readonly}
              style={metaInput}
            />
          </div>
          <div style={{ flex: 1 }}>
            <label style={{ fontSize: '12px', color: '#6b7280', display: 'block' }}>Meta</label>
            <input
              type="number"
              value={kr.metaFinal}
              onChange={(e) => atualizarKeyResult(objetivoId, kr.id, 'metaFinal', parseFloat(e.target.value))}
              disabled={readonly}
              style={metaInput}
            />
          </div>
          <div style={{ flex: 1 }}>
            <label style={{ fontSize: '12px', color: '#6b7280', display: 'block' }}>Atual</label>
            <input
              type="number"
              value={kr.valorAtual}
              onChange={(e) => atualizarKeyResult(objetivoId, kr.id, 'valorAtual', parseFloat(e.target.value))}
              disabled={readonly}
              style={metaInput}
            />
          </div>
          <div style={{ flex: 0.5 }}>
            <label style={{ fontSize: '12px', color: '#6b7280', display: 'block' }}>Unidade</label>
            <input
              type="text"
              value={kr.unidade}
              onChange={(e) => atualizarKeyResult(objetivoId, kr.id, 'unidade', e.target.value)}
              disabled={readonly}
              style={metaInput}
            />
          </div>
        </div>

        <div style={progressBarContainer}>
          <div style={progressBar} />
        </div>
        <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px', textAlign: 'right' }}>
          Progresso: {progresso.toFixed(1)}%
        </div>
      </div>
    );
  };

  const renderObjetivo = (objetivo: Objetivo) => {
    const isExpandido = expandido === objetivo.id;

    const objetivoCard: CSSProperties = {
      background: '#ffffff',
      border: '2px solid #3498DB',
      borderRadius: '12px',
      padding: '20px',
      marginBottom: '16px',
      transition: 'all 0.3s ease'
    };

    const headerStyle: CSSProperties = {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'start',
      marginBottom: isExpandido ? '16px' : '0'
    };

    const inputStyle: CSSProperties = {
      width: '100%',
      padding: '8px',
      border: '1px solid #d1d5db',
      borderRadius: '6px',
      fontSize: '14px',
      marginTop: '8px'
    };

    const totalKRs = objetivo.keyResults.length;
    const progressoMedio = totalKRs > 0
      ? objetivo.keyResults.reduce((acc, kr) => acc + calcularProgresso(kr), 0) / totalKRs
      : 0;

    return (
      <div key={objetivo.id} style={objetivoCard}>
        <div style={headerStyle}>
          <div style={{ flex: 1, cursor: 'pointer' }} onClick={() => setExpandido(isExpandido ? null : objetivo.id)}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
              <span style={{ fontSize: '24px' }}>🎯</span>
              {readonly ? (
                <h3 style={{ margin: 0, fontSize: '20px', color: '#1B4F72' }}>{objetivo.titulo}</h3>
              ) : (
                <input
                  type="text"
                  value={objetivo.titulo}
                  onChange={(e) => atualizarObjetivo(objetivo.id, 'titulo', e.target.value)}
                  onClick={(e) => e.stopPropagation()}
                  style={{ ...inputStyle, fontSize: '18px', fontWeight: 'bold' }}
                />
              )}
            </div>
            {readonly && <p style={{ margin: '8px 0', color: '#6b7280' }}>{objetivo.descricao}</p>}
          </div>

          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <Badge variant={progressoMedio >= 70 ? 'success' : progressoMedio >= 40 ? 'warning' : 'default'}>
              {progressoMedio.toFixed(0)}%
            </Badge>
            <Badge variant="info">{objetivo.prazo}</Badge>
            {!readonly && (
              <button
                onClick={() => removerObjetivo(objetivo.id)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#dc2626',
                  cursor: 'pointer',
                  fontSize: '24px',
                  padding: '0 8px'
                }}
              >
                ×
              </button>
            )}
          </div>
        </div>

        {isExpandido && (
          <>
            {!readonly && (
              <>
                <textarea
                  value={objetivo.descricao}
                  onChange={(e) => atualizarObjetivo(objetivo.id, 'descricao', e.target.value)}
                  placeholder="Descreva o objetivo estratégico..."
                  style={{
                    ...inputStyle,
                    minHeight: '60px',
                    resize: 'vertical',
                    fontFamily: 'inherit'
                  }}
                />
                <input
                  type="text"
                  value={objetivo.prazo}
                  onChange={(e) => atualizarObjetivo(objetivo.id, 'prazo', e.target.value)}
                  placeholder="Ex: T1 2025"
                  style={{ ...inputStyle, maxWidth: '200px' }}
                />
              </>
            )}

            <h4 style={{ marginTop: '24px', marginBottom: '12px', color: '#1B4F72' }}>
              Resultados-Chave ({totalKRs})
            </h4>

            {objetivo.keyResults.map(kr => renderKeyResult(objetivo.id, kr))}

            {!readonly && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => adicionarKeyResult(objetivo.id)}
                style={{ marginTop: '8px', borderColor: '#3498DB', color: '#3498DB' }}
              >
                + Adicionar Resultado-Chave
              </Button>
            )}
          </>
        )}
      </div>
    );
  };

  const containerStyle: CSSProperties = {
    width: '100%',
    padding: '24px'
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
      <div style={titleStyle}>OKR - Objectives and Key Results</div>
      <div style={subtitleStyle}>
        Defina objetivos claros e mensuráveis com resultados-chave que indicam o progresso
      </div>

      {okrData.objetivos.map(objetivo => renderObjetivo(objetivo))}

      {!readonly && (
        <Button
          variant="primary"
          onClick={adicionarObjetivo}
          style={{ marginTop: '16px' }}
        >
          + Adicionar Objetivo
        </Button>
      )}

      {okrData.objetivos.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '60px 20px',
          color: '#9ca3af',
          fontSize: '16px'
        }}>
          Nenhum objetivo definido ainda. Clique em "Adicionar Objetivo" para começar.
        </div>
      )}
    </div>
  );
};

export default WorkspaceOKR;
