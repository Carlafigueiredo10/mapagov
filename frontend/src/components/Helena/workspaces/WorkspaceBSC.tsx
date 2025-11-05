/**
 * Workspace BSC - Balanced Scorecard para Setor Público
 * Baseado na metodologia de Kaplan e Norton adaptada pelo MPO/MGI
 * 4 Perspectivas: Sociedade, Processos Internos, Aprendizado e Orçamento
 */
import React, { useState, CSSProperties } from 'react';
import { Button } from '../../ui/Button';
import { Badge } from '../../ui/Badge';

export interface Indicador {
  id: string;
  nome: string;
  meta: string;
  valorAtual: string;
  responsavel: string;
}

export interface Objetivo {
  id: string;
  titulo: string;
  indicadores: Indicador[];
}

export interface Perspectiva {
  id: string;
  nome: string;
  cor: string;
  icone: string;
  descricao: string;
  objetivos: Objetivo[];
}

export interface DadosBSC {
  perspectivas: Perspectiva[];
}

interface WorkspaceBSCProps {
  dados?: DadosBSC;
  onSalvar?: (dados: DadosBSC) => void;
  readonly?: boolean;
}

const PERSPECTIVAS_PADRAO: Perspectiva[] = [
  {
    id: 'sociedade',
    nome: 'Sociedade',
    cor: '#3498DB',
    icone: '👥',
    descricao: 'Impacto e valor entregue para a sociedade',
    objetivos: []
  },
  {
    id: 'processos',
    nome: 'Processos Internos',
    cor: '#27AE60',
    icone: '⚙️',
    descricao: 'Eficiência e qualidade dos processos',
    objetivos: []
  },
  {
    id: 'aprendizado',
    nome: 'Aprendizado e Crescimento',
    cor: '#9B59B6',
    icone: '📚',
    descricao: 'Capacitação e inovação organizacional',
    objetivos: []
  },
  {
    id: 'orcamento',
    nome: 'Orçamento e Recursos',
    cor: '#E67E22',
    icone: '💰',
    descricao: 'Sustentabilidade financeira e eficiência',
    objetivos: []
  }
];

