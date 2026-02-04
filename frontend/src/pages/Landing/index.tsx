// Landing/index.tsx - Página principal do MapaGov (migrada de HTML)
import { Link } from 'react-router-dom';
import Layout from '../../components/Layout/Layout';
import styles from './Landing.module.css';

export default function Landing() {
  return (
    <Layout>
      {/* HERO */}
      <section className={styles.hero}>
        <div className={styles.container}>
          <div className={styles.heroContent}>
            <div className={styles.heroText}>
              <h1>
                Governança, Riscos e <span className={styles.highlight}>Conformidade</span> para o
                Setor Público
              </h1>
              <p>
                <strong>Transforme mapeamentos dispersos e controles informais em processos, riscos e decisões estruturadas.</strong>
                {' '}Planejamento estratégico, análise de riscos e revisão de artefatos em um único
                sistema, com método, ferramentas e rastreabilidade.
              </p>

              <div className={styles.heroButtons}>
                <Link to="/chat" className={styles.btn}>
                  Começar Mapeamento
                </Link>
                <Link to="/riscos" className={`${styles.btn} ${styles.btnOutline}`}>
                  Análise de Riscos
                </Link>
              </div>

              <div className={styles.heroStats}>
                <div className={styles.statItem}>
                  <span className={styles.statNumber}>AI</span>
                  <span className={styles.statLabel}>Assistente Helena</span>
                </div>
                <div className={styles.statItem}>
                  <span className={styles.statNumber}>10</span>
                  <span className={styles.statLabel}>Produtos Planejados</span>
                </div>
                <div className={styles.statItem}>
                  <span className={styles.statNumber}>100%</span>
                  <span className={styles.statLabel}>Padrões Gov.br</span>
                </div>
              </div>
            </div>

            <div className={styles.heroVisual}>
              <Link to="/portal" className={styles.helenaPreviewLink}>
                <div className={styles.helenaPreview}>
                  <div className={styles.helenaAvatar}>
                    <img src="/helena_em_pe.png" alt="Helena - IA Assistente" />
                  </div>
                  <h4 className={styles.helenaTitle}>Helena - IA Assistente</h4>

                  <div className={styles.helenaChat}>
                    <div className={styles.helenaMessage}>
                      <strong>Oi, eu sou a Helena!</strong> Sou especialista em{' '}
                      <strong>mapeamento de processos e governança</strong> no setor público. Conheço
                      profundamente as normas e referenciais técnicos sobre o tema, e estou sempre me
                      atualizando para apoiar sua jornada.
                    </div>
                    <div className={styles.helenaMessage}>
                      Meu papel é te guiar dentro do <strong>MapaGov</strong>, tornando o mapeamento
                      mais simples, claro e eficiente.
                    </div>
                    <div className={styles.helenaMessage}>
                      👉 Quer saber por onde começar? É só me mandar um <strong>"oi"</strong> e
                      seguimos juntos!
                    </div>
                  </div>

                  <p className={styles.helenaNote}>Clique em qualquer lugar para acessar o portal</p>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* FUNCIONALIDADES */}
      <section id="funcionalidades" className={styles.features}>
        <div className={styles.container}>
          <h2 className={styles.sectionTitle}>Funcionalidades Implementadas</h2>
          <p className={styles.sectionSubtitle}>
            Sistema completo de mapeamento de processos com inteligência artificial integrada
          </p>

          <div className={styles.featuresGrid}>
            <Link to="/chat" className={styles.featureCard}>
              <span className={styles.featureIcon}>🗺️</span>
              <h3>Mapeamento de Processos</h3>
              <p>
                Documente processos com padrão profissional equivalente ao DECIPEX através de
                conversa natural com Helena.
              </p>
            </Link>

            <Link to="/riscos" className={styles.featureCard}>
              <span className={styles.featureIcon}>⚠️</span>
              <h3>Análise de Riscos</h3>
              <p>
                Identificação e categorização automática de riscos dos processos documentados.
              </p>
            </Link>

            <Link to="/fluxograma" className={styles.featureCard}>
              <span className={styles.featureIcon}>📊</span>
              <h3>Gerador de Fluxogramas</h3>
              <p>
                Criação automática de fluxogramas visuais em formato Mermaid a partir dos processos
                mapeados.
              </p>
            </Link>

            <Link to="/planejamento-estrategico" className={styles.featureCard}>
              <span className={styles.featureIcon}>🎯</span>
              <h3>Planejamento Estratégico</h3>
              <p>
                Desenvolvimento colaborativo de planos estratégicos com objetivos, iniciativas e indicadores.
              </p>
            </Link>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section id="cta" className={styles.cta}>
        <div className={styles.container}>
          <div className={styles.ctaContent}>
            <h2 className={styles.sectionTitle}>Transforme a Governança do seu Órgão</h2>
            <p className={styles.sectionSubtitle}>
              Junte-se aos órgãos públicos que já utilizam o MapaGov para otimizar seus processos e
              garantir conformidade total.
            </p>

            <div className={styles.ctaButtons}>
              <Link to="/sobre" className={styles.btn}>
                Conheça mais sobre o projeto
              </Link>
              <Link to="/portal" className={`${styles.btn} ${styles.btnOutline}`}>
                Como aderir
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ROADMAP */}
      <section id="roadmap" className={styles.roadmap}>
        <div className={styles.container}>
          <h2 className={styles.sectionTitle}>Roadmap de Desenvolvimento</h2>
          <p className={styles.sectionSubtitle}>
            Acompanhe os próximos lançamentos e a evolução do MapaGov
          </p>

          <div className={styles.roadmapGrid}>
            {/* Fase 1 - MVP */}
            <div className={styles.roadmapPhase}>
              <div className={styles.phaseBadge}>Fase 1 - MVP</div>
              <h3 className={styles.phaseTitle}>Produtos Essenciais</h3>
              <p className={styles.phaseTimeline}>Q1 2025</p>
              <ul className={styles.productList}>
                <li className={styles.productCompleted}>
                  <span className={styles.productIcon}>✅</span>
                  <span>Gerador de POP</span>
                </li>
                <li className={styles.productCompleted}>
                  <span className={styles.productIcon}>✅</span>
                  <span>Gerador de Fluxograma</span>
                </li>
                <li>
                  <span className={styles.productIcon}>📅</span>
                  <span>Dossiê PDF Completo</span>
                </li>
                <li>
                  <span className={styles.productIcon}>📅</span>
                  <span>Dashboard Executivo</span>
                </li>
              </ul>
            </div>

            {/* Fase 2 - Riscos & LGPD */}
            <div className={styles.roadmapPhase}>
              <div className={styles.phaseBadge}>Fase 2 - Riscos & LGPD</div>
              <h3 className={styles.phaseTitle}>Gestão de Riscos</h3>
              <p className={styles.phaseTimeline}>Q2 2025</p>
              <ul className={styles.productList}>
                <li className={styles.productCompleted}>
                  <span className={styles.productIcon}>✅</span>
                  <span>Análise de Riscos</span>
                </li>
                <li className={styles.productCompleted}>
                  <span className={styles.productIcon}>✅</span>
                  <span>Suporte ao Planejamento Estratégico</span>
                </li>
              </ul>
            </div>

            {/* Fase 3 - Governança */}
            <div className={styles.roadmapPhase}>
              <div className={styles.phaseBadge}>Fase 3 - Governança</div>
              <h3 className={styles.phaseTitle}>Governança Avançada</h3>
              <p className={styles.phaseTimeline}>Q3 2025</p>
              <ul className={styles.productList}>
                <li>
                  <span className={styles.productIcon}>📅</span>
                  <span>Dossiê de Governança 360°</span>
                </li>
                <li>
                  <span className={styles.productIcon}>📅</span>
                  <span>Relatório de Conformidade</span>
                </li>
              </ul>
            </div>

            {/* Fase 4 - Otimização */}
            <div className={styles.roadmapPhase}>
              <div className={styles.phaseBadge}>Fase 4 - Otimização</div>
              <h3 className={styles.phaseTitle}>Melhoria Contínua</h3>
              <p className={styles.phaseTimeline}>Q4 2025</p>
              <ul className={styles.productList}>
                <li>
                  <span className={styles.productIcon}>📅</span>
                  <span>Gerador de Documentos</span>
                </li>
                <li>
                  <span className={styles.productIcon}>📅</span>
                  <span>Análise de Artefatos</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* BASE LEGAL - Link para página dedicada */}
      <section id="base-legal-preview" className={styles.baseLegalPreview}>
        <div className={styles.container}>
          <h2 className={styles.sectionTitle}>Base Legal Integrada</h2>
          <p className={styles.sectionSubtitle}>
            Acesse a biblioteca completa de documentos normativos e referenciais técnicos
          </p>

          <div className={styles.legalPreviewGrid}>
            <div className={styles.legalPreviewCard}>
              <span className={styles.legalIcon}>⚖️</span>
              <h3>Leis e Decretos</h3>
              <p>Normas de cumprimento obrigatório</p>
            </div>
            <div className={styles.legalPreviewCard}>
              <span className={styles.legalIcon}>📋</span>
              <h3>Instruções Normativas</h3>
              <p>Portarias e INs da APF</p>
            </div>
            <div className={styles.legalPreviewCard}>
              <span className={styles.legalIcon}>🔍</span>
              <h3>Referenciais TCU/CGU</h3>
              <p>Diretrizes de auditoria e controle</p>
            </div>
            <div className={styles.legalPreviewCard}>
              <span className={styles.legalIcon}>🌐</span>
              <h3>Normas Internacionais</h3>
              <p>Padrões ISO e boas práticas</p>
            </div>
          </div>

          <div className={styles.baseLegalCta}>
            <Link to="/base-legal" className={styles.btn}>
              Acessar Biblioteca Completa
            </Link>
          </div>
        </div>
      </section>
    </Layout>
  );
}
