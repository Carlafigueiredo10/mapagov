// Sobre/index.tsx - Página institucional do MapaGov
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import Layout from '../../components/Layout/Layout';
import styles from './Sobre.module.css';

export default function Sobre() {
  const { hash } = useLocation();

  useEffect(() => {
    if (hash) {
      const el = document.getElementById(hash.slice(1));
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }
  }, [hash]);

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
        <section id="helena" className={styles.section}>
          <div className={styles.container}>
            <h2 className={styles.sectionTitle}>Helena — Assistente da Plataforma MapaGov</h2>
            <p className={styles.sectionSubtitle}>Inteligência artificial a serviço da governança pública</p>
            <p className={styles.text}>
              No centro do MapaGov está <strong>Helena</strong>, módulo de inteligência artificial conversacional
              desenvolvido para apoiar atividades administrativas no âmbito da governança, riscos e conformidade.
            </p>
            <p className={styles.text}>
              Projetada para compreender o contexto e a linguagem da administração pública, Helena auxilia na
              organização, estruturação e qualificação de informações institucionais, contribuindo para maior
              eficiência, padronização e segurança nos processos.
            </p>
            <p className={styles.text}>
              Sua atuação ocorre sempre como ferramenta de apoio, sob supervisão do usuário responsável.
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
                <h3>Capacidades da Helena</h3>
                <ul>
                  <li>Extrair informações estruturadas a partir de conversas e documentos institucionais</li>
                  <li>Apoiar o preenchimento de formulários e modelos oficiais</li>
                  <li>Sugerir melhorias com base em boas práticas e referenciais normativos</li>
                  <li>Indicar potenciais riscos e pontos de atenção em processos administrativos</li>
                  <li>Apoiar a verificação de aderência a normativos e manuais aplicáveis</li>
                </ul>
              </div>
            </div>

            <div className={styles.helenaDisclaimer}>
              <h4>Uso Responsável</h4>
              <p>
                As recomendações e análises geradas pela Helena possuem caráter auxiliar e não substituem
                a avaliação técnica, administrativa ou jurídica do usuário responsável. A decisão final sobre
                conteúdos, encaminhamentos e conformidade permanece sob responsabilidade do agente público competente.
              </p>
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

        {/* Diferenciais */}
        <section className={styles.section}>
          <div className={styles.container}>
            <h2 className={styles.sectionTitle}>Diferenciais institucionais</h2>

            <div className={styles.benefitsGrid}>
              <div className={styles.benefitCard}>
                <span className={styles.benefitIcon}>🏛</span>
                <h3>Desenvolvido para o setor público</h3>
                <p>Concebido no âmbito do DECIPEx/MGI, com base em referenciais do COSO ERM, ISO 31000 e boas práticas de governança organizacional.</p>
              </div>

              <div className={styles.benefitCard}>
                <span className={styles.benefitIcon}>⚡</span>
                <h3>Eficiência com conformidade</h3>
                <p>Estrutura processos e documentos mantendo aderência a normativos e padrões institucionais vigentes.</p>
              </div>

              <div className={styles.benefitCard}>
                <span className={styles.benefitIcon}>🔐</span>
                <h3>Segurança da informação</h3>
                <p>Tratamento de dados alinhado à Lei n.º 13.709/2018 (LGPD) e às diretrizes de segurança da Administração Pública Federal.</p>
              </div>

              <div className={styles.benefitCard}>
                <span className={styles.benefitIcon}>♿</span>
                <h3>Interface acessível</h3>
                <p>Interface responsiva e compatível com padrões de acessibilidade digital, promovendo inclusão e previsibilidade de uso.</p>
              </div>

              <div className={styles.benefitCard}>
                <span className={styles.benefitIcon}>🧠</span>
                <h3>Inteligência contextual</h3>
                <p>Apoio à tomada de decisão com base no contexto administrativo, referenciais normativos e boas práticas de governança.</p>
              </div>

              <div className={styles.benefitCard}>
                <span className={styles.benefitIcon}>🔄</span>
                <h3>Evolução e sustentabilidade institucional</h3>
                <p>Plataforma estruturada para atualização contínua, com governança técnica e acompanhamento institucional, assegurando aderência a mudanças normativas e tecnológicas.</p>
              </div>
            </div>
          </div>
        </section>

        {/* Arquitetura */}
        <section className={`${styles.section} ${styles.bgLight}`}>
          <div className={styles.container}>
            <h2 className={styles.sectionTitle}>Arquitetura e governança digital</h2>
            <p className={styles.sectionSubtitle}>
              Plataforma tecnológica estruturante para a modernização da governança pública.
            </p>

            <div className={styles.techGrid}>
              <div className={styles.techCard}>
                <h4>Inteligência artificial assistiva</h4>
                <p>
                  Modelos de linguagem com recuperação contextual (RAG) para apoio à análise de riscos,
                  estruturação de informações e qualificação de documentos administrativos.
                </p>
              </div>

              <div className={styles.techCard}>
                <h4>Aplicação web modular</h4>
                <p>
                  Arquitetura frontend escalável, tipada e preparada para expansão contínua de funcionalidades.
                </p>
              </div>

              <div className={styles.techCard}>
                <h4>Backend e processamento estruturado</h4>
                <p>
                  API REST com banco relacional e geração automatizada de documentos institucionais.
                </p>
              </div>

              <div className={styles.techCard}>
                <h4>Segurança e rastreabilidade</h4>
                <p>
                  Autenticação auditável, registro de ações e histórico de versões,
                  assegurando responsabilidade administrativa.
                </p>
              </div>

              <div className={styles.techCard}>
                <h4>Infraestrutura escalável</h4>
                <p>
                  Execução em ambientes de nuvem pública ou governamental,
                  com monitoramento contínuo e arquitetura containerizada.
                </p>
              </div>

              <div className={styles.techCard}>
                <h4>Evolução contínua</h4>
                <p>
                  Plataforma preparada para integração normativa, interoperabilidade governamental
                  e expansão progressiva de módulos estratégicos.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Impacto */}
        <section className={styles.section}>
          <div className={styles.container}>
            <h2 className={styles.sectionTitle}>Impacto na governança pública</h2>
            <p className={styles.sectionSubtitle}>Com o MapaGov, os órgãos públicos passam a:</p>

            <ul className={styles.impactList}>
              <li><strong>Estruturar e padronizar</strong> processos de governança de forma integrada</li>
              <li><strong>Consolidar dados estratégicos</strong> para acompanhamento e tomada de decisão</li>
              <li><strong>Reduzir retrabalho</strong> e aumentar a eficiência administrativa</li>
              <li><strong>Fortalecer mecanismos</strong> de integridade e prevenção de riscos</li>
              <li><strong>Elevar o nível de maturidade</strong> institucional em governança, riscos e conformidade</li>
            </ul>
          </div>
        </section>

        {/* Referenciais */}
        <section className={`${styles.section} ${styles.bgLight}`}>
          <div className={styles.container}>
            <h2 className={styles.sectionTitle}>Referenciais normativos e técnicos</h2>
            <p className={styles.sectionSubtitle}>
              Fundamentos jurídicos, metodológicos e digitais que orientam a concepção e evolução do MapaGov.
            </p>

            <div className={styles.refGrid}>
              <div className={styles.refCategory}>
                <h3>1. Governança e gestão pública</h3>
                <ul>
                  <li>Decreto n.º 9.203/2017 — Diretrizes de governança, gestão de riscos e controles internos na Administração Pública Federal.</li>
                  <li>Instrução Normativa Conjunta MP/CGU n.º 1/2016 — Controles internos, gestão de riscos e governança no Poder Executivo Federal.</li>
                  <li>Referencial Básico de Governança Organizacional — TCU (2020) — Diretrizes para liderança, estratégia e controle.</li>
                </ul>
              </div>

              <div className={styles.refCategory}>
                <h3>2. Integridade pública</h3>
                <ul>
                  <li>Decreto n.º 11.529/2023 — Sistema de Integridade, Transparência e Acesso à Informação.</li>
                  <li>Portaria MGI n.º 6.725/2024 — Programa de Integridade do MGI.</li>
                  <li>Modelo de Maturidade em Integridade Pública — CGU (2023)</li>
                </ul>
              </div>

              <div className={styles.refCategory}>
                <h3>3a. Gestão de riscos — marco institucional (MGI)</h3>
                <ul>
                  <li>Resolução CITARC/MGI n.º 1/2023 — Política de Gestão de Riscos do MGI.</li>
                  <li>Resolução CITARC/MGI n.º 4/2024 — Aprova o Guia de Gestão de Riscos do MGI.</li>
                  <li>Resolução CITARC/MGI n.º 5/2025 — Disciplina a Carteira de Riscos Estratégicos.</li>
                  <li>Guia de Gestão de Riscos do MGI (2024) — Metodologia institucional.</li>
                </ul>
              </div>

              <div className={styles.refCategory}>
                <h3>3b. Gestão de riscos — referenciais técnicos</h3>
                <ul>
                  <li>ISO 31000 (2018) — Diretrizes internacionais de gestão de riscos.</li>
                  <li>ABNT NBR ISO 31073 (2022) — Terminologia aplicável à gestão de riscos.</li>
                  <li>ABNT NBR ISO/IEC 31010 (2012) — Técnicas de identificação e análise de riscos.</li>
                  <li>COSO ERM (2017) — Estrutura integrada de riscos, estratégia e desempenho.</li>
                  <li>Referencial Básico de Gestão de Riscos — TCU (2018)</li>
                  <li>Manual de Gestão de Riscos — TCU (2020)</li>
                  <li>Metodologia de Gestão de Riscos — CGU (2018)</li>
                </ul>
              </div>

              <div className={styles.refCategory}>
                <h3>4. Estrutura organizacional, estratégia e processos</h3>
                <ul>
                  <li>Decreto n.º 12.102/2024 — Estrutura Regimental do MGI.</li>
                  <li>Resolução CMG/MGI n.º 1/2023 — Planejamento Estratégico 2023–2027.</li>
                  <li>Resolução CMG/MGI n.º 2/2024 — Cadeia de Valor do MGI.</li>
                  <li>Guia de Modelagem de Processos — MGI (2023)</li>
                  <li>Guia Prático de Gestão de Projetos — MGI (2025)</li>
                </ul>
              </div>

              <div className={styles.refCategory}>
                <h3>5. Experiência digital e comunicação</h3>

                <ul>
                  <li>Decreto n.º 10.332/2020 — Estratégia de Governo Digital.</li>
                  <li>Decreto n.º 9.094/2017 — Simplificação do atendimento ao usuário.</li>
                  <li>Lei n.º 13.460/2017 — Direitos dos usuários de serviços públicos.</li>
                  <li>Decreto n.º 11.871/2023 — Política de Linguagem Simples.</li>
                  <li>Design System Gov.br — vigente — Padrões oficiais de interface e acessibilidade digital.</li>
                </ul>
              </div>
            </div>
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