export const WorkspaceBSC: React.FC<WorkspaceBSCProps> = ({
  dados,
  onSalvar,
  readonly = false
}) => {
  const [bscData, setBscData] = useState<DadosBSC>(dados || {
    perspectivas: PERSPECTIVAS_PADRAO
  });

  const [perspectivaExpandida, setPerspectivaExpandida] = useState<string | null>(null);

  const adicionarObjetivo = (perspectivaId: string) => {
    const novoObjetivo: Objetivo = {
      id: Date.now().toString(),
      titulo: 'Novo Objetivo Estratégico',
      indicadores: []
    };

    const novosDados = {
      perspectivas: bscData.perspectivas.map(p =>
        p.id === perspectivaId
          ? { ...p, objetivos: [...p.objetivos, novoObjetivo] }
          : p
      )
    };

    setBscData(novosDados);

    if (onSalvar) {
      onSalvar(novosDados);
    }
  };

  const adicionarIndicador = (perspectivaId: string, objetivoId: string) => {
    const novoIndicador: Indicador = {
      id: Date.now().toString(),
      nome: 'Novo Indicador',
      meta: '100%',
      valorAtual: '0%',
      responsavel: ''
    };

    const novosDados = {
      perspectivas: bscData.perspectivas.map(p =>
        p.id === perspectivaId
          ? {
              ...p,
              objetivos: p.objetivos.map(obj =>
                obj.id === objetivoId
                  ? { ...obj, indicadores: [...obj.indicadores, novoIndicador] }
                  : obj
              )
            }
          : p
      )
    };

    setBscData(novosDados);

    if (onSalvar) {
      onSalvar(novosDados);
    }
  };

  const atualizarObjetivo = (perspectivaId: string, objetivoId: string, titulo: string) => {
    const novosDados = {
      perspectivas: bscData.perspectivas.map(p =>
        p.id === perspectivaId
          ? {
              ...p,
              objetivos: p.objetivos.map(obj =>
                obj.id === objetivoId ? { ...obj, titulo } : obj
              )
            }
          : p
      )
    };

    setBscData(novosDados);

    if (onSalvar) {
      onSalvar(novosDados);
    }
  };

  const atualizarIndicador = (
    perspectivaId: string,
    objetivoId: string,
    indicadorId: string,
    campo: keyof Indicador,
    valor: string
  ) => {
    const novosDados = {
      perspectivas: bscData.perspectivas.map(p =>
        p.id === perspectivaId
          ? {
              ...p,
              objetivos: p.objetivos.map(obj =>
                obj.id === objetivoId
                  ? {
                      ...obj,
                      indicadores: obj.indicadores.map(ind =>
                        ind.id === indicadorId ? { ...ind, [campo]: valor } : ind
                      )
                    }
                  : obj
              )
            }
          : p
      )
    };

    setBscData(novosDados);

    if (onSalvar) {
      onSalvar(novosDados);
    }
  };

  const removerObjetivo = (perspectivaId: string, objetivoId: string) => {
    const novosDados = {
      perspectivas: bscData.perspectivas.map(p =>
        p.id === perspectivaId
          ? { ...p, objetivos: p.objetivos.filter(obj => obj.id !== objetivoId) }
          : p
      )
    };

    setBscData(novosDados);

    if (onSalvar) {
      onSalvar(novosDados);
    }
  };

  const removerIndicador = (perspectivaId: string, objetivoId: string, indicadorId: string) => {
    const novosDados = {
      perspectivas: bscData.perspectivas.map(p =>
        p.id === perspectivaId
          ? {
              ...p,
              objetivos: p.objetivos.map(obj =>
                obj.id === objetivoId
                  ? { ...obj, indicadores: obj.indicadores.filter(ind => ind.id !== indicadorId) }
                  : obj
              )
            }
          : p
      )
    };

    setBscData(novosDados);

    if (onSalvar) {
      onSalvar(novosDados);
    }
  };

  const renderIndicador = (perspectivaId: string, objetivoId: string, indicador: Indicador) => {
    const indicadorStyle: CSSProperties = {
      background: '#f8f9fa',
      padding: '12px',
      borderRadius: '6px',
      border: '1px solid #e5e7eb',
      marginBottom: '8px'
    };

    const inputStyle: CSSProperties = {
      width: '100%',
      padding: '6px 8px',
      border: '1px solid #d1d5db',
      borderRadius: '4px',
      fontSize: '13px',
      marginTop: '4px'
    };

    const gridStyle: CSSProperties = {
      display: 'grid',
      gridTemplateColumns: '2fr 1fr 1fr',
      gap: '8px',
      marginTop: '8px'
    };

    return (
      <div key={indicador.id} style={indicadorStyle}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
          <div style={{ flex: 1 }}>
            {readonly ? (
              <strong style={{ fontSize: '14px' }}>{indicador.nome}</strong>
            ) : (
              <input
                type="text"
                value={indicador.nome}
                onChange={(e) => atualizarIndicador(perspectivaId, objetivoId, indicador.id, 'nome', e.target.value)}
                style={inputStyle}
                placeholder="Nome do indicador"
              />
            )}
          </div>
          {!readonly && (
            <button
              onClick={() => removerIndicador(perspectivaId, objetivoId, indicador.id)}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#dc2626',
                cursor: 'pointer',
                fontSize: '18px',
                padding: '0 8px',
                marginLeft: '8px'
              }}
            >
              ×
            </button>
          )}
        </div>

        <div style={gridStyle}>
          <div>
            <label style={{ fontSize: '11px', color: '#6b7280', display: 'block' }}>Meta</label>
            <input
              type="text"
              value={indicador.meta}
              onChange={(e) => atualizarIndicador(perspectivaId, objetivoId, indicador.id, 'meta', e.target.value)}
              disabled={readonly}
              style={inputStyle}
              placeholder="Ex: 100%"
            />
          </div>
          <div>
            <label style={{ fontSize: '11px', color: '#6b7280', display: 'block' }}>Atual</label>
            <input
              type="text"
              value={indicador.valorAtual}
              onChange={(e) => atualizarIndicador(perspectivaId, objetivoId, indicador.id, 'valorAtual', e.target.value)}
              disabled={readonly}
              style={inputStyle}
              placeholder="Ex: 75%"
            />
          </div>
          <div>
            <label style={{ fontSize: '11px', color: '#6b7280', display: 'block' }}>Responsável</label>
            <input
              type="text"
              value={indicador.responsavel}
              onChange={(e) => atualizarIndicador(perspectivaId, objetivoId, indicador.id, 'responsavel', e.target.value)}
              disabled={readonly}
              style={inputStyle}
              placeholder="Nome"
            />
          </div>
        </div>
      </div>
    );
  };

  const renderObjetivo = (perspectivaId: string, objetivo: Objetivo) => {
    const objetivoStyle: CSSProperties = {
      background: '#ffffff',
      padding: '16px',
      borderRadius: '8px',
      border: '1px solid #d1d5db',
      marginBottom: '12px'
    };

    const inputStyle: CSSProperties = {
      width: '100%',
      padding: '8px',
      border: '1px solid #d1d5db',
      borderRadius: '6px',
      fontSize: '14px',
      fontWeight: 'bold'
    };

    return (
      <div key={objetivo.id} style={objetivoStyle}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '12px' }}>
          {readonly ? (
            <h4 style={{ margin: 0, fontSize: '16px', color: '#1B4F72' }}>{objetivo.titulo}</h4>
          ) : (
            <input
              type="text"
              value={objetivo.titulo}
              onChange={(e) => atualizarObjetivo(perspectivaId, objetivo.id, e.target.value)}
              style={inputStyle}
              placeholder="Título do objetivo"
            />
          )}
          {!readonly && (
            <button
              onClick={() => removerObjetivo(perspectivaId, objetivo.id)}
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

        <div>
          <label style={{ fontSize: '12px', color: '#6b7280', fontWeight: 'bold', display: 'block', marginBottom: '8px' }}>
            Indicadores ({objetivo.indicadores.length})
          </label>
          {objetivo.indicadores.map(ind => renderIndicador(perspectivaId, objetivo.id, ind))}

          {!readonly && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => adicionarIndicador(perspectivaId, objetivo.id)}
              style={{ marginTop: '8px', fontSize: '13px' }}
            >
              + Adicionar Indicador
            </Button>
          )}
        </div>
      </div>
    );
  };

  const renderPerspectiva = (perspectiva: Perspectiva) => {
    const isExpandida = perspectivaExpandida === perspectiva.id;

    const perspectivaCard: CSSProperties = {
      background: '#ffffff',
      border: `3px solid ${perspectiva.cor}`,
      borderRadius: '12px',
      padding: '20px',
      marginBottom: '16px',
      transition: 'all 0.3s ease'
    };

    const headerStyle: CSSProperties = {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      cursor: 'pointer',
      marginBottom: isExpandida ? '16px' : '0'
    };

    const titleStyle: CSSProperties = {
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      flex: 1
    };

    return (
      <div key={perspectiva.id} style={perspectivaCard}>
        <div style={headerStyle} onClick={() => setPerspectivaExpandida(isExpandida ? null : perspectiva.id)}>
          <div style={titleStyle}>
            <span style={{ fontSize: '28px' }}>{perspectiva.icone}</span>
            <div>
              <h3 style={{ margin: 0, fontSize: '20px', color: perspectiva.cor }}>{perspectiva.nome}</h3>
              <p style={{ margin: '4px 0 0', fontSize: '13px', color: '#6b7280' }}>{perspectiva.descricao}</p>
            </div>
          </div>
          <Badge variant="info">{perspectiva.objetivos.length} objetivos</Badge>
        </div>

        {isExpandida && (
          <>
            {perspectiva.objetivos.map(obj => renderObjetivo(perspectiva.id, obj))}

            {!readonly && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => adicionarObjetivo(perspectiva.id)}
                style={{ marginTop: '8px', borderColor: perspectiva.cor, color: perspectiva.cor }}
              >
                + Adicionar Objetivo
              </Button>
            )}

            {perspectiva.objetivos.length === 0 && (
              <div style={{
                textAlign: 'center',
                padding: '40px 20px',
                color: '#9ca3af',
                fontSize: '14px'
              }}>
                Nenhum objetivo definido nesta perspectiva.
              </div>
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
      <div style={titleStyle}>BSC - Balanced Scorecard Público</div>
      <div style={subtitleStyle}>
        Gestão estratégica com 4 perspectivas adaptadas para o setor público
      </div>

      {bscData.perspectivas.map(perspectiva => renderPerspectiva(perspectiva))}
    </div>
  );
};

export default WorkspaceBSC;
