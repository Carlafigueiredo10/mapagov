import { Link } from 'react-router-dom';
import Layout from '../components/Layout/Layout';
import styles from './Funcionalidades.module.css';

export default function FuncionalidadesPage() {
  return (
    <Layout>
      <section className={styles.features}>
        <div className={styles.container}>
          <h2 className={styles.sectionTitle}>Conheça nossos produtos</h2>
          <p className={styles.sectionSubtitle}>
            Soluções integradas para estruturar, executar, monitorar e consolidar a governança do seu órgão.
          </p>

          <div className={styles.productsList}>
            {/* 1 — Gerador de POP */}
            <div className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Gerador de POP</h3>
                <Link to="/pop" className={styles.tagDisponivel}>Pronto</Link>
              </div>
              <h4 className={styles.subHeading}>O que é</h4>
              <p className={styles.subText}>Ferramenta para mapear processos administrativos e gerar automaticamente o Procedimento Operacional Padrão (POP) estruturado.</p>
              <h4 className={styles.subHeading}>Quando utilizar</h4>
              <p className={styles.subText}>Quando for necessário formalizar rotinas, padronizar fluxos internos ou registrar oficialmente a forma de execução de um processo.</p>
              <h4 className={styles.subHeading}>O que o sistema gera</h4>
              <ul className={styles.subList}>
                <li>Documento completo do POP em PDF</li>
                <li>Estrutura de etapas, responsáveis e regras</li>
                <li>Registro organizado para uso institucional</li>
              </ul>
              <h4 className={styles.subHeading}>Valor institucional</h4>
              <p className={styles.valorText}>Reduz ambiguidades, padroniza execução e fortalece a segurança administrativa.</p>
            </div>

            {/* 2 — Gerador de Fluxograma */}
            <div className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Gerador de Fluxograma</h3>
                <Link to="/fluxograma" className={styles.tagDesenvolvimento}>Em homologação</Link>
              </div>
              <h4 className={styles.subHeading}>O que é</h4>
              <p className={styles.subText}>Ferramenta para representação visual estruturada de processos.</p>
              <h4 className={styles.subHeading}>Quando utilizar</h4>
              <p className={styles.subText}>Para apresentar o fluxo de decisões, etapas e responsabilidades de forma clara para equipes, gestores ou auditorias.</p>
              <h4 className={styles.subHeading}>O que o sistema gera</h4>
              <ul className={styles.subList}>
                <li>Fluxograma visual do processo (imagem ou PDF)</li>
                <li>Estrutura lógica baseada no POP ou em descrição guiada</li>
              </ul>
              <h4 className={styles.subHeading}>Valor institucional</h4>
              <p className={styles.valorText}>Facilita compreensão, reduz erros operacionais e melhora comunicação interna.</p>
            </div>

            {/* 3 — Análise de Riscos */}
            <div className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Análise de Riscos</h3>
                <Link to="/riscos" className={styles.tagDisponivel}>Pronto</Link>
              </div>
              <h4 className={styles.subHeading}>O que é</h4>
              <p className={styles.subText}>Módulo de identificação, avaliação e proposição de tratamento de riscos administrativos.</p>
              <h4 className={styles.subHeading}>Quando utilizar</h4>
              <p className={styles.subText}>Na criação ou revisão de processos, projetos e iniciativas que exijam análise estruturada de riscos.</p>
              <h4 className={styles.subHeading}>O que o sistema gera</h4>
              <ul className={styles.subList}>
                <li>Relatório de Riscos</li>
                <li>Classificação conforme critérios institucionais</li>
                <li>Estratégias de mitigação sugeridas</li>
              </ul>
              <h4 className={styles.subHeading}>Valor institucional</h4>
              <p className={styles.valorText}>Antecipação de falhas, redução de vulnerabilidades e maior robustez na tomada de decisão.</p>
            </div>

            {/* 4 — Planejamento Estratégico */}
            <div className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Planejamento Estratégico</h3>
                <Link to="/planejamento-estrategico" className={styles.tagDesenvolvimento}>Em homologação</Link>
              </div>
              <h4 className={styles.subHeading}>O que é</h4>
              <p className={styles.subText}>Ferramenta para organizar objetivos, metas e diretrizes conforme orientações do MGI.</p>
              <h4 className={styles.subHeading}>Quando utilizar</h4>
              <p className={styles.subText}>Na elaboração de planos institucionais, planejamento de áreas ou definição de prioridades estratégicas.</p>
              <h4 className={styles.subHeading}>O que o sistema gera</h4>
              <ul className={styles.subList}>
                <li>Documento estruturado de planejamento</li>
                <li>Organização de metas e diretrizes</li>
                <li>Referência metodológica alinhada ao guia prático do MGI</li>
              </ul>
              <h4 className={styles.subHeading}>Valor institucional</h4>
              <p className={styles.valorText}>Alinhamento estratégico e organização estruturada das iniciativas.</p>
            </div>

            {/* 5 — Plano de Ação e Acompanhamento */}
            <div className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Plano de Ação e Acompanhamento</h3>
                <span className={styles.tagPlanejado}>Em desenvolvimento</span>
              </div>
              <h4 className={styles.subHeading}>O que é</h4>
              <p className={styles.subText}>Módulo para organizar ações, responsáveis, prazos e monitoramento de execução.</p>
              <h4 className={styles.subHeading}>Quando utilizar</h4>
              <p className={styles.subText}>Para operacionalizar projetos, implementar decisões estratégicas ou acompanhar execução de iniciativas.</p>
              <h4 className={styles.subHeading}>O que o sistema gera</h4>
              <ul className={styles.subList}>
                <li>Plano estruturado de ações</li>
                <li>Definição de responsáveis</li>
                <li>Registro de prazos e status</li>
              </ul>
              <h4 className={styles.subHeading}>Valor institucional</h4>
              <p className={styles.valorText}>Controle prático da execução e acompanhamento sistemático das entregas.</p>
            </div>

            {/* 6 — Painel Executivo */}
            <div className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Painel Executivo</h3>
                <Link to="/painel" className={styles.tagDesenvolvimento}>Em homologação</Link>
              </div>
              <h4 className={styles.subHeading}>O que é</h4>
              <p className={styles.subText}>Interface consolidada de indicadores e status das iniciativas registradas na plataforma.</p>
              <h4 className={styles.subHeading}>Quando utilizar</h4>
              <p className={styles.subText}>Para acompanhamento gerencial e visão estratégica do conjunto de processos e projetos.</p>
              <h4 className={styles.subHeading}>O que o sistema gera</h4>
              <ul className={styles.subList}>
                <li>Painel com indicadores consolidados</li>
                <li>Visão resumida das iniciativas</li>
                <li>Acompanhamento de andamento e resultados</li>
              </ul>
              <h4 className={styles.subHeading}>Valor institucional</h4>
              <p className={styles.valorText}>Suporte à tomada de decisão e monitoramento estratégico.</p>
            </div>

            {/* 7 — Dossiê Consolidado de Governança */}
            <div className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Dossiê Consolidado de Governança</h3>
                <span className={styles.tagPlanejado}>Em desenvolvimento</span>
              </div>
              <h4 className={styles.subHeading}>O que é</h4>
              <p className={styles.subText}>Documento integrado que reúne todos os produtos e análises gerados sobre um objeto.</p>
              <h4 className={styles.subHeading}>Quando utilizar</h4>
              <p className={styles.subText}>Ao final de um processo, projeto ou plano que necessite consolidação formal para registro ou prestação de contas.</p>
              <h4 className={styles.subHeading}>O que o sistema gera</h4>
              <ul className={styles.subList}>
                <li>Dossiê completo em PDF</li>
                <li>Compilação de POP, riscos, planejamento, ações e indicadores</li>
              </ul>
              <h4 className={styles.subHeading}>Valor institucional</h4>
              <p className={styles.valorText}>Evidência organizada da governança adotada.</p>
            </div>

            {/* 8 — Relatório Técnico Consolidado */}
            <div className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Relatório Técnico Consolidado</h3>
                <span className={styles.tagPlanejado}>Em desenvolvimento</span>
              </div>
              <h4 className={styles.subHeading}>O que é</h4>
              <p className={styles.subText}>Documento técnico com histórico completo do processo.</p>
              <h4 className={styles.subHeading}>Quando utilizar</h4>
              <p className={styles.subText}>Para formalização administrativa e arquivamento institucional.</p>
              <h4 className={styles.subHeading}>O que o sistema gera</h4>
              <ul className={styles.subList}>
                <li>Relatório técnico estruturado</li>
                <li>Registro de decisões e etapas executadas</li>
              </ul>
              <h4 className={styles.subHeading}>Valor institucional</h4>
              <p className={styles.valorText}>Documentação formal adequada para registro e tramitação.</p>
            </div>

            {/* 9 — Relatório de Conformidade */}
            <div className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Relatório de Conformidade</h3>
                <span className={styles.tagPlanejado}>Em desenvolvimento</span>
              </div>
              <h4 className={styles.subHeading}>O que é</h4>
              <p className={styles.subText}>Ferramenta de verificação de aderência do processo ao POP e às regras estabelecidas.</p>
              <h4 className={styles.subHeading}>Quando utilizar</h4>
              <p className={styles.subText}>Para avaliar se a execução seguiu etapas previstas e prazos definidos.</p>
              <h4 className={styles.subHeading}>O que o sistema gera</h4>
              <ul className={styles.subList}>
                <li>Relatório de verificação</li>
                <li>Identificação de desvios</li>
                <li>Registro formal de conformidade</li>
              </ul>
              <h4 className={styles.subHeading}>Valor institucional</h4>
              <p className={styles.valorText}>Redução de risco administrativo e fortalecimento do controle interno.</p>
            </div>

            {/* 10 — Revisão e Adequação de Documentos */}
            <div className={styles.productCard}>
              <div className={styles.productHeader}>
                <h3 className={styles.productName}>Revisão e Adequação de Documentos</h3>
                <span className={styles.tagPlanejado}>Em desenvolvimento</span>
              </div>
              <h4 className={styles.subHeading}>O que é</h4>
              <p className={styles.subText}>Ferramenta de revisão documental com foco em linguagem simples e adequação institucional.</p>
              <h4 className={styles.subHeading}>Quando utilizar</h4>
              <p className={styles.subText}>Na preparação de documentos oficiais para publicação ou tramitação.</p>
              <h4 className={styles.subHeading}>O que o sistema gera</h4>
              <ul className={styles.subList}>
                <li>Documento revisado</li>
                <li>Ajustes de clareza e conformidade normativa</li>
              </ul>
              <h4 className={styles.subHeading}>Valor institucional</h4>
              <p className={styles.valorText}>Melhoria da comunicação oficial e aderência aos padrões federais.</p>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
}
