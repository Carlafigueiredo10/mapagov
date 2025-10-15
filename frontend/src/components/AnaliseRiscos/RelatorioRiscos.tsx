// RelatorioRiscos.tsx - Visualização completa do relatório de riscos
import { useState } from 'react';
import { useRiscosStore } from '../../store/riscosStore';
import MatrizRiscos from './MatrizRiscos';
import PDFButton from './PDFButton';
import type { Risco } from './types';
import styles from './RelatorioRiscos.module.css';

export default function RelatorioRiscos() {
  const { relatorio, popInfo } = useRiscosStore();
  const [expandedRisk, setExpandedRisk] = useState<number | null>(null);
  const [filterCategory, setFilterCategory] = useState<string>('all');

  if (!relatorio) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner} />
        <p>Carregando relatório...</p>
      </div>
    );
  }

  const categories = [
    'all',
    'Operacional',
    'Tecnológico',
    'Normativo',
    'Financeiro',
    'Reputacional',
    'Integridade',
  ];

  const filteredRisks =
    filterCategory === 'all'
      ? relatorio.riscos
      : relatorio.riscos.filter((r) => r.categoria === filterCategory);

  const getSeverityColor = (severidade: string) => {
    const colors = {
      Crítico: '#d32f2f',
      Alto: '#f57c00',
      Moderado: '#f9a825',
      Baixo: '#388e3c',
    };
    return colors[severidade as keyof typeof colors] || '#757575';
  };

  const toggleRisk = (index: number) => {
    setExpandedRisk(expandedRisk === index ? null : index);
  };

  return (
    <div className={styles.container}>
      {/* Cabeçalho */}
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <h1>📋 Relatório de Análise de Riscos</h1>
          <div className={styles.headerMeta}>
            <div>
              <strong>POP:</strong> {relatorio.cabecalho.pop}
            </div>
            <div>
              <strong>Código:</strong> {relatorio.cabecalho.codigo}
            </div>
            <div>
              <strong>Data:</strong> {relatorio.cabecalho.data_analise}
            </div>
          </div>
        </div>
        <PDFButton relatorio={relatorio} />
      </div>

      {/* Matriz de Riscos */}
      <MatrizRiscos matriz={relatorio.matriz_riscos} />

      {/* Sumário Executivo */}
      <div className={styles.summaryBox}>
        <h3>💡 Sumário Executivo</h3>
        <div className={styles.summaryGrid}>
          <div className={styles.summaryCard}>
            <h4>🎯 Maiores Riscos</h4>
            <ul>
              {relatorio.sumario_executivo.maiores_riscos.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>
          <div className={styles.summaryCard}>
            <h4>⚠️ Áreas Críticas</h4>
            <ul>
              {relatorio.sumario_executivo.areas_criticas.map((a, i) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
          </div>
          <div className={styles.summaryCard}>
            <h4>🚨 Ações Urgentes</h4>
            <ul>
              {relatorio.sumario_executivo.acoes_urgentes.map((a, i) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
          </div>
        </div>
        <div className={styles.syntesis}>
          <strong>Síntese Gerencial:</strong>
          <p>{relatorio.sumario_executivo.sintese_gerencial}</p>
        </div>
      </div>

      {/* Filtros */}
      <div className={styles.filtersSection}>
        <h3>🔍 Riscos Identificados ({filteredRisks.length})</h3>
        <div className={styles.filters}>
          {categories.map((cat) => (
            <button
              key={cat}
              className={`${styles.filterBtn} ${
                filterCategory === cat ? styles.active : ''
              }`}
              onClick={() => setFilterCategory(cat)}
            >
              {cat === 'all' ? 'Todos' : cat}
              {cat !== 'all' &&
                ` (${relatorio.riscos.filter((r) => r.categoria === cat).length})`}
            </button>
          ))}
        </div>
      </div>

      {/* Lista de Riscos */}
      <div className={styles.risksList}>
        {filteredRisks.map((risco, index) => (
          <div
            key={index}
            className={`${styles.riskCard} ${
              expandedRisk === index ? styles.expanded : ''
            }`}
          >
            <div
              className={styles.riskHeader}
              onClick={() => toggleRisk(index)}
            >
              <div className={styles.riskTitle}>
                <h4>{risco.titulo}</h4>
                <div className={styles.riskMeta}>
                  <span className={styles.category}>{risco.categoria}</span>
                  <span
                    className={styles.severity}
                    style={{
                      background: `${getSeverityColor(risco.severidade)}20`,
                      color: getSeverityColor(risco.severidade),
                      border: `1px solid ${getSeverityColor(risco.severidade)}40`,
                    }}
                  >
                    {risco.severidade}
                  </span>
                </div>
              </div>
              <span className={styles.expandIcon}>
                {expandedRisk === index ? '▲' : '▼'}
              </span>
            </div>

            <div className={styles.riskBody}>
              <p className={styles.description}>{risco.descricao}</p>

              <div className={styles.riskDetails}>
                <div className={styles.detailRow}>
                  <strong>Probabilidade:</strong>
                  <span>{risco.probabilidade}</span>
                </div>
                <div className={styles.detailRow}>
                  <strong>Impacto:</strong>
                  <span>{risco.impacto}</span>
                </div>
                <div className={styles.detailRow}>
                  <strong>Tipo:</strong>
                  <span>{risco.tipo_risco}</span>
                </div>
                {risco.normativo_relacionado &&
                  risco.normativo_relacionado !== 'Não aplicável' && (
                    <div className={styles.detailRow}>
                      <strong>Normativo:</strong>
                      <span>{risco.normativo_relacionado}</span>
                    </div>
                  )}
              </div>

              <div className={styles.treatmentBox}>
                <div className={styles.treatmentHeader}>
                  💡 Tratamento Recomendado
                </div>
                <p>{risco.tratamento_recomendado}</p>
              </div>

              {risco.controles_existentes.length > 0 && (
                <div className={styles.controlsBox}>
                  <strong>✓ Controles Existentes:</strong>
                  <ul>
                    {risco.controles_existentes.map((c, i) => (
                      <li key={i}>{c}</li>
                    ))}
                  </ul>
                </div>
              )}

              {risco.indicadores_monitoramento.length > 0 && (
                <div className={styles.indicatorsBox}>
                  <strong>📊 Indicadores de Monitoramento:</strong>
                  <ul>
                    {risco.indicadores_monitoramento.map((ind, i) => (
                      <li key={i}>{ind}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Conclusões */}
      <div className={styles.conclusions}>
        <h3>📌 Conclusões e Recomendações</h3>
        <p>{relatorio.conclusoes_recomendacoes}</p>
      </div>

      {/* Botão de nova análise */}
      <div className={styles.actions}>
        <button
          className={styles.btnSecondary}
          onClick={() => window.location.reload()}
        >
          🔄 Nova Análise
        </button>
        <PDFButton relatorio={relatorio} variant="large" />
      </div>
    </div>
  );
}
