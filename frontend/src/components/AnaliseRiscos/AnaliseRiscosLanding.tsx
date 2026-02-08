/**
 * AnaliseRiscosLanding - Página inicial institucional de Análise de Riscos
 *
 * Tela de enquadramento exibida antes do wizard.
 * A Helena não realiza avaliações automáticas nem substitui decisões administrativas.
 */
import React from 'react';
import styles from './AnaliseRiscosLanding.module.css';

interface AnaliseRiscosLandingProps {
  onIniciar: () => void;
}

const ETAPAS = [
  {
    titulo: 'Definir o objeto da análise',
    descricao: 'Indicar se a análise está associada a um projeto, processo, plano ou outro instrumento institucional.',
  },
  {
    titulo: 'Contextualizar o cenário',
    descricao: 'Registrar informações relevantes sobre o ambiente, o escopo e as condições institucionais.',
  },
  {
    titulo: 'Identificar riscos',
    descricao: 'Descrever eventos que possam impactar o alcance dos objetivos institucionais.',
  },
  {
    titulo: 'Avaliar riscos',
    descricao: 'Classificar os riscos com base em critérios de impacto e probabilidade definidos.',
  },
  {
    titulo: 'Consolidar a matriz de riscos',
    descricao: 'Visualizar e organizar os riscos identificados e classificados.',
  },
  {
    titulo: 'Definir respostas aos riscos',
    descricao: 'Registrar estratégias e ações para tratamento, mitigação ou monitoramento.',
  },
];

const HELENA_CAPABILITIES = [
  'esclarecer termos e conceitos;',
  'orientar o uso das etapas da análise;',
  'apoiar a compreensão do método adotado.',
];

const USE_CASES = [
  'projetos em planejamento ou execução;',
  'processos de trabalho;',
  'normas, políticas ou procedimentos;',
  'planos institucionais (PPA, PEI, PDTI, entre outros).',
];

const AnaliseRiscosLanding: React.FC<AnaliseRiscosLandingProps> = ({ onIniciar }) => {
  return (
    <div className={styles.container}>
      {/* Cabeçalho */}
      <header className={styles.header}>
        <h1 className={styles.title}>Análise de Riscos</h1>
      </header>

      {/* Texto institucional */}
      <section className={styles.contextCard}>
        <p>
          Identifique, avalie e trate riscos associados a projetos, processos, planos
          ou instrumentos institucionais, apoiando a tomada de decisão administrativa
          e o fortalecimento da governança.
        </p>
        <p>
          A análise é realizada por meio de um processo estruturado, com registro
          organizado das informações.
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
            <h2 className={styles.helenaTitle}>Helena — Orientação institucional para Análise de Riscos</h2>
            <p className={styles.helenaText}>
              Helena atua como apoio conceitual durante a Análise de Riscos.
              Ela auxilia na compreensão dos conceitos, das etapas e dos critérios
              utilizados, orientando o correto preenchimento das informações.
            </p>
            <p className={styles.helenaLabel}>A Helena pode:</p>
            <ul className={styles.helenaList}>
              {HELENA_CAPABILITIES.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
            <p className={styles.helenaDisclaimer}>
              As informações registradas e as decisões tomadas são de responsabilidade
              do usuário e das instâncias institucionais competentes.
              A Helena não realiza avaliações automáticas nem substitui decisões
              formais de governança.
            </p>
          </div>
        </div>
      </section>

      {/* Quando utilizar */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Quando utilizar a Análise de Riscos</h2>
        <p className={styles.sectionIntro}>
          Utilize esta ferramenta quando precisar avaliar riscos relacionados a:
        </p>
        <ul className={styles.useCaseList}>
          {USE_CASES.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
        <p className={styles.useCaseNote}>
          A análise pode ser criada no início, durante a execução ou revisada
          sempre que houver mudanças relevantes no contexto institucional.
        </p>
      </section>

      {/* Como funciona */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Como funciona a análise</h2>
        <p className={styles.sectionIntro}>
          Ao iniciar uma nova Análise de Riscos, você será orientado a seguir as etapas abaixo:
        </p>
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

      {/* Bloco de decisão */}
      <section className={styles.decisionBlock}>
        <h2 className={styles.sectionTitle}>Quando faz sentido iniciar agora</h2>
        <p className={styles.decisionText}>
          É indicado iniciar uma Análise de Riscos quando houver um objeto institucional
          definido — como um projeto, processo ou plano — e a necessidade de registrar,
          de forma estruturada, os riscos associados ao seu contexto.
        </p>
      </section>

      {/* CTA */}
      <section className={styles.ctaSection}>
        <p className={styles.ctaText}>
          Inicie uma nova Análise de Riscos quando estiver pronto para registrar
          e avaliar os riscos do seu contexto institucional.
        </p>
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
