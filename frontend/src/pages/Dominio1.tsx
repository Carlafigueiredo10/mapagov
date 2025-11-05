/**
 * Domínio 1 - Abordagens e Fundamentos de Gestão
 * Página de conteúdo do primeiro domínio MGI
 */

import React from 'react';
import './Dominio.css';

export const Dominio1: React.FC = () => {
  return (
    <div className="dominio-container">
      {/* Header do Domínio */}
      <header className="dominio-header dominio-1-header">
        <div className="dominio-badge">Domínio 1</div>
        <h1>🟦 Abordagens e Fundamentos de Gestão</h1>
      </header>

      {/* Conteúdo Principal */}
      <main className="dominio-content">
        {/* Propósito */}
        <section className="dominio-section">
          <h2>🎯 Propósito</h2>
          <p className="proposito-text">
            Estabelecer a base do planejamento — o porquê e o como do projeto.
            Aqui, o gestor define a abordagem (tradicional, ágil, híbrida),
            o modelo de planejamento e o modo de trabalho da equipe.
          </p>
        </section>

        {/* O que fazer na prática */}
        <section className="dominio-section">
          <h2>⚙️ O que fazer na prática</h2>

          <div className="pratica-item">
            <h3>1. Escolha sua abordagem de gestão:</h3>
            <ul>
              <li><strong>Tradicional</strong> (ex: 5W2H, cronograma linear)</li>
              <li><strong>Ágil</strong> (ex: OKR, Kanban, ciclos curtos)</li>
              <li><strong>Híbrida</strong> (combina previsibilidade + adaptação)</li>
            </ul>
          </div>

          <div className="pratica-item">
            <h3>2. Defina o problema e o propósito:</h3>
            <ul>
              <li>Que necessidade institucional ou pública esse projeto resolve?</li>
              <li>Que valor público ele pretende gerar?</li>
            </ul>
          </div>

          <div className="pratica-item">
            <h3>3. Identifique aprendizados anteriores:</h3>
            <ul>
              <li>Há projetos similares na unidade?</li>
              <li>O que funcionou e o que não funcionou?</li>
            </ul>
          </div>

          <div className="pratica-item">
            <h3>4. Organize a equipe inicial e o ritual de acompanhamento:</h3>
            <ul>
              <li>Quem conduz?</li>
              <li>Como as decisões serão registradas (reuniões, atas, dashboard)?</li>
            </ul>
          </div>
        </section>

        {/* Artefatos Recomendados */}
        <section className="dominio-section">
          <h2>🧰 Artefatos recomendados</h2>

          <div className="artefatos-table-wrapper">
            <table className="artefatos-table">
              <thead>
                <tr>
                  <th>Ferramenta</th>
                  <th>Para quê usar</th>
                  <th>Quando aplicar</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Canvas de Projeto Público</strong></td>
                  <td>Definir propósito, escopo e entregas iniciais.</td>
                  <td>Início do projeto.</td>
                </tr>
                <tr>
                  <td><strong>Matriz 5W2H</strong></td>
                  <td>Detalhar ações e responsabilidades iniciais.</td>
                  <td>Planejamento rápido.</td>
                </tr>
                <tr>
                  <td><strong>Linha do Tempo Inicial</strong></td>
                  <td>Visualizar o percurso previsto.</td>
                  <td>Após definição de escopo.</td>
                </tr>
                <tr>
                  <td><strong>Checklist de Governança</strong></td>
                  <td>Garantir que papéis e decisões estão claros.</td>
                  <td>Após definição da equipe.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* Indicadores de Maturidade */}
        <section className="dominio-section">
          <h2>📊 Indicadores simples de maturidade</h2>

          <div className="indicadores-list">
            <div className="indicador-item">
              <span className="indicador-icon">✅</span>
              <p>O projeto tem objetivos escritos e mensuráveis.</p>
            </div>
            <div className="indicador-item">
              <span className="indicador-icon">✅</span>
              <p>A equipe sabe qual é o valor público esperado.</p>
            </div>
            <div className="indicador-item">
              <span className="indicador-icon">✅</span>
              <p>Há um ponto de contato único responsável pelo projeto.</p>
            </div>
          </div>
        </section>

        {/* Exemplo Prático */}
        <section className="dominio-section exemplo-pratico">
          <h2>🗂️ Exemplo prático (baseado em casos do Guia)</h2>

          <div className="exemplo-box">
            <p>
              <strong>Marina</strong>, gestora de saúde, iniciou o projeto
              <em>"Equidade no Atendimento"</em>.
            </p>
            <p>
              Antes de definir indicadores, ela aplicou um canvas simples para mapear
              as dores dos usuários e alinhou a equipe sobre o propósito central:
              <strong>"garantir atendimento digno e acessível a grupos vulneráveis."</strong>
            </p>
            <p>
              A clareza do propósito guiou todas as decisões seguintes.
            </p>
          </div>
        </section>

        {/* Navegação entre domínios */}
        <nav className="dominio-navigation">
          <button className="nav-btn nav-prev" disabled>
            ← Domínio Anterior
          </button>
          <button className="nav-btn nav-next" onClick={() => window.location.href = '/dominio2'}>
            Próximo Domínio: Escopo e valor →
          </button>
        </nav>
      </main>
    </div>
  );
};

export default Dominio1;
