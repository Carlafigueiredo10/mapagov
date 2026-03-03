// Landing/index.tsx - Página principal do MapaGov (migrada de HTML)
import { useState } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../components/Layout/Layout';
import HelenaPublicDrawer from '../../components/Helena/HelenaPublicDrawer';
import { useAuthStore } from '../../store/authStore';
import { hasRole } from '../../services/authApi';
import styles from './Landing.module.css';

export default function Landing() {
  const [drawerAberto, setDrawerAberto] = useState(false);
  const user = useAuthStore((s) => s.user);
  const isAdmin = hasRole(user, 'admin') || !!user?.is_superuser;

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

              <div className={styles.heroButtons}>
                <Link to="/login" className={styles.btn}>
                  Login
                </Link>
                <Link to="/pop" className={`${styles.btn} ${styles.btnOutline}`}>
                  Começar Mapeamento
                </Link>
                <a href="#produtos" className={`${styles.btn} ${styles.btnOutline}`}>
                  Ver Demais Produtos
                </a>
              </div>
              {isAdmin && (
                <div style={{ marginTop: '0.5rem' }}>
                  <Link to="/admin" className={styles.btn} style={{ background: '#1B4F72' }}>
                    Painel do Administrador
                  </Link>
                </div>
              )}

              <div className={styles.heroStats}>
                <div className={styles.statItem}>
                  <span className={styles.statTitle}>Conformidade com padrões Gov.br</span>
                  <span className={styles.statDesc}>Interface alinhada ao Design System oficial.</span>
                </div>
                <div className={styles.statItem}>
                  <span className={styles.statTitle}>Produtos estruturados de governança</span>
                  <span className={styles.statDesc}>Mapeamento, riscos e planejamento integrados.</span>
                </div>
                <div className={styles.statItem}>
                  <span className={styles.statTitle}>Assistente virtual de apoio</span>
                  <span className={styles.statDesc}>Orientação guiada para uso da plataforma.</span>
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
                  <img src="/helena_em_pe.png" alt="Helena — Assistente da Plataforma MapaGov" />
                </div>
                <h4 className={styles.helenaTitle}>Helena — Assistente da Plataforma MapaGov</h4>
                <p className={styles.helenaDesc}>
                  Assistente virtual para orientação sobre o funcionamento da plataforma e seus produtos de governança.
                </p>
                <div className={styles.helenaCards}>
                  <div className={styles.helenaCard}>Apoio conceitual em processos, riscos e controles</div>
                  <div className={styles.helenaCard}>Orientação alinhada a boas práticas de governança pública</div>
                  <div className={styles.helenaCard}>Construção progressiva do mapeamento, passo a passo</div>
                </div>
                <span className={styles.helenaLink}>
                  Ver orientações disponíveis
                </span>
                <p className={styles.helenaDisclaimer}>
                  As informações fornecidas têm caráter orientativo e não substituem normativos ou decisões administrativas do órgão.
                </p>
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

          {/* ── Produtos disponíveis ── */}
          <h3 className={styles.productsBlockTitle}>Disponíveis para uso</h3>

          <div className={styles.productsGrid}>
            <Link to="/pop" className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Gerador de POP</h3>
                <span className={styles.tagDisponivel}>Disponível</span>
              </div>
              <p className={styles.productEntrega}>Documento completo do Procedimento Operacional Padrão (PDF).</p>
              <span className={styles.productBtnAcessar}>Acessar produto</span>
            </Link>

            <Link to="/riscos" className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Análise de Riscos</h3>
                <span className={styles.tagDisponivel}>Disponível</span>
              </div>
              <p className={styles.productEntrega}>Relatório de Riscos com estratégias de mitigação.</p>
              <span className={styles.productBtnAcessar}>Acessar produto</span>
            </Link>

            <Link to="/fluxograma" className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Gerador de Fluxograma</h3>
                <span className={styles.tagDesenvolvimento}>Em homologação</span>
              </div>
              <p className={styles.productEntrega}>Fluxograma visual do processo (imagem ou PDF).</p>
              <span className={styles.productBtnAcessar}>Acessar produto</span>
            </Link>

            <Link to="/planejamento-estrategico" className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Planejamento Estratégico</h3>
                <span className={styles.tagDesenvolvimento}>Em homologação</span>
              </div>
              <p className={styles.productEntrega}>Plano estratégico estruturado em documento formal.</p>
              <span className={styles.productBtnAcessar}>Acessar produto</span>
            </Link>

            <Link to="/painel" className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Painel Executivo</h3>
                <span className={styles.tagHomologacao}>Em desenvolvimento</span>
              </div>
              <p className={styles.productEntrega}>Painel consolidado com indicadores e status das iniciativas.</p>
              <span className={styles.productBtnAcessar}>Acessar produto</span>
            </Link>
          </div>

          {/* ── Previstos ── */}
          <h3 className={styles.productsBlockTitle}>Previstos</h3>
          <div className={styles.productsGridPlanejado}>
            <div className={styles.productCardPlanejado}>
              <div className={styles.productHeader}>
                <h3 className={styles.productNamePlanejado}>Plano de Ação e Acompanhamento</h3>
                <span className={styles.tagPlanejado}>Previsto</span>
              </div>
              <p className={styles.productEntregaPlanejado}>Plano de ação com responsáveis, prazos e status de execução.</p>
              <Link to="/funcionalidades" className={styles.productLinkSaberMais}>Saber mais →</Link>
            </div>

            <div className={styles.productCardPlanejado}>
              <div className={styles.productHeader}>
                <h3 className={styles.productNamePlanejado}>Dossiê Consolidado de Governança</h3>
                <span className={styles.tagPlanejado}>Previsto</span>
              </div>
              <p className={styles.productEntregaPlanejado}>Dossiê completo reunindo todos os documentos e análises gerados.</p>
              <Link to="/funcionalidades" className={styles.productLinkSaberMais}>Saber mais →</Link>
            </div>

            <div className={styles.productCardPlanejado}>
              <div className={styles.productHeader}>
                <h3 className={styles.productNamePlanejado}>Relatório Técnico Consolidado</h3>
                <span className={styles.tagPlanejado}>Previsto</span>
              </div>
              <p className={styles.productEntregaPlanejado}>Relatório técnico com histórico completo do processo.</p>
              <Link to="/funcionalidades" className={styles.productLinkSaberMais}>Saber mais →</Link>
            </div>

            <div className={styles.productCardPlanejado}>
              <div className={styles.productHeader}>
                <h3 className={styles.productNamePlanejado}>Relatório de Conformidade</h3>
                <span className={styles.tagPlanejado}>Previsto</span>
              </div>
              <p className={styles.productEntregaPlanejado}>Verificação de aderência ao POP e prazos definidos.</p>
              <Link to="/funcionalidades" className={styles.productLinkSaberMais}>Saber mais →</Link>
            </div>

            <div className={styles.productCardPlanejado}>
              <div className={styles.productHeader}>
                <h3 className={styles.productNamePlanejado}>Revisão e Adequação de Documentos</h3>
                <span className={styles.tagPlanejado}>Previsto</span>
              </div>
              <p className={styles.productEntregaPlanejado}>Documento revisado conforme linguagem simples e padrões institucionais.</p>
              <Link to="/funcionalidades" className={styles.productLinkSaberMais}>Saber mais →</Link>
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
              <Link to="/registrar" className={`${styles.btn} ${styles.btnOutline}`}>
                Solicitar acesso
              </Link>
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
                  <span>Análise de Riscos</span>
                </li>
                <li className={styles.productHomologacao}>
                  <span className={styles.productIcon}>🟠</span>
                  <span>Gerador de Fluxograma</span>
                </li>
                <li className={styles.productHomologacao}>
                  <span className={styles.productIcon}>🟠</span>
                  <span>Planejamento Estratégico</span>
                </li>
              </ul>
            </div>

            {/* Fase 2 — Execução e Qualificação */}
            <div className={styles.roadmapPhase}>
              <div className={styles.phaseBadge}><span>Fase 2</span><br />Execução e Qualificação</div>
              <p className={styles.phaseTimeline}>2º trimestre de 2026</p>
              <ul className={styles.productList}>
                <li className={styles.productInProgress}>
                  <span className={styles.productIcon}>🟡</span>
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
