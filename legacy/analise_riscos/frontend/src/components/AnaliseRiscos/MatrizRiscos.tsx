// MatrizRiscos.tsx - Visualização da Matriz de Riscos
import type { MatrizRiscos as MatrizRiscosType } from './types';
import styles from './MatrizRiscos.module.css';

interface MatrizRiscosProps {
  matriz: MatrizRiscosType;
}

export default function MatrizRiscos({ matriz }: MatrizRiscosProps) {
  const total = matriz.criticos + matriz.altos + matriz.moderados + matriz.baixos;

  const cards = [
    {
      label: 'Críticos',
      count: matriz.criticos,
      color: 'critical',
      icon: '🔴',
      percent: total > 0 ? Math.round((matriz.criticos / total) * 100) : 0,
    },
    {
      label: 'Altos',
      count: matriz.altos,
      color: 'high',
      icon: '🟠',
      percent: total > 0 ? Math.round((matriz.altos / total) * 100) : 0,
    },
    {
      label: 'Moderados',
      count: matriz.moderados,
      color: 'moderate',
      icon: '🟡',
      percent: total > 0 ? Math.round((matriz.moderados / total) * 100) : 0,
    },
    {
      label: 'Baixos',
      count: matriz.baixos,
      color: 'low',
      icon: '🟢',
      percent: total > 0 ? Math.round((matriz.baixos / total) * 100) : 0,
    },
  ];

  return (
    <div className={styles.container}>
      <h3 className={styles.title}>📊 Matriz de Riscos</h3>
      <div className={styles.grid}>
        {cards.map((card) => (
          <div key={card.label} className={`${styles.card} ${styles[card.color]}`}>
            <div className={styles.cardHeader}>
              <span className={styles.icon}>{card.icon}</span>
              <span className={styles.label}>{card.label}</span>
            </div>
            <div className={styles.cardBody}>
              <div className={styles.count}>{card.count}</div>
              <div className={styles.percent}>{card.percent}%</div>
            </div>
            <div className={styles.progressBar}>
              <div
                className={styles.progressFill}
                style={{ width: `${card.percent}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      <div className={styles.summary}>
        <div className={styles.summaryItem}>
          <strong>Total de Riscos:</strong>
          <span className={styles.totalBadge}>{total}</span>
        </div>
        <div className={styles.summaryItem}>
          <strong>Exposição Geral:</strong>
          <span className={styles.exposureBadge}>
            {matriz.criticos > 0
              ? '🔴 Crítica'
              : matriz.altos > 2
              ? '🟠 Alta'
              : matriz.altos > 0 || matriz.moderados > 3
              ? '🟡 Moderada'
              : '🟢 Baixa'}
          </span>
        </div>
      </div>
    </div>
  );
}
