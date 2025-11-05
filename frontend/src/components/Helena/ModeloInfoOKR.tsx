/**
 * Componente de Informações Detalhadas - Modelo OKR
 * Modal/Drawer com tabs explicativas sobre o modelo OKR
 */
import React, { useState, CSSProperties } from 'react';
import { Button } from '../ui/Button';

interface ModeloInfoOKRProps {
  isOpen: boolean;
  onClose: () => void;
  onIniciar: () => void;
}

export const ModeloInfoOKR: React.FC<ModeloInfoOKRProps> = ({
  isOpen,
  onClose,
  onIniciar
}) => {
  const [abaAtiva, setAbaAtiva] = useState<'o-que-e' | 'quando-usar' | 'como-usar'>('o-que-e');

  if (!isOpen) return null;

  // Styles
  const overlayStyle: CSSProperties = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 9999,
    padding: '20px'
  };

  const modalStyle: CSSProperties = {
    backgroundColor: '#ffffff',
    borderRadius: '16px',
    maxWidth: '900px',
    width: '100%',
    maxHeight: '90vh',
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
    boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)'
  };

  const headerStyle: CSSProperties = {
    background: 'linear-gradient(135deg, #1B4F72 0%, #3498DB 100%)',
    color: '#ffffff',
    padding: '24px 32px',
    borderBottom: '4px solid #3498DB'
  };

  const titleStyle: CSSProperties = {
    fontSize: '28px',
    fontWeight: 'bold',
    margin: '0 0 8px 0',
    display: 'flex',
    alignItems: 'center',
    gap: '12px'
  };

  const subtitleStyle: CSSProperties = {
    fontSize: '16px',
    opacity: 0.9,
    margin: 0
  };

  const tabsContainerStyle: CSSProperties = {
    display: 'flex',
    borderBottom: '2px solid #e5e7eb',
    backgroundColor: '#f8f9fa'
  };

  const tabStyle = (isActive: boolean): CSSProperties => ({
    flex: 1,
    padding: '16px 24px',
    border: 'none',
    background: isActive ? '#ffffff' : 'transparent',
    color: isActive ? '#1B4F72' : '#6b7280',
    fontSize: '15px',
    fontWeight: isActive ? 'bold' : 'normal',
    cursor: 'pointer',
    borderBottom: isActive ? '3px solid #3498DB' : '3px solid transparent',
    transition: 'all 0.3s ease'
  });

  const contentContainerStyle: CSSProperties = {
    flex: 1,
    overflow: 'auto',
    padding: '32px'
  };

  const footerStyle: CSSProperties = {
    padding: '20px 32px',
    borderTop: '2px solid #e5e7eb',
    display: 'flex',
    gap: '12px',
    justifyContent: 'flex-end',
    backgroundColor: '#f8f9fa'
  };

  const sectionTitleStyle: CSSProperties = {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#1B4F72',
    marginTop: '0',
    marginBottom: '16px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  };

  const paragraphStyle: CSSProperties = {
    fontSize: '15px',
    lineHeight: '1.7',
    color: '#2C3E50',
    marginBottom: '16px'
  };

  const listStyle: CSSProperties = {
    marginLeft: '20px',
    marginBottom: '20px'
  };

  const listItemStyle: CSSProperties = {
    fontSize: '15px',
    lineHeight: '1.7',
    color: '#2C3E50',
    marginBottom: '10px'
  };

  const highlightBoxStyle: CSSProperties = {
    backgroundColor: '#E8F4F8',
    border: '2px solid #3498DB',
    borderRadius: '12px',
    padding: '20px',
    marginBottom: '20px'
  };

  const warningBoxStyle: CSSProperties = {
    backgroundColor: '#FEF3E2',
    border: '2px solid #F39C12',
    borderRadius: '12px',
    padding: '20px',
    marginBottom: '20px'
  };

  const closeButtonStyle: CSSProperties = {
    position: 'absolute',
    top: '24px',
    right: '24px',
    background: 'rgba(255, 255, 255, 0.2)',
    border: 'none',
    color: '#ffffff',
    fontSize: '28px',
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'all 0.2s ease'
  };

  // Content renderers
  const renderOQueE = () => (
    <div>
      <div style={highlightBoxStyle}>
        <h3 style={{ ...sectionTitleStyle, marginTop: 0 }}>🎯 O que é OKR?</h3>
        <p style={paragraphStyle}>
          <strong>OKR (Objectives and Key Results)</strong> é uma metodologia de gestão estratégica que
          define objetivos ambiciosos e resultados-chave mensuráveis para orientar equipes e organizações
          em direção a metas comuns.
        </p>
      </div>

      <h3 style={sectionTitleStyle}>📋 Estrutura do OKR</h3>
      <ul style={listStyle}>
        <li style={listItemStyle}>
          <strong>Objetivos:</strong> Metas qualitativas, inspiradoras e ambiciosas que definem "onde queremos chegar"
        </li>
        <li style={listItemStyle}>
          <strong>Key Results (Resultados-Chave):</strong> Métricas quantitativas que indicam "como saberemos que chegamos lá"
        </li>
      </ul>

      <h3 style={sectionTitleStyle}>🏛️ OKR no Setor Público</h3>
      <p style={paragraphStyle}>
        No contexto do governo federal, o OKR é adaptado para:
      </p>
      <ul style={listStyle}>
        <li style={listItemStyle}>Foco em impacto social e valor público (não apenas lucro)</li>
        <li style={listItemStyle}>Alinhamento com políticas públicas e diretrizes estratégicas</li>
        <li style={listItemStyle}>Transparência e prestação de contas à sociedade</li>
        <li style={listItemStyle}>Melhoria contínua dos serviços prestados ao cidadão</li>
      </ul>

      <div style={highlightBoxStyle}>
        <h4 style={{ margin: '0 0 12px', color: '#1B4F72' }}>✨ Exemplo de OKR Público:</h4>
        <p style={{ margin: '0 0 8px', fontWeight: 'bold' }}>
          Objetivo: Melhorar a experiência do cidadão no atendimento digital
        </p>
        <p style={{ margin: '0 0 4px', fontSize: '14px' }}>
          📊 KR1: Aumentar a satisfação do usuário de 65% para 85% até dezembro
        </p>
        <p style={{ margin: '0 0 4px', fontSize: '14px' }}>
          📊 KR2: Reduzir o tempo médio de atendimento de 15min para 8min
        </p>
        <p style={{ margin: '0', fontSize: '14px' }}>
          📊 KR3: Elevar a taxa de resolução no primeiro contato de 40% para 70%
        </p>
      </div>
    </div>
  );

  const renderQuandoUsar = () => (
    <div>
      <h3 style={sectionTitleStyle}>✅ Use OKR quando você precisa:</h3>
      <ul style={listStyle}>
        <li style={listItemStyle}>
          <strong>Alinhar equipes</strong> em torno de objetivos estratégicos comuns
        </li>
        <li style={listItemStyle}>
          <strong>Mensurar progresso</strong> de forma clara e objetiva
        </li>
        <li style={listItemStyle}>
          <strong>Aumentar o foco</strong> e priorizar iniciativas de maior impacto
        </li>
        <li style={listItemStyle}>
          <strong>Promover transparência</strong> sobre metas e resultados
        </li>
        <li style={listItemStyle}>
          <strong>Engajar equipes</strong> com metas desafiadoras mas alcançáveis
        </li>
      </ul>

      <h3 style={sectionTitleStyle}>👥 Contextos Ideais</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginBottom: '20px' }}>
        <div style={{ ...highlightBoxStyle, padding: '16px' }}>
          <h4 style={{ margin: '0 0 8px', color: '#3498DB' }}>🏢 Organizacional</h4>
          <p style={{ margin: 0, fontSize: '14px' }}>
            Órgãos públicos que precisam traduzir estratégia em ação mensurável
          </p>
        </div>
        <div style={{ ...highlightBoxStyle, padding: '16px' }}>
          <h4 style={{ margin: '0 0 8px', color: '#3498DB' }}>🎯 Projetos</h4>
          <p style={{ margin: 0, fontSize: '14px' }}>
            Iniciativas com objetivos claros e prazos definidos
          </p>
        </div>
        <div style={{ ...highlightBoxStyle, padding: '16px' }}>
          <h4 style={{ margin: '0 0 8px', color: '#3498DB' }}>🔄 Transformação</h4>
          <p style={{ margin: 0, fontSize: '14px' }}>
            Processos de mudança que exigem acompanhamento rigoroso
          </p>
        </div>
      </div>

      <h3 style={sectionTitleStyle}>📏 Tamanho de Equipe</h3>
      <ul style={listStyle}>
        <li style={listItemStyle}>
          <strong>Pequenas equipes (5-15 pessoas):</strong> OKRs por equipe
        </li>
        <li style={listItemStyle}>
          <strong>Departamentos (15-50 pessoas):</strong> OKRs por área + cascateamento
        </li>
        <li style={listItemStyle}>
          <strong>Órgãos inteiros (50+ pessoas):</strong> OKRs estratégicos + táticos + individuais
        </li>
      </ul>

      <div style={warningBoxStyle}>
        <h4 style={{ margin: '0 0 12px', color: '#E67E22' }}>⚠️ Quando NÃO usar OKR:</h4>
        <ul style={{ margin: 0, paddingLeft: '20px' }}>
          <li style={listItemStyle}>Atividades rotineiras e operacionais (use SOP/POP)</li>
          <li style={listItemStyle}>Projetos sem metas mensuráveis claras</li>
          <li style={listItemStyle}>Contextos que exigem apenas cumprimento de normas</li>
          <li style={listItemStyle}>Quando a equipe não tem autonomia para influenciar resultados</li>
        </ul>
      </div>
    </div>
  );

  const renderComoUsar = () => (
    <div>
      <h3 style={sectionTitleStyle}>🚀 Passo a Passo para Criar OKRs</h3>

      <div style={{ marginBottom: '24px' }}>
        <div style={{ ...highlightBoxStyle, borderLeft: '6px solid #3498DB' }}>
          <h4 style={{ margin: '0 0 8px', color: '#1B4F72' }}>1️⃣ Defina o Objetivo</h4>
          <p style={paragraphStyle}>
            Escreva uma meta <strong>qualitativa, inspiradora e ambiciosa</strong>. Pergunte-se:
            "O que queremos alcançar?" e "Por que isso importa?"
          </p>
          <p style={{ margin: 0, fontSize: '14px', fontStyle: 'italic' }}>
            Exemplo: "Transformar a experiência de atendimento ao cidadão"
          </p>
        </div>
      </div>

      <div style={{ marginBottom: '24px' }}>
        <div style={{ ...highlightBoxStyle, borderLeft: '6px solid #27AE60' }}>
          <h4 style={{ margin: '0 0 8px', color: '#1B4F72' }}>2️⃣ Defina 3-5 Key Results</h4>
          <p style={paragraphStyle}>
            Para cada objetivo, liste <strong>3 a 5 resultados mensuráveis</strong>. Cada KR deve:
          </p>
          <ul style={{ margin: '0 0 12px', paddingLeft: '20px' }}>
            <li style={{ fontSize: '14px', marginBottom: '4px' }}>Ser quantificável (número, %, tempo)</li>
            <li style={{ fontSize: '14px', marginBottom: '4px' }}>Ter prazo definido</li>
            <li style={{ fontSize: '14px', marginBottom: '4px' }}>Ser desafiador mas alcançável</li>
          </ul>
          <p style={{ margin: 0, fontSize: '14px', fontStyle: 'italic' }}>
            Exemplo: "Reduzir tempo de espera de 20min para 10min até Q4"
          </p>
        </div>
      </div>

      <div style={{ marginBottom: '24px' }}>
        <div style={{ ...highlightBoxStyle, borderLeft: '6px solid #9B59B6' }}>
          <h4 style={{ margin: '0 0 8px', color: '#1B4F72' }}>3️⃣ Defina Responsáveis</h4>
          <p style={{ margin: 0, fontSize: '14px' }}>
            Atribua um <strong>dono</strong> para cada Key Result. Essa pessoa será responsável por
            acompanhar e reportar progresso.
          </p>
        </div>
      </div>

      <div style={{ marginBottom: '24px' }}>
        <div style={{ ...highlightBoxStyle, borderLeft: '6px solid #E67E22' }}>
          <h4 style={{ margin: '0 0 8px', color: '#1B4F72' }}>4️⃣ Acompanhe Regularmente</h4>
          <p style={{ margin: 0, fontSize: '14px' }}>
            Realize <strong>check-ins semanais ou quinzenais</strong> para atualizar progresso,
            identificar bloqueios e ajustar estratégias.
          </p>
        </div>
      </div>

      <h3 style={sectionTitleStyle}>✨ Melhores Práticas no Setor Público</h3>
      <ul style={listStyle}>
        <li style={listItemStyle}>
          <strong>Alinhamento estratégico:</strong> Conecte OKRs às diretrizes do órgão/ministério
        </li>
        <li style={listItemStyle}>
          <strong>Transparência:</strong> Compartilhe OKRs publicamente com a equipe
        </li>
        <li style={listItemStyle}>
          <strong>Ciclos trimestrais:</strong> Revise e ajuste OKRs a cada 3 meses
        </li>
        <li style={listItemStyle}>
          <strong>Foco em impacto:</strong> Priorize métricas que beneficiam o cidadão
        </li>
        <li style={listItemStyle}>
          <strong>Aprendizado:</strong> Use OKRs não atingidos como oportunidade de melhoria
        </li>
      </ul>

      <div style={warningBoxStyle}>
        <h4 style={{ margin: '0 0 12px', color: '#E67E22' }}>❌ Erros Comuns a Evitar</h4>
        <ul style={{ margin: 0, paddingLeft: '20px' }}>
          <li style={listItemStyle}>Criar objetivos muito genéricos ("Melhorar processos")</li>
          <li style={listItemStyle}>Definir Key Results não mensuráveis ("Aumentar satisfação")</li>
          <li style={listItemStyle}>Ter OKRs demais (máximo 3-5 objetivos por ciclo)</li>
          <li style={listItemStyle}>Não revisar progresso regularmente</li>
          <li style={listItemStyle}>Usar OKRs como avaliação de desempenho individual</li>
        </ul>
      </div>
    </div>
  );

  return (
    <div style={overlayStyle} onClick={onClose}>
      <div style={modalStyle} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={{ position: 'relative' }}>
          <div style={headerStyle}>
            <h2 style={titleStyle}>
              🎯 Modelo OKR
            </h2>
            <p style={subtitleStyle}>
              Objectives and Key Results - Gestão por Objetivos Mensuráveis
            </p>
          </div>
          <button
            onClick={onClose}
            style={closeButtonStyle}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)';
              e.currentTarget.style.transform = 'scale(1.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
              e.currentTarget.style.transform = 'scale(1)';
            }}
          >
            ×
          </button>
        </div>

        {/* Tabs */}
        <div style={tabsContainerStyle}>
          <button
            style={tabStyle(abaAtiva === 'o-que-e')}
            onClick={() => setAbaAtiva('o-que-e')}
          >
            📖 O que é
          </button>
          <button
            style={tabStyle(abaAtiva === 'quando-usar')}
            onClick={() => setAbaAtiva('quando-usar')}
          >
            🎯 Quando usar
          </button>
          <button
            style={tabStyle(abaAtiva === 'como-usar')}
            onClick={() => setAbaAtiva('como-usar')}
          >
            🚀 Como usar
          </button>
        </div>

        {/* Content */}
        <div style={contentContainerStyle}>
          {abaAtiva === 'o-que-e' && renderOQueE()}
          {abaAtiva === 'quando-usar' && renderQuandoUsar()}
          {abaAtiva === 'como-usar' && renderComoUsar()}
        </div>

        {/* Footer Actions */}
        <div style={footerStyle}>
          <Button variant="secondary" onClick={onClose}>
            Fechar
          </Button>
          <Button variant="secondary" onClick={() => alert('Em breve: Exemplos de OKR')}>
            📚 Ver Exemplos
          </Button>
          <Button variant="secondary" onClick={() => alert('Em breve: Download PDF')}>
            📄 Baixar PDF
          </Button>
          <Button variant="primary" onClick={() => { onIniciar(); onClose(); }}>
            🎯 Iniciar OKR
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ModeloInfoOKR;
