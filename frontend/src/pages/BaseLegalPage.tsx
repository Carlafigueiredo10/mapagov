import { Link } from 'react-router-dom';
import Layout from '../components/Layout/Layout';
import { CATEGORIES } from './baseLegalLinks';
import type { Doc } from './baseLegalLinks';
import styles from './BaseLegalPage.module.css';

const BADGE_LABELS: Record<Doc['badge'], string> = {
  pdf: 'PDF',
  web: 'WEB',
  pago: 'ACESSO PAGO',
  indisponivel: 'INDISPON\u00cdVEL',
};

const BADGE_STYLES: Record<Doc['badge'], string> = {
  pdf: 'badgePdf',
  web: 'badgeWeb',
  pago: 'badgePago',
  indisponivel: 'badgeIndisponivel',
};

export default function BaseLegalPage() {
  return (
    <Layout>
      <div className={styles.container}>
        <Link to="/" className={styles.backLink}>
          ← Voltar ao início
        </Link>

        <header className={styles.header}>
          <h1 className={styles.title}>Base Legal Integrada</h1>
          <p className={styles.subtitle}>
            Biblioteca de documentos normativos, referenciais técnicos e guias oficiais que
            fundamentam as práticas de governança, gestão de riscos e integridade no âmbito
            da administração pública federal.
          </p>
        </header>

        {CATEGORIES.map((cat) => (
          <section key={cat.title} className={styles.category}>
            <div className={styles.categoryHeader}>
              <span className={styles.categoryIcon}>{cat.icon}</span>
              <h2 className={styles.categoryTitle}>{cat.title}</h2>
            </div>
            <ul className={styles.docList}>
              {cat.docs.map((doc) => (
                <li key={doc.title} className={styles.docItem}>
                  <span className={`${styles.badge} ${styles[BADGE_STYLES[doc.badge]]}`}>
                    {BADGE_LABELS[doc.badge]}
                  </span>
                  <div>
                    {doc.url ? (
                      <a
                        href={doc.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={styles.docLink}
                      >
                        {doc.title}
                      </a>
                    ) : (
                      <span className={styles.docLink}>{doc.title}</span>
                    )}
                    {doc.note && <span className={styles.note}>{doc.note}</span>}
                  </div>
                </li>
              ))}
            </ul>
          </section>
        ))}


      </div>
    </Layout>
  );
}
