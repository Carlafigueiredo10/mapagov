/**
 * CatalogoAreaPage — Lista de POPs de uma area organizacional.
 * Rota: /catalogo/:slug
 */
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import type { Area, POPListItem } from '../services/catalogoApi';
import { obterArea, listarPOPsPorArea } from '../services/catalogoApi';
import './CatalogoArea.css';

const STATUS_LABELS: Record<string, string> = {
  published: 'Publicado',
  draft: 'Rascunho',
  archived: 'Arquivado',
};

const STATUS_CLASSES: Record<string, string> = {
  published: 'cat-area__badge--published',
  draft: 'cat-area__badge--draft',
  archived: 'cat-area__badge--archived',
};

export default function CatalogoAreaPage() {
  const navigate = useNavigate();
  const { slug } = useParams<{ slug: string }>();
  const [area, setArea] = useState<Area | null>(null);
  const [pops, setPops] = useState<POPListItem[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('published');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    setError(null);

    const fetchData = async () => {
      try {
        const [areaData, popsData] = await Promise.all([
          obterArea(slug),
          listarPOPsPorArea(slug, { status: statusFilter }),
        ]);
        setArea(areaData);
        setPops(popsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro ao carregar área.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [slug, statusFilter]);

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="cat-area">
        <div className="cat-area__loading">Carregando...</div>
      </div>
    );
  }

  if (error || !area) {
    return (
      <div className="cat-area">
        <div className="cat-area__error">
          <p>{error || 'Área não encontrada.'}</p>
          <button onClick={() => navigate('/catalogo')}>Voltar ao catálogo</button>
        </div>
      </div>
    );
  }

  return (
    <div className="cat-area">
      {/* Header */}
      <header className="cat-area__header">
        <div className="cat-area__header-content">
          <a href="/" className="cat-area__logo">MapaGov</a>
          <nav className="cat-area__nav">
            <a href="/">Início</a>
            <a href="/catalogo">Catálogo</a>
          </nav>
        </div>
      </header>

      {/* Breadcrumb */}
      <div className="cat-area__breadcrumb-bar">
        <div className="cat-area__breadcrumb">
          <button onClick={() => navigate('/catalogo')} className="cat-area__breadcrumb-link">
            Catálogo
          </button>
          <span className="cat-area__breadcrumb-sep">/</span>
          <span className="cat-area__breadcrumb-current">{area.nome_curto}</span>
        </div>
      </div>

      {/* Area info */}
      <div className="cat-area__info">
        <div className="cat-area__info-content">
          <div>
            <span className="cat-area__info-codigo">{area.codigo}</span>
            <h1 className="cat-area__info-nome">{area.nome}</h1>
            {area.descricao && (
              <p className="cat-area__info-desc">{area.descricao}</p>
            )}
          </div>
          <div className="cat-area__info-stats">
            <span className="cat-area__info-stat-value">{area.pop_count}</span>
            <span className="cat-area__info-stat-label">POPs publicados</span>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="cat-area__content">
        {/* Filtros */}
        <div className="cat-area__toolbar">
          <div className="cat-area__filters">
            {['published', 'draft', 'archived'].map((s) => (
              <button
                key={s}
                className={`cat-area__filter-btn ${statusFilter === s ? 'cat-area__filter-btn--active' : ''}`}
                onClick={() => setStatusFilter(s)}
              >
                {STATUS_LABELS[s]}
              </button>
            ))}
          </div>
          <span className="cat-area__result-count">
            {pops.length} {pops.length === 1 ? 'resultado' : 'resultados'}
          </span>
        </div>

        {/* Tabela */}
        {pops.length === 0 ? (
          <div className="cat-area__empty">
            Nenhum POP com status "{STATUS_LABELS[statusFilter]}" nesta área.
          </div>
        ) : (
          <table className="cat-area__table">
            <thead>
              <tr>
                <th>Código</th>
                <th>Processo</th>
                <th>Macroprocesso</th>
                <th>Status</th>
                <th>Versão</th>
                <th>Atualizado</th>
              </tr>
            </thead>
            <tbody>
              {pops.map((pop) => (
                <tr
                  key={pop.uuid}
                  onClick={() => navigate(`/catalogo/${slug}/${pop.codigo_processo}`)}
                  className="cat-area__table-row"
                >
                  <td className="cat-area__table-codigo">{pop.codigo_processo}</td>
                  <td>{pop.nome_processo}</td>
                  <td className="cat-area__table-macro">{pop.macroprocesso || '—'}</td>
                  <td>
                    <span className={`cat-area__badge ${STATUS_CLASSES[pop.status] || ''}`}>
                      {STATUS_LABELS[pop.status] || pop.status}
                    </span>
                  </td>
                  <td className="cat-area__table-center">v{pop.versao}</td>
                  <td className="cat-area__table-date">{formatDate(pop.updated_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {/* Subareas */}
        {area.tem_subareas && area.subareas.length > 0 && (
          <div className="cat-area__subareas-section">
            <h3>Sub-áreas</h3>
            <div className="cat-area__subareas-grid">
              {area.subareas.map((sub) => (
                <div
                  key={sub.id}
                  className="cat-area__subarea-card"
                  onClick={() => navigate(`/catalogo/${sub.slug}`)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => e.key === 'Enter' && navigate(`/catalogo/${sub.slug}`)}
                >
                  <span className="cat-area__subarea-codigo">{sub.codigo}</span>
                  <span className="cat-area__subarea-nome">{sub.nome_curto}</span>
                  <span className="cat-area__subarea-count">{sub.pop_count} POPs</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
