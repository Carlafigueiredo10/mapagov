// Sobre/index.tsx - Página institucional do MapaGov
import Layout from '../../components/Layout/Layout';
import styles from './Sobre.module.css';

export default function Sobre() {
  return (
    <Layout>
      <div className={styles.sobreContainer}>
        {/* Hero */}
        <section className={styles.hero}>
          <div className={styles.container}>
            <h1 className={styles.title}>Conheça o MapaGov</h1>
            <p className={styles.subtitle}>
              Transformando a Governança Pública com Inteligência Artificial
            </p>
          </div>
        </section>

        {/* Introdução */}
        <section className={styles.section}>
          <div className={styles.container}>
            <p className={styles.intro}>
              O MapaGov é uma plataforma inovadora desenvolvida pela{' '}
              <strong>Diretoria de Serviços de Aposentados, Pensionistas e Órgãos Extintos (DECIPEX)</strong>,
              vinculada ao Ministério da Gestão e da Inovação em Serviços Públicos (MGI). Sua missão é
              fortalecer a governança, a gestão de riscos e a conformidade na Administração Pública Federal,
              tornando a gestão mais acessível, inteligente e eficiente por meio do uso ético e responsável da
              Inteligência Artificial.
            </p>
          </div>
        </section>

        {/* Desafio */}
        <section className={`${styles.section} ${styles.bgLight}`}>
          <div className={styles.container}>
            <h2 className={styles.sectionTitle}>O Desafio que Enfrentamos</h2>
            <p className={styles.text}>
              Servidores públicos lidam diariamente com a complexidade de documentar processos, garantir
              conformidade normativa e identificar riscos de forma preventiva. O MapaGov surgiu para enfrentar
              esse desafio, oferecendo soluções que simplificam e integram a governança, sem abrir mão da
              transparência, segurança e rastreabilidade exigidas na gestão pública.
            </p>
          </div>
        </section>

        {/* Helena */}
        <section className={styles.section}>
          <div className={styles.container}>
            <h2 className={styles.sectionTitle}>Helena: Inteligência a Serviço da Governança</h2>
            <p className={styles.text}>
              No centro do MapaGov está <strong>Helena</strong>, o módulo de inteligência artificial conversacional
              da plataforma. Desenvolvida para compreender o contexto e o linguajar da administração pública, Helena
              apoia o servidor na produção e qualificação de informações institucionais.
            </p>

            {/* Layout 2 colunas: Helena + Features */}
            <div className={styles.helenaGrid}>
              <div className={styles.helenaImageContainer}>
                <img
                  src="/helena_sobre.png"
                  alt="Helena - IA Assistente"
                  className={styles.helenaImage}
                />
              </div>

              <div className={styles.featuresList}>
                <h3>Com base em modelos de IA ética e supervisionada, Helena:</h3>
                <ul>
                  <li>Extrai informações estruturadas de conversas e documentos</li>
                  <li>Preenche automaticamente formulários e modelos oficiais</li>
                  <li>Sugere melhorias baseadas em boas práticas e normativos</li>
                  <li>Identifica riscos e pontos de atenção</li>
                  <li>Valida conformidade com legislações e manuais aplicáveis</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Catálogo */}
        <section className={`${styles.section} ${styles.bgLight}`}>
          <div className={styles.container}>
            <h2 className={styles.sectionTitle}>Catálogo de Soluções</h2>

            <div className={styles.catalogGrid}>
              <div className={styles.catalogCard}>
                <div className={styles.catalogBadge}>✅ Disponíveis Agora</div>
                <ul>
                  <li><strong>Gerador de POP:</strong> Estrutura processos e gera o Procedimento Operacional Padrão auditável.</li>
                  <li><strong>Gerador de Fluxograma:</strong> Representa visualmente o fluxo do processo mapeado.</li>
                  <li><strong>Análise de Riscos:</strong> Identifica, avalia e propõe tratamento de riscos conforme diretrizes institucionais.</li>
                  <li><strong>Planejamento Estratégico:</strong> Organiza objetivos, metas e ferramentas conforme orientações do MGI.</li>
                </ul>
              </div>

              <div className={styles.catalogCard}>
                <div className={`${styles.catalogBadge} ${styles.development}`}>🔵 Em Desenvolvimento</div>
                <ul>
                  <li><strong>Plano de Ação e Acompanhamento:</strong> Define ações, responsáveis e prazos para execução e monitoramento.</li>
                  <li><strong>Painel Executivo:</strong> Apresenta indicadores e visão consolidada das iniciativas.</li>
                  <li><strong>Dossiê Consolidado de Governança:</strong> Reúne todos os documentos e análises produzidos sobre o objeto.</li>
                  <li><strong>Relatório Técnico Consolidado:</strong> Formaliza o histórico completo do processo para arquivamento.</li>
                  <li><strong>Relatório de Conformidade:</strong> Avalia se o processo executado seguiu etapas e prazos previstos.</li>
                  <li><strong>Revisão e Adequação de Documentos:</strong> Ajusta documentos à linguagem simples e aos padrões institucionais.</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Por que escolher */}
        <section className={styles.section}>
          <div className={styles.container}>
            <h2 className={styles.sectionTitle}>Por que escolher o MapaGov</h2>

            <div className={styles.benefitsGrid}>
              <div className={styles.benefitCard}>
                <span className={styles.benefitIcon}>🎯</span>
                <h3>Desenvolvido por e para o Setor Público</h3>
                <p>Concebido pela DECIPEX/MGI com base em referenciais como COSO ERM, ISO 31000, Modelo das Três Linhas (IIA) e Referencial Básico de Governança Organizacional do TCU.</p>
              </div>

              <div className={styles.benefitCard}>
                <span className={styles.benefitIcon}>⚡</span>
                <h3>Agilidade com Confiabilidade</h3>
                <p>Reduz o tempo de documentação e análise mantendo o rigor técnico e a aderência às normas vigentes.</p>
              </div>

              <div className={styles.benefitCard}>
                <span className={styles.benefitIcon}>🔒</span>
                <h3>Segurança e Privacidade</h3>
                <p>Totalmente alinhado à Lei Geral de Proteção de Dados (Lei nº 13.709/2018) e às diretrizes de segurança da informação do governo federal.</p>
              </div>

              <div className={styles.benefitCard}>
                <span className={styles.benefitIcon}>🤝</span>
                <h3>Interface Intuitiva e Acessível</h3>
                <p>Design moderno e responsivo, compatível com o padrão gov.br, pensado para todos os níveis de usuários.</p>
              </div>

              <div className={styles.benefitCard}>
                <span className={styles.benefitIcon}>📊</span>
                <h3>Inteligência Contextualizada</h3>
                <p>A IA reconhece o contexto de cada órgão, sugerindo automaticamente bases legais, controles internos e boas práticas de governança e integridade.</p>
              </div>
            </div>
          </div>
        </section>

        {/* Tecnologia */}
        <section className={`${styles.section} ${styles.bgLight}`}>
          <div className={styles.container}>
            <h2 className={styles.sectionTitle}>Tecnologia e Arquitetura</h2>
            <p className={styles.text}>O MapaGov combina tecnologias abertas, seguras e escaláveis:</p>

            <div className={styles.techGrid}>
              <div className={styles.techCard}>
                <h4>IA Avançada</h4>
                <p>Modelos baseados em GPT-4 com RAG (Retrieval-Augmented Generation) para respostas precisas e contextualizadas</p>
              </div>
              <div className={styles.techCard}>
                <h4>Interface Moderna</h4>
                <p>Construída em React 19 + TypeScript para experiência fluida e responsiva</p>
              </div>
              <div className={styles.techCard}>
                <h4>Backend Robusto</h4>
                <p>Desenvolvido em Django + PostgreSQL, assegurando estabilidade e integridade dos dados</p>
              </div>
              <div className={styles.techCard}>
                <h4>Cloud Native</h4>
                <p>Preparado para implantação em infraestrutura de nuvem pública ou governamental</p>
              </div>
            </div>
          </div>
        </section>

        {/* Impacto */}
        <section className={styles.section}>
          <div className={styles.container}>
            <h2 className={styles.sectionTitle}>Impacto Esperado</h2>
            <p className={styles.text}>Com o MapaGov, os órgãos públicos poderão:</p>

            <ul className={styles.impactList}>
              <li>Padronizar e automatizar fluxos de trabalho</li>
              <li>Integrar dados e gerar indicadores em tempo real</li>
              <li>Reduzir retrabalho e tempo de tramitação</li>
              <li>Fortalecer a cultura de integridade e prevenção de riscos</li>
              <li>Elevar o nível de maturidade em governança institucional</li>
            </ul>
          </div>
        </section>

        {/* Alinhamento */}
        <section className={`${styles.section} ${styles.bgLight}`}>
          <div className={styles.container}>
            <h2 className={styles.sectionTitle}>Alinhamento Técnico e Institucional</h2>
            <p className={styles.text}>O MapaGov está fundamentado nos principais referenciais nacionais e internacionais:</p>

            <ul className={styles.referencesList}>
              <li>COSO ERM – Enterprise Risk Management (2017)</li>
              <li>ISO 31000 – Risk Management (2018)</li>
              <li>Referencial Básico de Governança Organizacional – TCU (2020)</li>
              <li>Guia de Gestão de Riscos – CGU (2022)</li>
              <li>Modelo de Maturidade em Integridade Pública – MMIP/CGU (2023)</li>
            </ul>

            <p className={styles.text}>
              Esses referenciais orientam toda a arquitetura da plataforma, garantindo aderência normativa, transparência e valor público.
            </p>
          </div>
        </section>

        {/* CTA Final */}
        <section className={styles.ctaSection}>
          <div className={styles.container}>
            <h2 className={styles.ctaTitle}>Junte-se à Transformação da Governança Pública</h2>
            <p className={styles.ctaText}>
              O MapaGov, desenvolvido pela DECIPEX/MGI, é mais que uma ferramenta digital — é um ecossistema de inovação institucional voltado à melhoria contínua da gestão pública. Seu propósito é apoiar servidores e gestores na tomada de decisão baseada em evidências, no fortalecimento da integridade e na entrega de valor público sustentável.
            </p>
            <p className={styles.ctaHighlight}>
              👉 Conheça o MapaGov e descubra como a tecnologia pode fortalecer a governança do seu órgão — com ética, inteligência e propósito público.
            </p>

            <div className={styles.ctaFooter}>
              <strong>MapaGov – Governança Inteligente para o Setor Público</strong>
              <p>Desenvolvido pela DECIPEX/MGI</p>
              <p>Transformando processos. Elevando resultados. Fortalecendo instituições.</p>
            </div>
          </div>
        </section>
      </div>
    </Layout>
  );
}
