/**
 * AnaliseRiscosLanding - Página inicial institucional de Análise de Riscos
 *
 * Tela de enquadramento exibida antes do wizard.
 * A Helena é um elemento visual institucional estático, não interativo.
 */
import React from 'react';
import styles from './AnaliseRiscosLanding.module.css';

interface AnaliseRiscosLandingProps {
  onIniciar: () => void;
}

const ETAPAS = [
  {
    titulo: 'Definição do objeto da análise',
    descricao: 'Identificação do projeto, processo, norma ou plano a ser avaliado.',
  },
  {
    titulo: 'Contextualização',
    descricao: 'Registro de informações relevantes para compreensão do ambiente e do escopo.',
  },
  {
    titulo: 'Identificação dos riscos',
    descricao: 'Levantamento dos eventos que podem impactar o alcance dos objetivos institucionais.',
  },
  {
    titulo: 'Análise e classificação',
    descricao: 'Avaliação de probabilidade e impacto, conforme critérios definidos.',
  },
  {
    titulo: 'Matriz de riscos',
    descricao: 'Consolidação visual dos riscos identificados e classificados.',
  },
  {
    titulo: 'Resposta aos riscos',
    descricao: 'Definição de estratégias e ações para o tratamento dos riscos.',
  },
];

const AnaliseRiscosLanding: React.FC<AnaliseRiscosLandingProps> = ({ onIniciar }) => {
  return (
    <div className={styles.container}>
      {/* Cabeçalho */}
      <header className={styles.header}>
        <h1 className={styles.title}>Análise de Riscos</h1>
        <p className={styles.subtitle}>Ferramenta de apoio à governança pública</p>
      </header>

      {/* Texto institucional */}
      <section className={styles.institutionalText}>
        <p>
          A Análise de Riscos do MapaGov é um instrumento institucional de apoio à identificação,
          avaliação e tratamento de riscos associados às atividades da administração pública,
          com foco na tomada de decisão administrativa e no fortalecimento da governança.
        </p>
      </section>

      {/* Card Helena */}
      <section className={styles.helenaCard}>
        <div className={styles.helenaCardInner}>
          <div className={styles.helenaAvatar}>
            <img
              src="/helena_riscos.png"
              alt="Helena - Orientação institucional"
            />
          </div>
          <div className={styles.helenaContent}>
            <h2 className={styles.helenaTitle}>Helena — Orientação institucional</h2>
            <p className={styles.helenaText}>
              Este instrumento organiza a análise de riscos em etapas estruturadas,
              permitindo avaliar impactos, probabilidades e respostas associadas
              a atividades institucionais.
            </p>
            <p className={styles.helenaDisclaimer}>
              As informações geradas não substituem a avaliação do responsável institucional.
            </p>
          </div>
        </div>
      </section>

      {/* Quando utilizar */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Quando utilizar a Análise de Riscos</h2>
        <ul className={styles.useCaseList}>
          <li>Avaliar riscos relacionados a um projeto</li>
          <li>Avaliar riscos em um processo de trabalho</li>
          <li>Avaliar riscos associados a uma norma, política ou procedimento</li>
          <li>Apoiar decisões vinculadas a um plano institucional</li>
        </ul>
        <p className={styles.useCaseNote}>
          A análise pode ser realizada tanto na criação quanto na revisão desses objetos.
        </p>
      </section>

      {/* Como funciona */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Como funciona a análise</h2>
        <ol className={styles.stepsList}>
          {ETAPAS.map((etapa, index) => (
            <li key={index} className={styles.stepItem}>
              <span className={styles.stepNumber}>{index + 1}</span>
              <div className={styles.stepContent}>
                <h3 className={styles.stepTitle}>{etapa.titulo}</h3>
                <p className={styles.stepDescription}>{etapa.descricao}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      {/* CTA */}
      <section className={styles.ctaSection}>
        <button
          type="button"
          className={styles.ctaButton}
          onClick={onIniciar}
        >
          Iniciar análise de riscos
        </button>
      </section>
    </div>
  );
};

export default AnaliseRiscosLanding;
