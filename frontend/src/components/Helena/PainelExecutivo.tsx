/**
 * PainelExecutivo - Visão consolidada do Painel de Gestão MapaGov
 *
 * Exibe KPIs por produto e detalhamento por área organizacional.
 * Artefato de acompanhamento institucional — sem ranking, sem cor valorativa.
 *
 * Fontes: Mapeamento, Riscos, PE, Adoção (login/sessões).
 * Dados refletem registros das áreas, não avaliam desempenho.
 */
import React from 'react';
import styles from './PainelExecutivo.module.css';
import type { PainelGestaoOverview, PainelGestaoKPIs } from './DashboardLanding';

/* ===== TYPES ===== */

interface DadosArea {
  sigla: string;
  mapeamento: { atividades: number; pops: number } | null;
  riscos: { abertos: number; criticos: number } | null;
  pe: { projetos: number; demandas: number } | null;
  adocao: { usuarios_30d: number } | null;
}

interface PainelExecutivoProps {
  onVoltar: () => void;
  overview?: PainelGestaoOverview | null;
  dadosPorArea?: DadosArea[];
}

/* ===== SUMMARY CONFIG ===== */

interface SummaryConfig {
  id: keyof PainelGestaoKPIs;
  titulo: string;
  kpis: Array<{ key: string; label: string; sufixo?: string }>;
}

const SUMMARY_SECTIONS: SummaryConfig[] = [
  {
    id: 'mapeamento',
    titulo: 'Mapeamento',
    kpis: [
      { key: 'atividades_registradas', label: 'Atividades' },
      { key: 'pops_publicados', label: 'POPs' },
      { key: 'pct_pops_atividades', label: '% c/ POP', sufixo: '%' },
    ],
  },
  {
    id: 'riscos',
    titulo: 'Riscos',
    kpis: [
      { key: 'riscos_abertos', label: 'Abertos' },
      { key: 'pct_alto_critico', label: '% crítico', sufixo: '%' },
      { key: 'processos_sem_plano', label: 'S/ plano' },
    ],
  },
  {
    id: 'pe',
    titulo: 'Planej. Estratégico',
    kpis: [
      { key: 'projetos_ativos', label: 'Projetos' },
      { key: 'pct_em_execucao', label: '% execução', sufixo: '%' },
      { key: 'demandas_pendentes', label: 'Demandas' },
    ],
  },
  {
    id: 'adocao',
    titulo: 'Adoção',
    kpis: [
      { key: 'usuarios_ativos_30d', label: 'Usuários (30d)' },
      { key: 'areas_ativas', label: 'Áreas ativas' },
      { key: 'variacao_90d', label: 'Variação (90d)' },
    ],
  },
];

/* ===== TABLE COLUMNS ===== */

const COLUNAS_TABELA = [
  { key: 'sigla', label: 'Área' },
  { key: 'map_ativ', label: 'Atividades' },
  { key: 'map_pops', label: 'POPs' },
  { key: 'ris_abertos', label: 'Riscos abertos' },
  { key: 'ris_criticos', label: 'Riscos críticos' },
  { key: 'pe_projetos', label: 'Projetos' },
  { key: 'pe_demandas', label: 'Demandas' },
  { key: 'ado_usuarios', label: 'Usuários (30d)' },
] as const;

/* ===== HELPERS ===== */

function fmt(valor: number | string | undefined | null, sufixo?: string): string {
  if (valor === undefined || valor === null) return '\u2014';
  if (typeof valor === 'string') return valor;
  return `${valor.toLocaleString('pt-BR')}${sufixo || ''}`;
}

