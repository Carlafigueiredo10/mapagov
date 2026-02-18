import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import Layout from '../components/Layout/Layout';
import styles from './LegalPage.module.css';

const BASE = import.meta.env.BASE_URL;

const DOCS: Record<string, string> = {
  politica: `${BASE}legal/politica_privacidade.md`,
  termos: `${BASE}legal/termos_de_uso.md`,
};

export default function LegalPage() {
  const { doc } = useParams<{ doc: string }>();
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const path = doc ? DOCS[doc] : undefined;
    if (!path) {
      setContent('# Documento não encontrado');
      setLoading(false);
      return;
    }
    fetch(path)
      .then((r) => r.text())
      .then((text) => setContent(text))
      .catch(() => setContent('# Erro ao carregar o documento'))
      .finally(() => setLoading(false));
  }, [doc]);

  return (
    <Layout>
      <div className={styles.legalContainer}>
        {loading ? (
          <p className={styles.loading}>Carregando...</p>
        ) : (
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
        )}
      </div>
    </Layout>
  );
}
