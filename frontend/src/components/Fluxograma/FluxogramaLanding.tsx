/**
 * FluxogramaLanding - Página inicial institucional do Gerador de Fluxogramas
 *
 * Tela de enquadramento exibida antes da ferramenta de geração.
 * Segue o padrão de landing documentado em landing-pattern.md.
 */
import React from 'react';
import styles from './FluxogramaLanding.module.css';

interface FluxogramaLandingProps {
  onIniciar: () => void;
}

const HELENA_CAPABILITIES = [
  'orientar a escolha do tipo de fluxograma adequado;',
  'apoiar a interpretação do POP ou documento enviado;',
  'esclarecer conceitos de notação BPMN utilizados na geração.',
];

const USE_CASES = [
  'visualizar o fluxo de uma atividade já documentada em POP;',
  'apoiar a análise e melhoria de processos de trabalho;',
  'facilitar a comunicação institucional sobre como o trabalho é realizado;',
  'complementar documentação de governança com representação visual.',
];

const ETAPAS = [
  {
    titulo: 'Enviar o documento',
    descricao: 'Faça upload do PDF do Procedimento Operacional Padrão ou documento equivalente.',
  },
  {
    titulo: 'Conversar com a Helena',
    descricao: 'Helena fará perguntas complementares para compreender o fluxo da atividade.',
  },
  {
    titulo: 'Visualizar o fluxograma',
    descricao: 'O fluxograma será gerado em notação visual (Mermaid/BPMN) a partir das informações coletadas.',
  },
  {
    titulo: 'Revisar e exportar',
    descricao: 'Revise o resultado e exporte em formato adequado para uso institucional.',
  },
];

const FluxogramaLanding: React.FC<FluxogramaLandingProps> = ({ onIniciar }) => {
  return (
    <div className={styles.container}>
      {/* Cabeçalho */}
      <header className={styles.header}>
        <h1 className={styles.title}>Gerador de Fluxogramas</h1>
      </header>

      {/* Texto institucional */}
      <section className={styles.contextCard}>
        <p>
          Transforme atividades documentadas em representações visuais estruturadas,
          facilitando a compreensão, a comunicação e a análise dos processos de trabalho.
        </p>
        <p>
          O fluxograma é gerado a partir de um Procedimento Operacional Padrão (POP)
          ou documento equivalente, utilizando notação visual padronizada.
        </p>
      </section>

      {/* Card Helena */}
      <section className={styles.helenaCard}>
        <div className={styles.helenaCardInner}>
          <div className={styles.helenaAvatar}>
            <img
              src="/helena_fluxograma.png"
              alt="Helena - Apoio à geração de fluxogramas"
            />
          </div>
          <div className={styles.helenaContent}>
            <h2 className={styles.helenaTitle}>Helena — Apoio à geração de fluxogramas</h2>
            <p className={styles.helenaText}>
              Helena auxilia na interpretação do documento enviado e na construção
              do fluxograma correspondente. Ela pode fazer perguntas complementares
              para garantir que o diagrama reflita com fidelidade o processo descrito.
            </p>
            <p className={styles.helenaLabel}>Durante o processo, a Helena pode:</p>
            <ul className={styles.helenaList}>
              {HELENA_CAPABILITIES.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
            <p className={styles.helenaDisclaimer}>
              O fluxograma gerado é uma representação visual baseada nas informações
              fornecidas. A validação do conteúdo permanece sob responsabilidade
              do usuário e das instâncias institucionais competentes.
            </p>
          </div>
        </div>
      </section>

      {/* Como funciona */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Como funciona</h2>
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

      {/* Quando utilizar */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Quando utilizar</h2>
        <p className={styles.sectionIntro}>
          Utilize o gerador de fluxogramas para:
        </p>
        <ul className={styles.bulletList}>
          {USE_CASES.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
        <p className={styles.sectionNote}>
          É recomendável ter um POP ou documento descritivo da atividade antes de iniciar.
        </p>
      </section>

      {/* Bloco de decisão */}
      <section className={styles.decisionBlock}>
        <h2 className={styles.sectionTitle}>Quando faz sentido iniciar agora</h2>
        <p className={styles.decisionText}>
          É indicado gerar um fluxograma quando houver uma atividade documentada
          que precise de representação visual — seja para análise, comunicação
          ou complementação da documentação institucional.
        </p>
      </section>

      {/* CTA */}
      <section className={styles.ctaSection}>
        <p className={styles.ctaText}>
          Inicie a geração do fluxograma quando tiver o documento
          da atividade pronto para envio.
        </p>
        <button
          type="button"
          className={styles.ctaButton}
          onClick={onIniciar}
        >
          Iniciar geração de fluxograma
        </button>
      </section>
    </div>
  );
};

export default FluxogramaLanding;
