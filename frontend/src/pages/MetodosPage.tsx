/**
 * Página de Métodos de Gestão e Execução Estratégica
 * Lista OKR e Hoshin Kanri com navegação para páginas individuais
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import './MetodosPage.css';

interface Metodo {
  id: string;
  nome: string;
  descricao: string;
  url: string;
  icone: string;
  complexidade: string;
  prazo: string;
}

const METODOS: Metodo[] = [
  {
    id: 'okr',
    nome: 'OKR',
    descricao: 'Para que usar: Definir objetivos ambiciosos com resultados-chave mensuráveis. Como usar: Estabeleça 3-5 objetivos qualitativos e para cada um defina 3-5 resultados-chave quantificáveis. Revise trimestralmente.',
    url: '/metodos/okr',
    icone: '🎯',
    complexidade: 'Baixa',
    prazo: 'Curto'
  },
  {
    id: 'hoshin',
    nome: 'Hoshin Kanri',
    descricao: 'Para que usar: Desdobrar estratégia em cascata por toda a organização. Como usar: Defina diretrizes estratégicas no topo e desdobre em metas operacionais para cada nível hierárquico, garantindo alinhamento vertical.',
    url: '/metodos/hoshin',
    icone: '🧭',
    complexidade: 'Alta',
    prazo: 'Longo'
  }
];

const MetodosPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="metodos-page">
      <div className="metodos-header-page">
        <button
          className="btn-voltar"
          onClick={() => window.history.back()}
        >
          ← Voltar
        </button>
        <h1>🎯 Métodos de Gestão e Execução Estratégica</h1>
        <p className="subtitle">Ferramentas práticas para aplicar, acompanhar e melhorar a execução do seu plano</p>
      </div>

      <div className="metodos-lista-page">
        {METODOS.map((metodo) => (
          <div key={metodo.id} className="metodo-item">
            <span className="metodo-icone">{metodo.icone}</span>
            <div className="metodo-conteudo">
              <div className="metodo-header-item">
                <button
                  onClick={() => navigate(metodo.url)}
                  className="metodo-nome"
                >
                  {metodo.nome}
                </button>
                <div className="metodo-badges">
                  <span className="badge-complexidade" data-nivel={metodo.complexidade.toLowerCase()}>
                    {metodo.complexidade}
                  </span>
                  <span className="badge-prazo">
                    {metodo.prazo}
                  </span>
                </div>
              </div>
              <p className="metodo-descricao">{metodo.descricao}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="metodos-info-footer">
        <p>💡 <strong>Dica:</strong> Escolha o método de acordo com a maturidade da sua equipe e o prazo disponível.</p>
      </div>
    </div>
  );
};

export default MetodosPage;
