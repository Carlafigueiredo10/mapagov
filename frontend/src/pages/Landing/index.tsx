// Landing/index.tsx - Página principal do MapaGov (migrada de HTML)
import { useState } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../components/Layout/Layout';
import HelenaPublicDrawer from '../../components/Helena/HelenaPublicDrawer';
import styles from './Landing.module.css';

const AUTH_MODE = import.meta.env.VITE_PUBLIC_MVP_MODE !== '1';

export default function Landing() {
  const [drawerAberto, setDrawerAberto] = useState(false);

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
                <strong>Estruture mapeamentos, controles e decisões de forma organizada.</strong>
                {' '}Planejamento estratégico, análise de riscos e revisão de artefatos em um único
                sistema, com método e ferramentas integradas.
              </p>

              {AUTH_MODE ? (
                <div className={styles.heroButtons}>
                  <Link to="/login" className={styles.btn}>
                    Entrar no Sistema
                  </Link>
                  <Link to="/sobre" className={`${styles.btn} ${styles.btnOutline}`}>
                    Conhecer a Plataforma
                  </Link>
                </div>
              ) : (
                <div className={styles.heroButtons}>
                  <Link to="/pop" className={styles.btn}>
                    Começar Mapeamento
                  </Link>
                  <Link to="/riscos" className={`${styles.btn} ${styles.btnOutline}`}>
                    Análise de Riscos
                  </Link>
                </div>
              )}

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
              <div
                className={styles.helenaCompact}
                onClick={() => setDrawerAberto(true)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => { if (e.key === 'Enter') setDrawerAberto(true); }}
              >
                <div className={styles.helenaAvatarSmall}>
                  <img src="/helena_em_pe.png" alt="Helena — Assistente de Governança" />
                </div>
                <h4 className={styles.helenaTitle}>Helena — Assistente de Governança</h4>
                <p className={styles.helenaDesc}>
                  Assistente especializada em mapeamento de processos, riscos e conformidade no setor público.
                </p>
                <div className={styles.helenaCards}>
                  <div className={styles.helenaCard}>Apoio conceitual em processos, riscos e controles</div>
                  <div className={styles.helenaCard}>Orientação alinhada a boas práticas de governança pública</div>
                  <div className={styles.helenaCard}>Construção progressiva do mapeamento, passo a passo</div>
                </div>
                <span className={styles.helenaLink}>
                  Falar com a Helena
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* PRODUTOS */}
      <section id="produtos" className={styles.features}>
        <div className={styles.container}>
          <h2 className={styles.sectionTitle}>Conheça nossos produtos</h2>
          <p className={styles.sectionSubtitle}>
            Soluções integradas para estruturar, executar, monitorar e consolidar a governança do seu órgão.
          </p>

          <div className={styles.productsGrid}>
            {/* 1 — Pronto */}
            <div className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Gerador de POP</h3>
                <Link to="/pop" className={styles.tagDisponivel}>Pronto</Link>
              </div>
              <p className={styles.productEntrega}>Entrega: Documento completo do Procedimento Operacional Padrão (PDF).</p>
              <p className={styles.productDescricao}>Estrutura etapas, responsabilidades e regras do processo, pronto para formalização e uso institucional.</p>
              <Link to="/funcionalidades" className={styles.productLink}>Ver funcionalidades →</Link>
            </div>

            {/* 2 — Pronto */}
            <div className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Gerador de Fluxograma</h3>
                <Link to="/fluxograma" className={styles.tagDisponivel}>Pronto</Link>
              </div>
              <p className={styles.productEntrega}>Entrega: Fluxograma visual do processo (imagem ou PDF).</p>
              <p className={styles.productDescricao}>Representação gráfica clara das etapas e decisões para organização e apresentação interna.</p>
              <Link to="/funcionalidades" className={styles.productLink}>Ver funcionalidades →</Link>
            </div>

            {/* 3 — Pronto */}
            <div className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Análise de Riscos</h3>
                <Link to="/riscos" className={styles.tagDisponivel}>Pronto</Link>
              </div>
              <p className={styles.productEntrega}>Entrega: Relatório de Riscos com estratégias de mitigação.</p>
              <p className={styles.productDescricao}>Documento estruturado com identificação, avaliação e propostas de tratamento para anexar ao projeto.</p>
              <Link to="/funcionalidades" className={styles.productLink}>Ver funcionalidades →</Link>
            </div>

            {/* 4 — Pronto */}
            <div className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Planejamento Estratégico</h3>
                <Link to="/planejamento-estrategico" className={styles.tagDisponivel}>Pronto</Link>
              </div>
              <p className={styles.productEntrega}>Entrega: Plano estratégico estruturado em documento formal.</p>
              <p className={styles.productDescricao}>Organiza objetivos, metas e diretrizes conforme orientações do MGI.</p>
              <Link to="/funcionalidades" className={styles.productLink}>Ver funcionalidades →</Link>
            </div>

            {/* 5 — Em desenvolvimento */}
            <div className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Plano de Ação e Acompanhamento</h3>
                <span className={styles.tagPlanejado}>Em desenvolvimento</span>
              </div>
              <p className={styles.productEntrega}>Entrega: Plano de ação com responsáveis, prazos e status de execução.</p>
              <p className={styles.productDescricao}>Organiza a implementação de projetos e iniciativas com acompanhamento estruturado.</p>
              <Link to="/funcionalidades" className={styles.productLink}>Ver funcionalidades →</Link>
            </div>

            {/* 6 — Em desenvolvimento */}
            <div className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Painel Executivo</h3>
                <span className={styles.tagPlanejado}>Em desenvolvimento</span>
              </div>
              <p className={styles.productEntrega}>Entrega: Painel consolidado com indicadores e status das iniciativas.</p>
              <p className={styles.productDescricao}>Apresenta visão gerencial das ações, riscos e resultados produzidos na plataforma.</p>
              <Link to="/funcionalidades" className={styles.productLink}>Ver funcionalidades →</Link>
            </div>

            {/* 7 — Em desenvolvimento */}
            <div className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Dossiê Consolidado de Governança</h3>
                <span className={styles.tagPlanejado}>Em desenvolvimento</span>
              </div>
              <p className={styles.productEntrega}>Entrega: Dossiê completo reunindo todos os documentos e análises gerados.</p>
              <p className={styles.productDescricao}>Compilação estruturada para registro institucional e prestação de contas.</p>
              <Link to="/funcionalidades" className={styles.productLink}>Ver funcionalidades →</Link>
            </div>

            {/* 8 — Em desenvolvimento */}
            <div className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Relatório Técnico Consolidado</h3>
                <span className={styles.tagPlanejado}>Em desenvolvimento</span>
              </div>
              <p className={styles.productEntrega}>Entrega: Relatório técnico com histórico completo do processo.</p>
              <p className={styles.productDescricao}>Formaliza as etapas realizadas para arquivamento e documentação administrativa.</p>
              <Link to="/funcionalidades" className={styles.productLink}>Ver funcionalidades →</Link>
            </div>

            {/* 9 — Em desenvolvimento */}
            <div className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Relatório de Conformidade</h3>
                <span className={styles.tagPlanejado}>Em desenvolvimento</span>
              </div>
              <p className={styles.productEntrega}>Entrega: Relatório de verificação de aderência ao POP e prazos definidos.</p>
              <p className={styles.productDescricao}>Avalia a execução do processo conforme regras estabelecidas.</p>
              <Link to="/funcionalidades" className={styles.productLink}>Ver funcionalidades →</Link>
            </div>

            {/* 10 — Em desenvolvimento */}
            <div className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Revisão e Adequação de Documentos</h3>
                <span className={styles.tagPlanejado}>Em desenvolvimento</span>
              </div>
              <p className={styles.productEntrega}>Entrega: Documento revisado conforme linguagem simples e padrões institucionais.</p>
              <p className={styles.productDescricao}>Ajusta textos para adequação normativa e maior clareza administrativa.</p>
              <Link to="/funcionalidades" className={styles.productLink}>Ver funcionalidades →</Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section id="cta" className={styles.cta}>
        <div className={styles.container}>
          <div className={styles.ctaContent}>
            <h2 className={styles.sectionTitle}>Estruture a governança do seu órgão</h2>
            <p className={styles.sectionSubtitle}>
              Organize processos, riscos e controles com método, ferramentas integradas e suporte ao planejamento institucional, alinhados aos padrões da Administração Pública Federal.
            </p>

            <div className={styles.ctaButtons}>
              <Link to="/sobre" className={styles.btn}>
                Conheça o projeto
              </Link>
              {AUTH_MODE ? (
                <Link to="/registrar" className={`${styles.btn} ${styles.btnOutline}`}>
                  Solicitar acesso
                </Link>
              ) : (
                <Link to="/portal" className={`${styles.btn} ${styles.btnOutline}`}>
                  Acessar o portal
                </Link>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* ROADMAP */}
      <section id="roadmap" className={styles.roadmap}>
        <div className={styles.container}>
          <h2 className={styles.sectionTitle}>Roteiro de Desenvolvimento</h2>
          <p className={styles.sectionSubtitle}>
            Acompanhe as próximas entregas e a evolução da plataforma.
          </p>

          <div className={styles.roadmapGrid}>
            {/* Fase 1 — Estruturação */}
            <div className={styles.roadmapPhase}>
              <div className={styles.phaseBadge}><span>Fase 1</span><br />Entrega Inicial</div>
              <p className={styles.phaseTimeline}>1º trimestre de 2026</p>
              <ul className={styles.productList}>
                <li className={styles.productCompleted}>
                  <span className={styles.productIcon}>✅</span>
                  <span>Gerador de POP</span>
                </li>
                <li className={styles.productCompleted}>
                  <span className={styles.productIcon}>✅</span>
                  <span>Gerador de Fluxograma</span>
                </li>
                <li className={styles.productCompleted}>
                  <span className={styles.productIcon}>✅</span>
                  <span>Análise de Riscos</span>
                </li>
                <li className={styles.productCompleted}>
                  <span className={styles.productIcon}>✅</span>
                  <span>Planejamento Estratégico</span>
                </li>
              </ul>
            </div>

            {/* Fase 2 — Execução e Qualificação */}
            <div className={styles.roadmapPhase}>
              <div className={styles.phaseBadge}><span>Fase 2</span><br />Execução e Qualificação</div>
              <p className={styles.phaseTimeline}>2º trimestre de 2026</p>
              <ul className={styles.productList}>
                <li>
                  <span className={styles.productIcon}>📅</span>
                  <span>Painel Executivo</span>
                </li>
                <li>
                  <span className={styles.productIcon}>📅</span>
                  <span>Revisão e Adequação de Documentos</span>
                </li>
              </ul>
            </div>

            {/* Fase 3 — Governança e Monitoramento */}
            <div className={styles.roadmapPhase}>
              <div className={styles.phaseBadge}><span>Fase 3</span><br />Governança e Monitoramento</div>
              <p className={styles.phaseTimeline}>3º trimestre de 2026</p>
              <ul className={styles.productList}>
                <li>
                  <span className={styles.productIcon}>📅</span>
                  <span>Plano de Ação e Acompanhamento</span>
                </li>
                <li>
                  <span className={styles.productIcon}>📅</span>
                  <span>Dossiê Consolidado de Governança</span>
                </li>
              </ul>
            </div>

            {/* Fase 4 — Consolidação e Conformidade */}
            <div className={styles.roadmapPhase}>
              <div className={styles.phaseBadge}><span>Fase 4</span><br />Consolidação e Conformidade</div>
              <p className={styles.phaseTimeline}>4º trimestre de 2026</p>
              <ul className={styles.productList}>
                <li>
                  <span className={styles.productIcon}>📅</span>
                  <span>Relatório Técnico Consolidado</span>
                </li>
                <li>
                  <span className={styles.productIcon}>📅</span>
                  <span>Relatório de Conformidade</span>
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
      <HelenaPublicDrawer open={drawerAberto} onClose={() => setDrawerAberto(false)} />
    </Layout>
  );
}
