/**
 * DashboardLanding - Página institucional do Painel de Gestão MapaGov
 *
 * Artefato de acompanhamento institucional. Apresenta KPIs consolidados
 * de Mapeamento, Riscos, Planejamento Estratégico e Adoção.
 *
 * Os dados refletem registros produzidos pelas áreas — não avaliam desempenho.
 * Cada seção inclui: definição, fonte, recorte, cobertura e limitações.
 */
import React from 'react';
import styles from './DashboardLanding.module.css';

/* ===== TYPES ===== */

interface KpiConfig {
  key: string;
  label: string;
  sufixo?: string;
}

interface SecaoConfig {
  id: string;
  titulo: string;
  definicao: string;
  fonte: string;
  recorte: string;
  cobertura: string;
  limitacoes: string;
  kpis: KpiConfig[];
  bullets: string[];
  nota?: string;
}

interface MetricaGlossario {
  termo: string;
  oQueE: string;
  naoInclui: string;
  podeVariar: string;
}

export interface PainelGestaoKPIs {
  mapeamento?: {
    atividades_registradas?: number;
    pops_publicados?: number;
    pct_pops_atividades?: number;
  };
  riscos?: {
    riscos_abertos?: number;
    pct_alto_critico?: number;
    processos_sem_plano?: number;
  };
  pe?: {
    projetos_ativos?: number;
    pct_em_execucao?: number;
    demandas_pendentes?: number;
  };
  adocao?: {
    usuarios_ativos_30d?: number;
    areas_ativas?: number;
    variacao_90d?: string;
  };
}

export interface PainelGestaoOverview {
  atualizadoEm: string;
  areasComRegistro: number;
  totalAreas: number;
  disclaimerFonteExterna?: string;
  kpis: PainelGestaoKPIs;
}

interface DashboardLandingProps {
  onAcessar: () => void;
  dados?: PainelGestaoOverview | null;
}

/* ===== CONSTANTES — SEÇÕES ===== */

