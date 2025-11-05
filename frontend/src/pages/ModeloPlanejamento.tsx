/**
 * Página Genérica de Modelo de Planejamento
 * Renderiza conteúdo completo de um modelo sem modal
 */
import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import modelosData from '../data/modelosContent.json';
import './ModeloPlanejamento.css';

export const ModeloPlanejamento: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  // Mapeamento de URL para ID do modelo
  const urlToModelId: Record<string, string> = {
    '/classico': 'tradicional',
    '/bsc': 'bsc',
    '/okr': 'okr',
    '/swot': 'swot',
    '/cenarios': 'cenarios',
    '/5w2h': '5w2h'
  };

  const modeloId = urlToModelId[location.pathname];

  const modelo = modelosData[modeloId as keyof typeof modelosData];
  const tabKeys = modelo ? Object.keys(modelo.tabs) : [];
  const [abaAtiva, setAbaAtiva] = useState(tabKeys[0] || '');

  // Fallback para modelo não encontrado
  if (!modelo) {
    return (
      <div className="modelo-not-found">
        <div className="error-container">
          <h2>⚠️ Modelo não encontrado</h2>
          <p>O conteúdo para <strong>{modeloId}</strong> ainda não está disponível.</p>
          <button className="btn-voltar" onClick={() => navigate('/planejamento-estrategico')}>
            ← Voltar para Planejamento Estratégico
          </button>
        </div>
      </div>
    );
  }

  // Renderizadores de seções
  const renderSecao = (secao: any, index: number) => {
    switch (secao.tipo) {
      case 'destaque':
        return (
          <div key={index} className="secao-destaque">
            {secao.titulo && (
              <h3>
                {secao.icone} {secao.titulo}
              </h3>
            )}
            <div className="markdown-content">
              <ReactMarkdown>{secao.conteudo}</ReactMarkdown>
            </div>
          </div>
        );

      case 'lista':
        return (
          <div key={index} className="secao-lista">
            {secao.titulo && (
              <h3>
                {secao.icone} {secao.titulo}
              </h3>
            )}
            {secao.descricao && <p className="secao-descricao">{secao.descricao}</p>}
            <ul>
              {secao.itens.map((item: string, i: number) => (
                <li key={i}>
                  <ReactMarkdown>{item}</ReactMarkdown>
                </li>
              ))}
            </ul>
          </div>
        );

      case 'passos':
        return (
          <div key={index} className="secao-passos">
            {secao.titulo && (
              <h3>
                {secao.icone} {secao.titulo}
              </h3>
            )}
            {secao.passos.map((passo: any, i: number) => (
              <div
                key={i}
                className="passo-card"
                style={{ borderLeftColor: passo.cor }}
              >
                <h4>
                  {passo.numero} {passo.titulo}
                </h4>
                <div className="passo-descricao">
                  <ReactMarkdown>{passo.descricao}</ReactMarkdown>
                </div>
                {passo.itens && (
                  <ul className="passo-itens">
                    {passo.itens.map((item: string, j: number) => (
                      <li key={j}>{item}</li>
                    ))}
                  </ul>
                )}
                {passo.exemplo && (
                  <p className="passo-exemplo">
                    💡 <em>Exemplo: {passo.exemplo}</em>
                  </p>
                )}
              </div>
            ))}
          </div>
        );

      case 'exemplo':
        return (
          <div key={index} className="secao-exemplo">
            <h4>✨ {secao.titulo}</h4>
            <p className="exemplo-objetivo">{secao.objetivo}</p>
            {secao.keyResults.map((kr: string, i: number) => (
              <p key={i} className="exemplo-kr">
                {kr}
              </p>
            ))}
          </div>
        );

      case 'alerta':
        return (
          <div key={index} className="secao-alerta">
            <h4>
              {secao.icone} {secao.titulo}
            </h4>
            <ul>
              {secao.itens.map((item: string, i: number) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
        );

      case 'cards':
        return (
          <div key={index} className="secao-cards">
            {secao.titulo && (
              <h3>
                {secao.icone} {secao.titulo}
              </h3>
            )}
            <div className="cards-grid">
              {secao.cards.map((card: any, i: number) => (
                <div key={i} className="info-card">
                  <h4>
                    {card.icone} {card.titulo}
                  </h4>
                  <p>{card.descricao}</p>
                </div>
              ))}
            </div>
          </div>
        );

      case 'texto':
        return (
          <div key={index} className="secao-texto">
            {secao.titulo && (
              <h3>
                {secao.icone} {secao.titulo}
              </h3>
            )}
            <div className="markdown-content">
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
    <div className="modelo-planejamento-page">
      {/* Header */}
      <div className="modelo-header" style={{ background: `linear-gradient(135deg, #1B4F72 0%, ${modelo.cor} 100%)` }}>
        <button className="btn-voltar-header" onClick={() => navigate('/planejamento-estrategico')}>
          ← Voltar
        </button>
        <h1>
          {modelo.icone} {modelo.titulo}
        </h1>
        <p className="modelo-subtitulo">{modelo.subtitulo}</p>
      </div>

      {/* Tabs */}
      <div className="modelo-tabs">
        {Object.entries(modelo.tabs).map(([key, tab]) => (
          <button
            key={key}
            className={`tab-button ${abaAtiva === key ? 'active' : ''}`}
            onClick={() => setAbaAtiva(key)}
            style={
              abaAtiva === key
                ? { borderBottomColor: modelo.cor, color: '#1B4F72' }
                : {}
            }
          >
            {tab.icone} {tab.titulo}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="modelo-content">
        {tabAtual.secoes.map((secao, index) => renderSecao(secao, index))}
      </div>

      {/* Footer Actions */}
      <div className="modelo-footer">
        <button className="btn-secondary" onClick={() => navigate('/planejamento-estrategico')}>
          ← Voltar
        </button>
        <button className="btn-secondary" onClick={() => alert('Em breve: Exemplos de ' + modelo.titulo)}>
          📚 Ver Mais Exemplos
        </button>
        <button className="btn-secondary" onClick={() => alert('Em breve: Download PDF')}>
          📄 Baixar PDF
        </button>
        <button
          className="btn-primary"
          style={{ background: `linear-gradient(135deg, ${modelo.cor} 0%, #1B4F72 100%)` }}
          onClick={() => {
            navigate('/planejamento-estrategico');
            setTimeout(() => alert(`Iniciando ${modelo.titulo}...`), 100);
          }}
        >
          {modelo.icone} Iniciar {modelo.id.toUpperCase()}
        </button>
      </div>
    </div>
  );
};

export default ModeloPlanejamento;
