/**
 * Página Individual de Método
 * Renderiza conteúdo completo com abas (O que é, Quando usar, Como usar, Exemplos)
 */
import React, { useState } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import modelosData from '../data/modelosContent.json';
import './ModeloPlanejamento.css';

export const MetodoIndividual: React.FC = () => {
  const params = useParams<{ metodoId?: string }>();
  const location = useLocation();
  const navigate = useNavigate();

  // Extrai metodoId tanto de /metodos/:metodoId quanto de /planejamento-estrategico/modelos/:metodoId
  let metodoId = params.metodoId;
  if (!metodoId) {
    // Fallback para rota legada /planejamento-estrategico/modelos/okr ou /planejamento-estrategico/modelos/hoshin
    const match = location.pathname.match(/\/planejamento-estrategico\/modelos\/(okr|hoshin)/);
    if (match) {
      metodoId = match[1];
    }
  }

  const modelo = modelosData[metodoId as keyof typeof modelosData];
  const tabKeys = modelo ? Object.keys(modelo.tabs) : [];
  const [abaAtiva, setAbaAtiva] = useState(tabKeys[0] || '');

  // Fallback para método não encontrado
  if (!modelo) {
    return (
      <div className="modelo-not-found">
        <div className="error-container">
          <h2>⚠️ Método não encontrado</h2>
          <p>O conteúdo para <strong>{metodoId}</strong> ainda não está disponível.</p>
          <button className="btn-voltar" onClick={() => navigate('/metodos')}>
            ← Voltar para Métodos
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
                      <li key={j}>
                        <ReactMarkdown>{item}</ReactMarkdown>
                      </li>
                    ))}
                  </ul>
                )}
                {passo.exemplo && (
                  <div className="passo-exemplo">
                    <strong>Exemplo:</strong> {passo.exemplo}
                  </div>
                )}
              </div>
            ))}
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

      case 'alerta':
        return (
          <div key={index} className="secao-alerta">
            {secao.titulo && (
              <h3>
                {secao.icone} {secao.titulo}
              </h3>
            )}
            <ul>
              {secao.itens.map((item: string, i: number) => (
                <li key={i}>
                  <ReactMarkdown>{item}</ReactMarkdown>
                </li>
              ))}
            </ul>
          </div>
        );

      case 'exemplo':
        return (
          <div key={index} className="secao-exemplo">
            {secao.titulo && <h3>{secao.titulo}</h3>}
            <div className="exemplo-objetivo">
              <strong>Objetivo:</strong> {secao.objetivo}
            </div>
            <div className="exemplo-krs">
              {secao.keyResults.map((kr: string, i: number) => (
                <div key={i} className="kr-item">
                  {kr}
                </div>
              ))}
            </div>
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
                  <div className="card-icon">{card.icone}</div>
                  <h4>{card.titulo}</h4>
                  <p>{card.descricao}</p>
                </div>
              ))}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  const renderConteudoAba = () => {
    if (!abaAtiva || !modelo.tabs[abaAtiva as keyof typeof modelo.tabs]) {
      return <p>Selecione uma aba para visualizar o conteúdo.</p>;
    }

    const aba = modelo.tabs[abaAtiva as keyof typeof modelo.tabs];
    return (
      <div className="aba-conteudo">
        {aba.secoes.map((secao: any, index: number) => renderSecao(secao, index))}
      </div>
    );
  };

  return (
    <div className="modelo-planejamento-page">
      {/* Header */}
      <div className="modelo-header" style={{ borderLeftColor: modelo.cor }}>
        <button className="btn-voltar" onClick={() => navigate('/metodos')}>
          ← Voltar para Métodos
        </button>
        <div className="header-content">
          <span className="modelo-icone">{modelo.icone}</span>
          <div className="header-text">
            <h1>{modelo.titulo}</h1>
            <p>{modelo.subtitulo}</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="modelo-tabs">
        {tabKeys.map((tabKey) => {
          const tab = modelo.tabs[tabKey as keyof typeof modelo.tabs];
          return (
            <button
              key={tabKey}
              className={`tab-button ${abaAtiva === tabKey ? 'active' : ''}`}
              onClick={() => setAbaAtiva(tabKey)}
              style={
                abaAtiva === tabKey
                  ? { borderBottomColor: modelo.cor, color: modelo.cor }
                  : {}
              }
            >
              {tab.icone} {tab.titulo}
            </button>
          );
        })}
      </div>

      {/* Conteúdo da Aba */}
      <div className="modelo-content">{renderConteudoAba()}</div>
    </div>
  );
};

export default MetodoIndividual;