const SECOES: SecaoConfig[] = [
  {
    id: 'mapeamento',
    titulo: 'Mapeamento de Processos',
    definicao: 'Registros de atividades e POPs produzidos via conversa guiada com Helena Mapeamento.',
    fonte: 'Registros exportados (CSV/JSON) e banco de dados do MapaGov.',
    recorte: 'Acumulado desde o início da operação, com filtro por período.',
    cobertura: 'Áreas com ao menos 1 atividade registrada no período.',
    limitacoes: 'Não inclui atividades registradas fora da ferramenta. Nem todas as atividades mapeadas resultam necessariamente em POP.',
    kpis: [
      { key: 'atividades_registradas', label: 'Atividades registradas' },
      { key: 'pops_publicados', label: 'POPs publicados' },
      { key: 'pct_pops_atividades', label: '% de atividades com POP', sufixo: '%' },
    ],
    bullets: [
      'atividades registradas por área;',
      'POPs publicados por área;',
      'áreas com cobertura acima de 50%;',
      'áreas sem dados suficientes no período.',
    ],
  },
  {
    id: 'riscos',
    titulo: 'Análise de Riscos',
    definicao: 'Riscos identificados durante análise guiada de processos mapeados.',
    fonte: 'Registros da Helena Análise de Riscos associados a processos existentes.',
    recorte: 'Situação atual dos riscos registrados, com histórico por período.',
    cobertura: 'Processos com ao menos 1 risco registrado.',
    limitacoes: 'Riscos só são registrados para processos previamente mapeados. A criticidade reflete a classificação informada pelo usuário.',
    kpis: [
      { key: 'riscos_abertos', label: 'Riscos abertos' },
      { key: 'pct_alto_critico', label: '% alto/crítico', sufixo: '%' },
      { key: 'processos_sem_plano', label: 'Processos sem plano' },
    ],
    bullets: [
      'distribuição de riscos por nível de criticidade;',
      'processos com riscos pendentes de tratamento;',
      'áreas com riscos registrados;',
      'áreas sem dados suficientes no período.',
    ],
  },
  {
    id: 'pe',
    titulo: 'Planejamento Estratégico',
    definicao: 'Projetos estratégicos e demandas da direção registrados via Helena PE.',
    fonte: 'Dados do Dashboard de Áreas e Dashboard do Diretor.',
    recorte: 'Projetos ativos no período selecionado.',
    cobertura: 'Áreas com ao menos 1 projeto registrado.',
    limitacoes: 'Andamento e fases refletem a última atualização registrada pela área responsável. Projetos suspensos ou encerrados não contam como ativos.',
    kpis: [
      { key: 'projetos_ativos', label: 'Projetos ativos' },
      { key: 'pct_em_execucao', label: '% em execução', sufixo: '%' },
      { key: 'demandas_pendentes', label: 'Demandas pendentes' },
    ],
    bullets: [
      'projetos registrados por área e fase;',
      'andamento das fases (planejamento, execução, conclusão);',
      'demandas da direção e status de atendimento;',
      'áreas sem dados suficientes no período.',
    ],
  },
  {
    id: 'adocao',
    titulo: 'Uso e Adoção',
    definicao: 'Métricas de utilização das ferramentas do MapaGov por área e período.',
    fonte: 'Registros de sessão e autenticação do sistema.',
    recorte: 'Últimos 30 dias (usuários ativos) e últimos 90 dias (variação).',
    cobertura: 'Áreas com ao menos 1 usuário autenticado no período.',
    limitacoes: 'Ausência de registro pode decorrer de férias, migração de sistemas, escopo específico da área ou indisponibilidade temporária. Não representa avaliação de desempenho.',
    kpis: [
      { key: 'usuarios_ativos_30d', label: 'Usuários ativos (30d)' },
      { key: 'areas_ativas', label: 'Áreas ativas' },
      { key: 'variacao_90d', label: 'Variação (90d)' },
    ],
    nota: 'Nota: Área ativa = ao menos 1 sessão concluída no período. Ausência de registro pode decorrer de férias, migração ou escopo da área.',
    bullets: [
      'usuários ativos por área nos últimos 30 dias;',
      'áreas com sessões registradas;',
      'variação de uso nos últimos 90 dias;',
      'áreas sem dados suficientes no período.',
    ],
  },
];

/* ===== CONSTANTES — GLOSSÁRIO ===== */

const GLOSSARIO_METRICAS: MetricaGlossario[] = [
  {
    termo: 'Atividades registradas',
    oQueE: 'Total de atividades inseridas via conversa guiada com Helena Mapeamento.',
    naoInclui: 'Atividades importadas ou registradas manualmente fora da ferramenta.',
    podeVariar: 'Registros podem ser excluídos, revisados ou ter versões anteriores substituídas.',
  },
  {
    termo: '% de atividades com POP publicado',
    oQueE: 'Proporção de atividades registradas que possuem ao menos um POP publicado associado.',
    naoInclui: 'Atividades que deliberadamente não exigem formalização em POP.',
    podeVariar: 'Nem todas as atividades mapeadas resultam necessariamente em um POP.',
  },
  {
    termo: 'Riscos abertos',
    oQueE: 'Total de riscos registrados com status diferente de "tratado" ou "aceito".',
    naoInclui: 'Riscos encerrados, aceitos ou arquivados.',
    podeVariar: 'A classificação é informada pelo usuário e pode ser atualizada a qualquer momento.',
  },
  {
    termo: 'Projetos ativos',
    oQueE: 'Projetos estratégicos com fase diferente de "Encerrado" ou "Suspenso".',
    naoInclui: 'Projetos encerrados, suspensos ou em fase de planejamento sem registro inicial.',
    podeVariar: 'O status reflete a última atualização registrada pela área responsável.',
  },
  {
    termo: 'Usuários ativos (30d)',
    oQueE: 'Usuários que realizaram ao menos 1 sessão autenticada nos últimos 30 dias.',
    naoInclui: 'Acessos não autenticados ou sessões expiradas sem interação.',
    podeVariar: 'Férias, licenças, mudanças de lotação ou indisponibilidade do sistema afetam o número.',
  },
  {
    termo: 'Variação (90d)',
    oQueE: 'Diferença percentual no número de sessões entre os últimos 90 dias e os 90 dias anteriores.',
    naoInclui: 'Análise qualitativa do uso. Crescente não é necessariamente positivo; decrescente não é necessariamente negativo.',
    podeVariar: 'Sazonalidade, implantação gradual e eventos institucionais influenciam a variação.',
  },
];

