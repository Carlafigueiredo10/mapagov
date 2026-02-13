/**
 * PlanejamentoLanding - Página inicial institucional de Planejamento Estratégico
 *
 * Segue o padrão institucional das demais landings (POP, Riscos).
 * A Helena não realiza decisões automáticas nem substitui instâncias de governança.
 */
import React from 'react';
import styles from './PlanejamentoLanding.module.css';

interface PlanejamentoLandingProps {
  onIniciar: () => void;
}

const HELENA_CAPABILITIES = [
  'auxiliar na compreensão dos conceitos e modelos de planejamento;',
  'orientar a escolha do modelo mais adequado ao contexto institucional;',
  'apoiar o preenchimento progressivo das informações ao longo do processo.',
];

const ETAPAS = [
  {
    titulo: 'Diagnóstico institucional',
    descricao: 'Responder perguntas orientadas sobre contexto, maturidade e horizonte de planejamento.',
  },
  {
    titulo: 'Escolha do modelo',
    descricao: 'Selecionar o modelo estratégico recomendado ou escolher diretamente entre as opções disponíveis.',
  },
  {
    titulo: 'Construção guiada',
    descricao: 'Preencher progressivamente os componentes do planejamento com apoio da Helena.',
  },
  {
    titulo: 'Acompanhamento',
    descricao: 'Acompanhar projetos e demandas por meio dos painéis de governança.',
  },
];

const QUANDO_UTILIZAR = [
  'início ou revisão de ciclos oficiais (PPA, PEI, PDTI e instrumentos equivalentes);',
  'criação ou reestruturação de projetos estratégicos;',
  'necessidade de organizar objetivos, metas e indicadores institucionais;',
  'preparação de insumos para instâncias de governança.',
];

const PlanejamentoLanding: React.FC<PlanejamentoLandingProps> = ({ onIniciar }) => {
  return (
    <div className={styles.container}>
      {/* Cabeçalho */}
      <header className={styles.header}>
        <h1 className={styles.title}>Planejamento Estratégico</h1>
        <span className={styles.badgeDesenvolvimento}>Em homologação</span>
      </header>

      {/* Texto institucional */}
      <section className={styles.contextCard}>
        <p>
          Organize objetivos, metas e diretrizes institucionais por meio de modelos
          estruturados de planejamento estratégico, com registro progressivo das
          informações ao longo do ciclo oficial.
        </p>
        <p>
          O sistema oferece sete modelos de planejamento (Estratégico Clássico, BSC,
          SWOT, OKR, Cenários, 5W2H e Hoshin Kanri), além de painéis de acompanhamento
          para projetos e demandas da Direção.
        </p>
      </section>

      {/* Card Helena */}
      <section className={styles.helenaCard}>
        <div className={styles.helenaCardInner}>
          <div className={styles.helenaAvatar}>
            <img
              src="/helena_plano.png"
              alt="Helena - Apoio ao Planejamento Estratégico"
            />
          </div>
          <div className={styles.helenaContent}>
            <h2 className={styles.helenaTitle}>Helena — Apoio ao Planejamento Estratégico</h2>
            <p className={styles.helenaText}>
              Helena atua como apoio conceitual durante o planejamento estratégico.
              Ela auxilia na compreensão dos conceitos, na escolha de modelos e no
              preenchimento progressivo das informações.
            </p>
            <p className={styles.helenaLabel}>A Helena pode:</p>
            <ul className={styles.helenaList}>
              {HELENA_CAPABILITIES.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
            <p className={styles.helenaDisclaimer}>
              As decisões, registros e validações permanecem sob responsabilidade
              do usuário e das instâncias institucionais competentes.
              A Helena não realiza avaliações automáticas nem substitui decisões
              formais de governança.
            </p>
          </div>
        </div>
      </section>

      {/* Quando utilizar */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Quando utilizar o Planejamento Estratégico</h2>
        <p className={styles.sectionIntro}>
          Utilize esta ferramenta quando precisar estruturar ou acompanhar ações relacionadas a:
        </p>
        <ul className={styles.itemList}>
          {QUANDO_UTILIZAR.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
        <p className={styles.itemNote}>
          O planejamento pode ser iniciado a qualquer momento e revisado conforme
          mudanças no contexto institucional.
        </p>
      </section>

      {/* Como funciona */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Como funciona o processo</h2>
        <p className={styles.sectionIntro}>
          Ao iniciar, você será orientado a seguir as etapas abaixo:
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
          É indicado iniciar o planejamento estratégico quando houver uma necessidade
          institucional definida — como o início de um novo ciclo, a criação de projetos
          estratégicos ou a reorganização de objetivos e metas — e disponibilidade para
          registrar as informações de forma progressiva.
        </p>
      </section>

      {/* CTA */}
      <section className={styles.ctaSection}>
        <p className={styles.ctaText}>
          Inicie o planejamento estratégico quando estiver pronto para organizar
          objetivos, escolher modelos e estruturar o ciclo institucional.
        </p>
        <button
          type="button"
          className={styles.ctaButton}
          onClick={onIniciar}
        >
          Iniciar planejamento estratégico
        </button>
      </section>
    </div>
  );
};

export default PlanejamentoLanding;
