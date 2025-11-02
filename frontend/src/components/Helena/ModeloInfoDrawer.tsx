/**
 * Componente Generalizado de Informações de Modelos
 * Lê conteúdo de modelosContent.json e renderiza dinamicamente
 * Padrão definitivo Helena - versão aprimorada
 */
import React, { useState, CSSProperties } from 'react';
import ReactMarkdown from 'react-markdown';
import { Button } from '../ui/Button';
import modelosData from '../../data/modelosContent.json';

interface ModeloInfoDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onIniciar: () => void;
  modeloId: string;
}

export const ModeloInfoDrawer: React.FC<ModeloInfoDrawerProps> = ({
  isOpen,
  onClose,
  onIniciar,
  modeloId
}) => {
  // Styles (declarados antes para usar no fallback)
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

  const modelo = modelosData[modeloId as keyof typeof modelosData];
  const tabKeys = modelo ? Object.keys(modelo.tabs) : [];
  const [abaAtiva, setAbaAtiva] = useState(tabKeys[0] || '');

  if (!isOpen) return null;

  // 🔧 Fallback elegante para modelo não encontrado (Recomendação 7)
  if (!modelo) {
    return (
      <div
        style={overlayStyle}
        onMouseDown={(e) => e.target === e.currentTarget && onClose()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="error-title"
      >
        <div style={{
          backgroundColor: '#ffffff',
          borderRadius: '16px',
          padding: '40px',
          maxWidth: '500px',
          textAlign: 'center',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)'
        }}>
          <p id="error-title" style={{ fontSize: '18px', color: '#555', marginBottom: '20px' }}>
            ⚠️ Modelo não encontrado.
          </p>
          <p style={{ fontSize: '14px', color: '#777', marginBottom: '24px' }}>
            O conteúdo para <strong>{modeloId}</strong> ainda não está disponível.
          </p>
          <Button variant="secondary" onClick={onClose}>
            Fechar
          </Button>
        </div>
      </div>
    );
  }

  const headerStyle: CSSProperties = {
    background: `linear-gradient(135deg, #1B4F72 0%, ${modelo.cor} 100%)`,
    color: '#ffffff',
    padding: '24px 32px',
    borderBottom: `4px solid ${modelo.cor}`
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
    borderBottom: isActive ? `3px solid ${modelo.cor}` : '3px solid transparent',
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

  // Renderizadores de seções
  const renderSecao = (secao: any, index: number) => {
    const sectionTitleStyle: CSSProperties = {
      fontSize: '20px',
      fontWeight: 'bold',
      color: '#1B4F72',
      marginTop: index === 0 ? '0' : '24px',
      marginBottom: '16px',
      display: 'flex',
      alignItems: 'center',
      gap: '8px'
    };

    const paragraphStyle: CSSProperties = {
      fontSize: '15px',
      lineHeight: '1.7',
      color: '#2C3E50',
      marginBottom: '16px',
      whiteSpace: 'pre-line'
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
      border: `2px solid ${modelo.cor}`,
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

    switch (secao.tipo) {
      case 'destaque':
        return (
          <div key={index} style={highlightBoxStyle}>
            {secao.titulo && (
              <h3 style={{ ...sectionTitleStyle, marginTop: 0 }}>
                {secao.icone} {secao.titulo}
              </h3>
            )}
            <div style={{ ...paragraphStyle, margin: 0 }}>
              <ReactMarkdown>{secao.conteudo}</ReactMarkdown>
            </div>
          </div>
        );

      case 'lista':
        return (
          <div key={index}>
            {secao.titulo && (
              <h3 style={sectionTitleStyle}>
                {secao.icone} {secao.titulo}
              </h3>
            )}
            {secao.descricao && <p style={paragraphStyle}>{secao.descricao}</p>}
            <ul style={listStyle}>
              {secao.itens.map((item: string, i: number) => (
                <li key={i} style={listItemStyle}>
                  <ReactMarkdown>{item}</ReactMarkdown>
                </li>
              ))}
            </ul>
          </div>
        );

      case 'passos':
        return (
          <div key={index}>
            {secao.titulo && (
              <h3 style={sectionTitleStyle}>
                {secao.icone} {secao.titulo}
              </h3>
            )}
            {secao.passos.map((passo: any, i: number) => (
              <div
                key={i}
                style={{
                  ...highlightBoxStyle,
                  borderLeft: `6px solid ${passo.cor}`
                }}
              >
                <h4 style={{ margin: '0 0 8px', color: '#1B4F72' }}>
                  {passo.numero} {passo.titulo}
                </h4>
                <div style={{ ...paragraphStyle, margin: '0 0 12px' }}>
                  <ReactMarkdown>{passo.descricao}</ReactMarkdown>
                </div>
                {passo.itens && (
                  <ul style={{ margin: '0 0 12px', paddingLeft: '20px' }}>
                    {passo.itens.map((item: string, j: number) => (
                      <li key={j} style={{ fontSize: '14px', marginBottom: '4px' }}>{item}</li>
                    ))}
                  </ul>
                )}
                {passo.exemplo && (
                  <p style={{ margin: 0, fontSize: '14px', fontStyle: 'italic' }}>
                    {passo.exemplo}
                  </p>
                )}
              </div>
            ))}
          </div>
        );

      case 'exemplo':
        return (
          <div key={index} style={highlightBoxStyle}>
            <h4 style={{ margin: '0 0 12px', color: '#1B4F72' }}>
              ✨ {secao.titulo}
            </h4>
            <p style={{ margin: '0 0 8px', fontWeight: 'bold' }}>
              {secao.objetivo}
            </p>
            {secao.keyResults.map((kr: string, i: number) => (
              <p key={i} style={{ margin: '0 0 4px', fontSize: '14px' }}>
                {kr}
              </p>
            ))}
          </div>
        );

      case 'alerta':
        return (
          <div key={index} style={warningBoxStyle}>
            <h4 style={{ margin: '0 0 12px', color: '#E67E22' }}>
              {secao.icone} {secao.titulo}
            </h4>
            <ul style={{ margin: 0, paddingLeft: '20px' }}>
              {secao.itens.map((item: string, i: number) => (
                <li key={i} style={listItemStyle}>{item}</li>
              ))}
            </ul>
          </div>
        );

      case 'cards':
        return (
          <div key={index}>
            {secao.titulo && (
              <h3 style={sectionTitleStyle}>
                {secao.icone} {secao.titulo}
              </h3>
            )}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
              gap: '16px',
              marginBottom: '20px'
            }}>
              {secao.cards.map((card: any, i: number) => (
                <div key={i} style={{ ...highlightBoxStyle, padding: '16px' }}>
                  <h4 style={{ margin: '0 0 8px', color: modelo.cor }}>
                    {card.icone} {card.titulo}
                  </h4>
                  <p style={{ margin: 0, fontSize: '14px' }}>
                    {card.descricao}
                  </p>
                </div>
              ))}
            </div>
          </div>
        );

      case 'texto':
        return (
          <div key={index}>
            {secao.titulo && (
              <h3 style={sectionTitleStyle}>
                {secao.icone} {secao.titulo}
              </h3>
            )}
            <div style={paragraphStyle}>
              <ReactMarkdown>{secao.conteudo}</ReactMarkdown>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  const tabAtual = modelo.tabs[abaAtiva as keyof typeof modelo.tabs];

  return (
    // 🔧 Overlay com onMouseDown + target checking (Recomendação 1)
    <div
      style={overlayStyle}
      onMouseDown={(e) => e.target === e.currentTarget && onClose()}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div style={modalStyle} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={{ position: 'relative' }}>
          <div style={headerStyle}>
            {/* 🔧 Acessibilidade - id para aria-labelledby (Recomendação 5) */}
            <h2 id="modal-title" style={titleStyle}>
              {modelo.icone} {modelo.titulo}
            </h2>
            <p style={subtitleStyle}>
              {modelo.subtitulo}
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
            aria-label="Fechar modal"
          >
            ×
          </button>
        </div>

        {/* Tabs */}
        <div style={tabsContainerStyle} role="tablist">
          {Object.entries(modelo.tabs).map(([key, tab]) => (
            <button
              key={key}
              style={tabStyle(abaAtiva === key)}
              onClick={() => setAbaAtiva(key)}
              role="tab"
              aria-selected={abaAtiva === key}
              aria-controls={`panel-${key}`}
            >
              {tab.icone} {tab.titulo}
            </button>
          ))}
        </div>

        {/* Content */}
        <div
          style={contentContainerStyle}
          role="tabpanel"
          id={`panel-${abaAtiva}`}
          aria-labelledby={`tab-${abaAtiva}`}
        >
          {tabAtual.secoes.map((secao, index) => renderSecao(secao, index))}
        </div>

        {/* Footer Actions */}
        <div style={footerStyle}>
          <Button variant="secondary" onClick={onClose}>
            Fechar
          </Button>
          <Button variant="secondary" onClick={() => alert('Em breve: Exemplos de ' + modelo.titulo)}>
            📚 Ver Exemplos
          </Button>
          <Button variant="secondary" onClick={() => alert('Em breve: Download PDF')}>
            📄 Baixar PDF
          </Button>
          <Button variant="primary" onClick={() => { onIniciar(); onClose(); }}>
            {modelo.icone} Iniciar {modelo.id.toUpperCase()}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ModeloInfoDrawer;
