/**
 * Workspace 5W2H - Planejamento de Ações
 * What, Why, Where, When, Who, How, How Much
 * Ferramenta prática para definir planos de ação detalhados
 */
import React, { useState, CSSProperties } from 'react';
import { Button } from '../../ui/Button';
import { Badge } from '../../ui/Badge';

export interface Acao {
  id: string;
  what: string;      // O que será feito?
  why: string;       // Por que será feito?
  where: string;     // Onde será feito?
  when: string;      // Quando será feito?
  who: string;       // Quem fará?
  how: string;       // Como será feito?
  howMuch: string;   // Quanto custará?
  status: 'pendente' | 'em_andamento' | 'concluido';
}

export interface Dados5W2H {
  acoes: Acao[];
}

interface Workspace5W2HProps {
  dados?: Dados5W2H;
  onSalvar?: (dados: Dados5W2H) => void;
  readonly?: boolean;
}

export const Workspace5W2H: React.FC<Workspace5W2HProps> = ({
  dados,
  onSalvar,
  readonly = false
}) => {
  const [data5w2h, setData5w2h] = useState<Dados5W2H>(dados || {
    acoes: []
  });

  const [acaoExpandida, setAcaoExpandida] = useState<string | null>(null);

  const adicionarAcao = () => {
    const novaAcao: Acao = {
      id: Date.now().toString(),
      what: 'Nova ação',
      why: 'Justificativa',
      where: 'Local',
      when: 'Prazo',
      who: 'Responsável',
      how: 'Método',
      howMuch: 'R$ 0,00',
      status: 'pendente'
    };

    const novosDados = {
      acoes: [...data5w2h.acoes, novaAcao]
    };

    setData5w2h(novosDados);
    setAcaoExpandida(novaAcao.id);

    if (onSalvar) {
      onSalvar(novosDados);
    }
  };

  const atualizarAcao = (acaoId: string, campo: keyof Acao, valor: any) => {
    const novosDados = {
      acoes: data5w2h.acoes.map(acao =>
        acao.id === acaoId ? { ...acao, [campo]: valor } : acao
      )
    };

    setData5w2h(novosDados);

    if (onSalvar) {
      onSalvar(novosDados);
    }
  };

  const removerAcao = (acaoId: string) => {
    const novosDados = {
      acoes: data5w2h.acoes.filter(acao => acao.id !== acaoId)
    };

    setData5w2h(novosDados);

    if (onSalvar) {
      onSalvar(novosDados);
    }
  };

  const getCorStatus = (status: Acao['status']) => {
    switch (status) {
      case 'concluido':
        return '#27AE60';
      case 'em_andamento':
        return '#F39C12';
      default:
        return '#95a5a6';
    }
  };

  const renderCampo = (
    acaoId: string,
    campo: keyof Acao,
    label: string,
    placeholder: string,
    icone: string,
    multiline: boolean = false
  ) => {
    const acao = data5w2h.acoes.find(a => a.id === acaoId);
    if (!acao) return null;

    const containerStyle: CSSProperties = {
      marginBottom: '16px'
    };

    const labelStyle: CSSProperties = {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      fontSize: '14px',
      fontWeight: 'bold',
      color: '#1B4F72',
      marginBottom: '8px'
    };

    const inputStyle: CSSProperties = {
      width: '100%',
      padding: '10px 12px',
      border: '2px solid #e5e7eb',
      borderRadius: '8px',
      fontSize: '14px',
      fontFamily: 'inherit',
      outline: 'none',
      transition: 'border-color 0.2s',
      resize: multiline ? 'vertical' : undefined,
      minHeight: multiline ? '80px' : undefined
    };

    const valor = acao[campo];

    return (
      <div key={campo} style={containerStyle}>
        <div style={labelStyle}>
          <span>{icone}</span>
          <span>{label}</span>
        </div>
        {readonly ? (
          <div style={{
            padding: '10px 12px',
            background: '#f8f9fa',
            borderRadius: '8px',
            fontSize: '14px',
            lineHeight: 1.5
          }}>
            {valor}
          </div>
        ) : (
          multiline ? (
            <textarea
              value={valor as string}
              onChange={(e) => atualizarAcao(acaoId, campo, e.target.value)}
              placeholder={placeholder}
              style={inputStyle}
            />
          ) : (
            <input
              type="text"
              value={valor as string}
              onChange={(e) => atualizarAcao(acaoId, campo, e.target.value)}
              placeholder={placeholder}
              style={inputStyle}
            />
          )
        )}
      </div>
    );
  };

  const renderAcao = (acao: Acao) => {
    const isExpandida = acaoExpandida === acao.id;

    const acaoCard: CSSProperties = {
      background: '#ffffff',
      border: `2px solid ${getCorStatus(acao.status)}`,
      borderRadius: '12px',
      padding: '20px',
      marginBottom: '16px',
      transition: 'all 0.3s ease'
    };

    const headerStyle: CSSProperties = {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'start',
      marginBottom: isExpandida ? '20px' : '0',
      cursor: 'pointer'
    };

    const titleSection: CSSProperties = {
      flex: 1
    };

    const actionsSection: CSSProperties = {
      display: 'flex',
      gap: '8px',
      alignItems: 'center'
    };

    const statusOptions: { value: Acao['status']; label: string }[] = [
      { value: 'pendente', label: 'Pendente' },
      { value: 'em_andamento', label: 'Em andamento' },
      { value: 'concluido', label: 'Concluído' }
    ];

    const selectStyle: CSSProperties = {
      padding: '6px 12px',
      border: '1px solid #d1d5db',
      borderRadius: '6px',
      fontSize: '13px',
      cursor: 'pointer'
    };

    return (
      <div key={acao.id} style={acaoCard}>
        <div style={headerStyle} onClick={() => setAcaoExpandida(isExpandida ? null : acao.id)}>
          <div style={titleSection}>
            <h3 style={{ margin: '0 0 8px', fontSize: '18px', color: '#1B4F72' }}>
              {acao.what}
            </h3>
            <p style={{ margin: 0, fontSize: '14px', color: '#6b7280' }}>
              <strong>Responsável:</strong> {acao.who} | <strong>Prazo:</strong> {acao.when}
            </p>
          </div>

          <div style={actionsSection}>
            {!readonly && (
              <select
                value={acao.status}
                onChange={(e) => {
                  e.stopPropagation();
                  atualizarAcao(acao.id, 'status', e.target.value);
                }}
                style={selectStyle}
                onClick={(e) => e.stopPropagation()}
              >
                {statusOptions.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            )}
            {readonly && (
              <Badge variant={
                acao.status === 'concluido' ? 'success' :
                acao.status === 'em_andamento' ? 'warning' : 'default'
              }>
                {statusOptions.find(opt => opt.value === acao.status)?.label}
              </Badge>
            )}
            {!readonly && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  removerAcao(acao.id);
                }}
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

        {isExpandida && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '20px'
          }}>
            <div>
              {renderCampo(acao.id, 'what', 'O QUE será feito?', 'Descreva a ação...', '📋', true)}
              {renderCampo(acao.id, 'why', 'POR QUE será feito?', 'Justificativa...', '🎯', true)}
              {renderCampo(acao.id, 'how', 'COMO será feito?', 'Método/Processo...', '⚙️', true)}
            </div>

            <div>
              {renderCampo(acao.id, 'who', 'QUEM fará?', 'Responsável...', '👤')}
              {renderCampo(acao.id, 'when', 'QUANDO será feito?', 'Prazo...', '📅')}
              {renderCampo(acao.id, 'where', 'ONDE será feito?', 'Local...', '📍')}
              {renderCampo(acao.id, 'howMuch', 'QUANTO custará?', 'Custo estimado...', '💰')}
            </div>
          </div>
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

  const statsStyle: CSSProperties = {
    display: 'flex',
    gap: '16px',
    marginBottom: '24px',
    padding: '16px',
    background: '#f8f9fa',
    borderRadius: '12px'
  };

  const statItem: CSSProperties = {
    flex: 1,
    textAlign: 'center'
  };

  const totalAcoes = data5w2h.acoes.length;
  const pendentes = data5w2h.acoes.filter(a => a.status === 'pendente').length;
  const emAndamento = data5w2h.acoes.filter(a => a.status === 'em_andamento').length;
  const concluidas = data5w2h.acoes.filter(a => a.status === 'concluido').length;

  return (
    <div style={containerStyle}>
      <div style={titleStyle}>5W2H - Plano de Ação</div>
      <div style={subtitleStyle}>
        Defina ações detalhadas respondendo: O que, Por que, Onde, Quando, Quem, Como e Quanto custa
      </div>

      {totalAcoes > 0 && (
        <div style={statsStyle}>
          <div style={statItem}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1B4F72' }}>{totalAcoes}</div>
            <div style={{ fontSize: '12px', color: '#6b7280' }}>Total de Ações</div>
          </div>
          <div style={statItem}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#95a5a6' }}>{pendentes}</div>
            <div style={{ fontSize: '12px', color: '#6b7280' }}>Pendentes</div>
          </div>
          <div style={statItem}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#F39C12' }}>{emAndamento}</div>
            <div style={{ fontSize: '12px', color: '#6b7280' }}>Em Andamento</div>
          </div>
          <div style={statItem}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#27AE60' }}>{concluidas}</div>
            <div style={{ fontSize: '12px', color: '#6b7280' }}>Concluídas</div>
          </div>
        </div>
      )}

      {data5w2h.acoes.map(acao => renderAcao(acao))}

      {!readonly && (
        <Button
          variant="primary"
          onClick={adicionarAcao}
          style={{ marginTop: '16px' }}
        >
          + Adicionar Ação
        </Button>
      )}

      {data5w2h.acoes.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '60px 20px',
          color: '#9ca3af',
          fontSize: '16px'
        }}>
          Nenhuma ação definida ainda. Clique em "Adicionar Ação" para começar.
        </div>
      )}
    </div>
  );
};

export default Workspace5W2H;
