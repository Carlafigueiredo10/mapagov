/**
 * MapeamentoProcessosLanding - Página inicial institucional de Mapeamento de Atividades (POP)
 *
 * Tela de enquadramento exibida antes do chat de mapeamento.
 * A Helena não realiza avaliações automáticas nem substitui decisões administrativas.
 */
import React from 'react';
import styles from './MapeamentoProcessosLanding.module.css';
import PopHubSection from './PopHubSection';

interface MapeamentoProcessosLandingProps {
  onIniciar: () => void;
  onRetomar: (uuid: string) => void;
  onRevisar: (uuid: string) => void;
  onVerVersoes: (uuid: string) => void;
}

const HELENA_CAPABILITIES = [
  'orientar o preenchimento das informações do POP;',
  'ajudar na identificação de macroprocesso, processo, subprocesso e atividade;',
  'apoiar a criação do código do processo na arquitetura institucional (CAP);',
  'registrar sistemas utilizados e normas associadas;',
  'organizar o passo a passo da atividade conforme informado pelo usuário.',
];

const CONVERSA_ITEMS = [
  'o POP será construído progressivamente em uma barra lateral, conforme suas respostas;',
  'você poderá acompanhar a construção do documento ao longo da conversa;',
  'ao final, você terá um POP estruturado, pronto para revisão, validação e uso.',
];

const PREREQUISITOS = [
  'conheça a atividade que será mapeada;',
  'tenha clareza sobre como o trabalho é realizado no dia a dia;',
  'esteja confortável para descrever o passo a passo da atividade.',
];

const USE_CASES = [
  'documentar atividades recorrentes;',
  'apoiar a padronização do trabalho;',
  'facilitar a capacitação de novos servidores;',
  'reduzir dependência de conhecimento individual;',
  'apoiar iniciativas de governança e melhoria de processos.',
];

const MapeamentoProcessosLanding: React.FC<MapeamentoProcessosLandingProps> = ({
  onIniciar,
  onRetomar,
  onRevisar,
  onVerVersoes,
}) => {
  return (
    <div className={styles.container}>
      {/* Cabeçalho */}
      <header className={styles.header}>
        <h1 className={styles.title}>Mapeamento de Atividades</h1>
      </header>

      {/* Texto institucional */}
      <section className={styles.contextCard}>
        <p>
          Registre, organize e documente uma atividade de trabalho por meio de um
          Procedimento Operacional Padrão (POP), garantindo clareza, padronização
          e segurança institucional.
        </p>
        <p>
          Este processo apoia a gestão do conhecimento, a continuidade administrativa
          e a melhoria dos processos de trabalho.
        </p>
      </section>

      {/* Hub de gestão documental */}
      <PopHubSection
        onCriarNovo={onIniciar}
        onRetomar={onRetomar}
        onRevisar={onRevisar}
        onVerVersoes={onVerVersoes}
      />

      {/* Card Helena */}
      <section className={styles.helenaCard}>
        <div className={styles.helenaCardInner}>
          <div className={styles.helenaAvatar}>
            <img
              src="/helena_mapeamento.png"
              alt="Helena - Guia para mapeamento de atividades"
            />
          </div>
          <div className={styles.helenaContent}>
            <h2 className={styles.helenaTitle}>Helena — Guia para mapeamento de atividades</h2>
            <p className={styles.helenaText}>
              Helena é o ecossistema de apoio do MapaGov para o mapeamento de atividades e processos.
              Ela conduz uma conversa guiada, estruturada para apoiar o preenchimento do POP
              de forma clara, progressiva e orientada.
            </p>
            <p className={styles.helenaLabel}>Durante o processo, a Helena irá:</p>
            <ul className={styles.helenaList}>
              {HELENA_CAPABILITIES.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
            <p className={styles.helenaDisclaimer}>
              As informações registradas são fornecidas pelo usuário e permanecem sob
              responsabilidade da unidade e das instâncias institucionais competentes.
              A Helena não substitui análise técnica, validação formal ou decisões administrativas.
            </p>
          </div>
        </div>
      </section>

      {/* O que vai acontecer a seguir */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>O que vai acontecer a seguir</h2>
        <p className={styles.sectionIntro}>
          Ao iniciar, você participará de uma conversa guiada com a Helena.
          Enquanto você responde às perguntas:
        </p>
        <ul className={styles.bulletList}>
          {CONVERSA_ITEMS.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </section>

      {/* O que você precisa para começar */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>O que você precisa para começar</h2>
        <p className={styles.sectionIntro}>
          Antes de iniciar, é importante que você:
        </p>
        <ul className={styles.bulletList}>
          {PREREQUISITOS.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
        <p className={styles.sectionNote}>
          Não é necessário conhecer metodologias ou normas previamente.
          A orientação será feita ao longo da conversa.
        </p>
      </section>

      {/* Quando usar */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Quando usar esta funcionalidade</h2>
        <p className={styles.sectionIntro}>
          Utilize o mapeamento de atividades para:
        </p>
        <ul className={styles.bulletList}>
          {USE_CASES.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </section>

      {/* Bloco de decisão */}
      <section className={styles.decisionBlock}>
        <h2 className={styles.sectionTitle}>Quando faz sentido iniciar agora</h2>
        <p className={styles.decisionText}>
          É indicado iniciar o mapeamento quando houver uma atividade de trabalho
          conhecida que precise ser documentada — seja para padronização, capacitação
          ou registro institucional do processo.
        </p>
      </section>

      {/* CTA */}
      <section className={styles.ctaSection}>
        <p className={styles.ctaText}>
          Inicie o mapeamento quando estiver pronto para descrever sua atividade
          e construir o POP correspondente.
        </p>
        <button
          type="button"
          className={styles.ctaButton}
          onClick={onIniciar}
        >
          Iniciar mapeamento da atividade
        </button>
      </section>
    </div>
  );
};

export default MapeamentoProcessosLanding;