function fmtData(iso: string): string {
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

function celula(dados: DadosArea, colKey: string): string {
  switch (colKey) {
    case 'sigla': return dados.sigla;
    case 'map_ativ': return dados.mapeamento ? fmt(dados.mapeamento.atividades) : '\u2014';
    case 'map_pops': return dados.mapeamento ? fmt(dados.mapeamento.pops) : '\u2014';
    case 'ris_abertos': return dados.riscos ? fmt(dados.riscos.abertos) : '\u2014';
    case 'ris_criticos': return dados.riscos ? fmt(dados.riscos.criticos) : '\u2014';
    case 'pe_projetos': return dados.pe ? fmt(dados.pe.projetos) : '\u2014';
    case 'pe_demandas': return dados.pe ? fmt(dados.pe.demandas) : '\u2014';
    case 'ado_usuarios': return dados.adocao ? fmt(dados.adocao.usuarios_30d) : '\u2014';
    default: return '\u2014';
  }
}

/* ===== COMPONENTE ===== */

const PainelExecutivo: React.FC<PainelExecutivoProps> = ({ onVoltar, overview, dadosPorArea }) => {

  const getKpiValue = (secaoId: keyof PainelGestaoKPIs, kpiKey: string): number | string | undefined => {
    if (!overview?.kpis) return undefined;
    const secao = overview.kpis[secaoId];
    if (!secao) return undefined;
    return (secao as Record<string, number | string | undefined>)[kpiKey];
  };

  return (
    <div className={styles.container}>

      {/* Top Bar */}
      <div className={styles.topBar}>
        <button className={styles.backButton} onClick={onVoltar} type="button">
          {'\u2190'} Voltar
        </button>
        <h1 className={styles.pageTitle}>Painel de Gestão</h1>
      </div>

      {/* Freshness Banner */}
      <div className={styles.freshnessBanner} role="status" aria-live="polite">
        <span className={styles.freshnessIcon} aria-hidden="true">{'\u25F7'}</span>
        {overview ? (
          <div>
            <div className={styles.freshnessText}>
              Dados consolidados até {fmtData(overview.atualizadoEm)}
              {' \u00B7 '}
              {overview.areasComRegistro} de {overview.totalAreas} áreas com registros
            </div>
            <div className={styles.freshnessMeta}>
              {overview.disclaimerFonteExterna || 'Atualização automática diária. Fontes externas dependem de exportação pelas áreas.'}
            </div>
          </div>
        ) : (
          <div className={styles.freshnessText}>
            Dados não disponíveis. O painel será atualizado quando houver registros nas ferramentas do MapaGov.
          </div>
        )}
      </div>

      {/* Summary Grid — 4 cards */}
      <div className={styles.summaryGrid}>
        {SUMMARY_SECTIONS.map((secao) => (
          <div key={secao.id} className={styles.summaryCard}>
            <h2 className={styles.summaryCardTitle}>{secao.titulo}</h2>
            <div className={styles.summaryKpiRow}>
              {secao.kpis.map((kpi) => {
                const valor = getKpiValue(secao.id, kpi.key);
                const valorFormatado = fmt(valor, kpi.sufixo);
                return (
                  <div
                    key={kpi.key}
                    className={styles.summaryKpi}
                    aria-label={`${kpi.label}: ${valorFormatado === '\u2014' ? 'sem dados' : valorFormatado}`}
                  >
                    <div className={styles.summaryKpiValue}>{valorFormatado}</div>
                    <div className={styles.summaryKpiLabel}>{kpi.label}</div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Tabela por Área */}
      <div className={styles.tableSection}>
        <div className={styles.tableSectionHeader}>
          <h2 className={styles.tableSectionTitle}>Panorama por área</h2>
          <span className={styles.tableSectionMeta}>
            {dadosPorArea
              ? `${dadosPorArea.filter(a =>
                  a.mapeamento || a.riscos || a.pe || a.adocao
                ).length} áreas com dados`
              : 'Sem dados disponíveis'}
          </span>
        </div>

        {dadosPorArea && dadosPorArea.length > 0 ? (
          <table className={styles.areaTable}>
            <thead>
              <tr>
                {COLUNAS_TABELA.map((col) => (
                  <th key={col.key}>{col.label}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {dadosPorArea.map((area) => {
                const temDados = area.mapeamento || area.riscos || area.pe || area.adocao;
                return (
                  <tr key={area.sigla}>
                    {COLUNAS_TABELA.map((col) => (
                      <td
                        key={col.key}
                        className={col.key === 'sigla' ? styles.areaSigla : (!temDados ? styles.noData : undefined)}
                      >
                        {col.key === 'sigla'
                          ? area.sigla
                          : (!temDados ? 'Sem dados suficientes' : celula(area, col.key))}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
            <tfoot>
              <tr>
                <td>Total</td>
                <td>{fmt(dadosPorArea.reduce((s, a) => s + (a.mapeamento?.atividades ?? 0), 0))}</td>
                <td>{fmt(dadosPorArea.reduce((s, a) => s + (a.mapeamento?.pops ?? 0), 0))}</td>
                <td>{fmt(dadosPorArea.reduce((s, a) => s + (a.riscos?.abertos ?? 0), 0))}</td>
                <td>{fmt(dadosPorArea.reduce((s, a) => s + (a.riscos?.criticos ?? 0), 0))}</td>
                <td>{fmt(dadosPorArea.reduce((s, a) => s + (a.pe?.projetos ?? 0), 0))}</td>
                <td>{fmt(dadosPorArea.reduce((s, a) => s + (a.pe?.demandas ?? 0), 0))}</td>
                <td>{fmt(dadosPorArea.reduce((s, a) => s + (a.adocao?.usuarios_30d ?? 0), 0))}</td>
              </tr>
            </tfoot>
          </table>
        ) : (
          <div style={{ padding: '32px 20px', textAlign: 'center', color: '#636363', fontSize: '14px' }}>
            Nenhuma área com dados registrados no período.
            Verifique se há exportações pendentes ou registros nas ferramentas.
          </div>
        )}
      </div>

      {/* Disclaimer */}
      <div className={styles.disclaimer}>
        <h3 className={styles.disclaimerTitle}>Responsabilidade institucional</h3>
        <p className={styles.disclaimerText}>
          Os dados apresentados refletem os registros produzidos pelas áreas durante o uso
          das ferramentas do MapaGov. A interpretação e as decisões decorrentes são de
          responsabilidade da gestão. Áreas sem registro aparecem como &ldquo;Sem dados
          suficientes&rdquo; — ausência de dado não implica inatividade.
        </p>
      </div>
    </div>
  );
};

export default PainelExecutivo;