/* ===== HELPERS ===== */

function formatarValor(valor: number | string | undefined | null, sufixo?: string): string {
  if (valor === undefined || valor === null) return '\u2014';
  if (typeof valor === 'string') return valor;
  return `${valor.toLocaleString('pt-BR')}${sufixo || ''}`;
}

function formatarData(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleDateString('pt-BR', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

/* ===== COMPONENTE ===== */

const DashboardLanding: React.FC<DashboardLandingProps> = ({ onAcessar, dados }) => {

  const getKpiValue = (secaoId: string, kpiKey: string): number | string | undefined => {
    if (!dados?.kpis) return undefined;
    const secao = dados.kpis[secaoId as keyof PainelGestaoKPIs];
    if (!secao) return undefined;
    return (secao as Record<string, number | string | undefined>)[kpiKey];
  };

  return (
    <div className={styles.container}>

      {/* 1. Título — alinhado à esquerda, hierarquia "serviço" */}
      <header className={styles.header}>
        <h1 className={styles.title}>Painel de Gestão</h1>
      </header>

      {/* 2. Banner de Atualização */}
      <div className={styles.freshnessBanner} role="status" aria-live="polite">
        <span className={styles.freshnessIcon} aria-hidden="true">{'\u25F7'}</span>
        {dados ? (
          <div>
            <div className={styles.freshnessText}>
              Dados consolidados até {formatarData(dados.atualizadoEm)}
              {' \u00B7 '}
              {dados.areasComRegistro} de {dados.totalAreas} áreas com registros no período
            </div>
            <div className={styles.freshnessMeta}>
              {dados.disclaimerFonteExterna || 'Atualização automática diária. Fontes externas dependem de exportação pelas áreas.'}
            </div>
          </div>
        ) : (
          <div className={styles.freshnessText}>
            Dados não disponíveis. O painel será atualizado quando houver registros nas ferramentas do MapaGov.
          </div>
        )}
      </div>

      {/* 3. Context Card */}
      <section className={styles.contextCard}>
        <p>
          O Painel de Gestão reúne, em uma visão consolidada, os registros
          produzidos pelas ferramentas do MapaGov. Os dados refletem exclusivamente
          o que foi registrado pelas áreas durante o uso das ferramentas.
        </p>
        <p>
          Áreas sem registro no período aparecem como &ldquo;Sem dados suficientes&rdquo;.
          A cobertura e a atualização dos dados são informadas em cada seção.
        </p>
      </section>

      {/* 4. Helena Card */}
      <section className={styles.helenaCard}>
        <div className={styles.helenaCardInner}>
          <div className={styles.helenaAvatar}>
            <img
              src="/helena_gestao.png"
              alt="Helena - Consolidação do Painel de Gestão"
            />
          </div>
          <div className={styles.helenaContent}>
            <h2 className={styles.helenaTitle}>Helena — Painel de Gestão</h2>
            <p className={styles.helenaText}>
              Helena organiza as informações produzidas durante as conversas guiadas
              e apresenta um panorama por área, por produto e por período.
              Os indicadores são calculados a partir dos registros existentes —
              não representam avaliação de desempenho.
            </p>
            <p className={styles.helenaDisclaimer}>
              Os dados consolidados refletem os registros das áreas.
              A interpretação e as decisões decorrentes são de responsabilidade
              da gestão e das instâncias institucionais competentes.
            </p>
          </div>
        </div>
      </section>

      {/* 5. Seções com KPI Preview */}
      {SECOES.map((secao) => (
        <section key={secao.id} className={styles.kpiSection} aria-labelledby={`titulo-${secao.id}`}>
          <h2 id={`titulo-${secao.id}`} className={styles.sectionTitle}>{secao.titulo}</h2>

          {/* KPI Grid */}
          <div className={styles.kpiGrid} role="group" aria-label={`Indicadores de ${secao.titulo}`}>
            {secao.kpis.map((kpi) => {
              const valor = getKpiValue(secao.id, kpi.key);
              const valorFormatado = formatarValor(valor, kpi.sufixo);
              return (
                <div
                  key={kpi.key}
                  className={styles.kpiCard}
                  aria-label={`${kpi.label}: ${valorFormatado === '\u2014' ? 'sem dados' : valorFormatado}`}
                >
                  <div className={styles.kpiValue}>{valorFormatado}</div>
                  <div className={styles.kpiLabel}>{kpi.label}</div>
                </div>
              );
            })}
          </div>

          {/* Definition Block — estrutura semântica padronizada */}
          <dl className={styles.definitionBlock}>
            <div className={styles.definitionRow}>
              <dt>O que mede: </dt>
              <dd>{secao.definicao}</dd>
            </div>
            <div className={styles.definitionRow}>
              <dt>Fonte: </dt>
              <dd>{secao.fonte}</dd>
            </div>
            <div className={styles.definitionRow}>
              <dt>Recorte temporal: </dt>
              <dd>{secao.recorte}</dd>
            </div>
            <div className={styles.definitionRow}>
              <dt>Cobertura: </dt>
              <dd>{secao.cobertura}</dd>
            </div>
            <div className={styles.definitionRow}>
              <dt>Limitações conhecidas: </dt>
              <dd>{secao.limitacoes}</dd>
            </div>
          </dl>

          {/* Nota contextual (ex: seção Adoção) */}
          {secao.nota && (
            <p className={styles.sectionNote}>{secao.nota}</p>
          )}

          {/* Bullets: o que encontra no painel */}
          <p className={styles.bulletIntro}>O que você encontra no painel:</p>
          <ul className={styles.bulletList}>
            {secao.bullets.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </section>
      ))}

      {/* 6. Decision Block */}
      <section className={styles.decisionBlock}>
        <h2 className={styles.sectionTitle}>Responsabilidade institucional</h2>
        <p className={styles.decisionText}>
          O Painel de Gestão é uma ferramenta de acompanhamento institucional.
          Os dados apresentados refletem os registros produzidos pelas áreas
          durante o uso das ferramentas do MapaGov. A interpretação e as decisões
          decorrentes são de responsabilidade da gestão.
        </p>

        {/* Accordion acessível — sem armadilha de foco */}
        <details className={styles.metricsDetails}>
          <summary>Entenda as métricas e limitações</summary>
          <div className={styles.metricsContent}>
            {GLOSSARIO_METRICAS.map((metrica) => (
              <div key={metrica.termo} className={styles.metricsEntry}>
                <h3 className={styles.metricsEntryTitle}>{metrica.termo}</h3>
                <p><strong>O que é:</strong> {metrica.oQueE}</p>
                <p><strong>Não inclui:</strong> {metrica.naoInclui}</p>
                <p><strong>Pode variar porque:</strong> {metrica.podeVariar}</p>
              </div>
            ))}
          </div>
        </details>
      </section>

      {/* 7. CTA */}
      <section className={styles.ctaSection}>
        <p className={styles.ctaText}>
          Acesse o painel para visualizar os indicadores consolidados
          e acompanhar o panorama institucional por área e período.
        </p>
        <button
          type="button"
          className={styles.ctaButton}
          onClick={onAcessar}
        >
          Acessar Painel
        </button>
      </section>
    </div>
  );
};

export default DashboardLanding;
