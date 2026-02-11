/**
 * CatalogoPOPDetailPage — Visualizacao read-only de um POP publicado.
 * Rota: /catalogo/:slug/:codigo
 */
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import type { POPDetail, PopVersion } from '../services/catalogoApi';
import { obterPOPPorCodigo, listarVersoes, buildPdfUrl } from '../services/catalogoApi';
import './CatalogoPOPDetail.css';

const STATUS_LABELS: Record<string, string> = {
  published: 'Publicado',
  draft: 'Rascunho',
  archived: 'Arquivado',
};

interface Etapa {
  numero?: number;
  nome?: string;
  descricao?: string;
  responsavel?: string;
  prazo?: string;
  [key: string]: unknown;
}

export default function CatalogoPOPDetailPage() {
  const navigate = useNavigate();
  const { slug, codigo } = useParams<{ slug: string; codigo: string }>();
  const [pop, setPop] = useState<POPDetail | null>(null);
  const [versions, setVersions] = useState<PopVersion[]>([]);
  const [showVersions, setShowVersions] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug || !codigo) return;
    setLoading(true);
    setError(null);

    const fetchData = async () => {
      try {
        const popData = await obterPOPPorCodigo(slug, codigo);
        setPop(popData);
        if (popData.uuid) {
          const versionsData = await listarVersoes(popData.uuid);
          setVersions(versionsData);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro ao carregar POP.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [slug, codigo]);

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="pop-detail">
        <div className="pop-detail__loading">Carregando POP...</div>
      </div>
    );
  }

  if (error || !pop) {
    return (
      <div className="pop-detail">
        <div className="pop-detail__error">
          <p>{error || 'POP não encontrado.'}</p>
          <button onClick={() => navigate(slug ? `/catalogo/${slug}` : '/catalogo')}>
            Voltar
          </button>
        </div>
      </div>
    );
  }

  const etapas = (pop.etapas || []) as Etapa[];
  const currentVersion = versions.find((v) => v.is_current);

  return (
    <div className="pop-detail">
      {/* Header */}
      <header className="pop-detail__header">
        <div className="pop-detail__header-content">
          <a href="/" className="pop-detail__logo">MapaGov</a>
          <nav className="pop-detail__nav">
            <a href="/">Início</a>
            <a href="/catalogo">Catálogo</a>
          </nav>
        </div>
      </header>

      {/* Breadcrumb */}
      <div className="pop-detail__breadcrumb-bar">
        <div className="pop-detail__breadcrumb">
          <button onClick={() => navigate('/catalogo')} className="pop-detail__breadcrumb-link">
            Catálogo
          </button>
          <span className="pop-detail__breadcrumb-sep">/</span>
          <button
            onClick={() => navigate(`/catalogo/${slug}`)}
            className="pop-detail__breadcrumb-link"
          >
            {pop.area_detail?.nome_curto || slug}
          </button>
          <span className="pop-detail__breadcrumb-sep">/</span>
          <span className="pop-detail__breadcrumb-current">{pop.codigo_processo}</span>
        </div>
      </div>

      {/* Conteudo */}
      <div className="pop-detail__content">
        {/* Cabecalho do POP */}
        <div className="pop-detail__pop-header">
          <div className="pop-detail__pop-meta">
            <span className="pop-detail__pop-codigo">{pop.codigo_processo}</span>
            <span className={`pop-detail__pop-status pop-detail__pop-status--${pop.status}`}>
              {STATUS_LABELS[pop.status] || pop.status}
            </span>
            <span className="pop-detail__pop-version">v{pop.versao}</span>
            <a
              href={buildPdfUrl(slug!, pop.codigo_processo, currentVersion?.versao)}
              target="_blank"
              rel="noopener noreferrer"
              className="pop-detail__pdf-btn"
            >
              Baixar PDF
            </a>
          </div>
          <h1 className="pop-detail__pop-nome">{pop.nome_processo}</h1>
          {pop.macroprocesso && (
            <p className="pop-detail__pop-macro">Macroprocesso: {pop.macroprocesso}</p>
          )}
        </div>

        {/* Campos descritivos */}
        <div className="pop-detail__sections">
          {pop.objetivo && (
            <section className="pop-detail__section">
              <h2>Objetivo</h2>
              <p>{pop.objetivo}</p>
            </section>
          )}

          {pop.base_legal && (
            <section className="pop-detail__section">
              <h2>Base Legal</h2>
              <p>{pop.base_legal}</p>
            </section>
          )}

          {pop.documentos_entrada && (
            <section className="pop-detail__section">
              <h2>Documentos de Entrada</h2>
              <p>{pop.documentos_entrada}</p>
            </section>
          )}

          {pop.documentos_saida && (
            <section className="pop-detail__section">
              <h2>Documentos de Saída</h2>
              <p>{pop.documentos_saida}</p>
            </section>
          )}

          {pop.sistemas_utilizados && (
            <section className="pop-detail__section">
              <h2>Sistemas Utilizados</h2>
              <p>{pop.sistemas_utilizados}</p>
            </section>
          )}

          {/* Etapas */}
          {etapas.length > 0 && (
            <section className="pop-detail__section">
              <h2>Etapas do Procedimento</h2>
              <div className="pop-detail__etapas">
                {etapas.map((etapa, i) => (
                  <div key={i} className="pop-detail__etapa">
                    <div className="pop-detail__etapa-num">{etapa.numero || i + 1}</div>
                    <div className="pop-detail__etapa-body">
                      {etapa.nome && (
                        <h3 className="pop-detail__etapa-nome">{etapa.nome}</h3>
                      )}
                      {etapa.descricao && (
                        <p className="pop-detail__etapa-desc">{etapa.descricao}</p>
                      )}
                      {etapa.responsavel && (
                        <span className="pop-detail__etapa-resp">
                          Responsável: {etapa.responsavel}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {pop.observacoes && (
            <section className="pop-detail__section">
              <h2>Observações</h2>
              <p>{pop.observacoes}</p>
            </section>
          )}
        </div>

        {/* Rodape: versoes + metadados */}
        <div className="pop-detail__footer">
          <div className="pop-detail__footer-meta">
            <span>Criado em {formatDate(pop.created_at)}</span>
            <span>Atualizado em {formatDate(pop.updated_at)}</span>
            {pop.integrity_hash && (
              <span className="pop-detail__hash" title={pop.integrity_hash}>
                Hash: {pop.integrity_hash.substring(0, 12)}...
              </span>
            )}
          </div>

          {versions.length > 0 && (
            <div className="pop-detail__versions">
              <button
                className="pop-detail__versions-toggle"
                onClick={() => setShowVersions(!showVersions)}
              >
                {showVersions ? 'Ocultar' : 'Mostrar'} histórico de versões ({versions.length})
              </button>

              {showVersions && (
                <table className="pop-detail__versions-table">
                  <thead>
                    <tr>
                      <th>Versão</th>
                      <th>Publicado em</th>
                      <th>Por</th>
                      <th>Atual</th>
                    </tr>
                  </thead>
                  <tbody>
                    {versions.map((v) => (
                      <tr key={v.versao}>
                        <td>v{v.versao}</td>
                        <td>{formatDate(v.published_at)}</td>
                        <td>{v.published_by_name || '—'}</td>
                        <td>{v.is_current ? 'Sim' : '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
