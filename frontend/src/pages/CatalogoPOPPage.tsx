/**
 * CatalogoPOPPage — Grid de areas organizacionais com contagem de POPs.
 * Rota: /catalogo
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Area, StatsGlobal, POPListItem } from '../services/catalogoApi';
import { listarAreas, obterStatsGlobal, buscarPOPs } from '../services/catalogoApi';
import './CatalogoPOP.css';

export default function CatalogoPOPPage() {
  const navigate = useNavigate();
  const [areas, setAreas] = useState<Area[]>([]);
  const [stats, setStats] = useState<StatsGlobal | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<POPListItem[] | null>(null);
  const [searching, setSearching] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [areasData, statsData] = await Promise.all([
          listarAreas(),
          obterStatsGlobal(),
        ]);
        setAreas(areasData);
        setStats(statsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro ao carregar dados.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const doSearch = useCallback(async (q: string) => {
    if (q.length < 3) {
      setSearchResults(null);
      setSearching(false);
      return;
    }
    setSearching(true);
    try {
      const results = await buscarPOPs({ q, limit: 20 });
      setSearchResults(results);
    } catch {
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  }, []);

  const handleSearchChange = (value: string) => {
    setSearchQuery(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (value.length < 3) {
      setSearchResults(null);
      return;
    }
    debounceRef.current = setTimeout(() => doSearch(value), 300);
  };

  if (loading) {
    return (
      <div className="catalogo-page">
        <div className="catalogo-page__loading">Carregando catálogo...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="catalogo-page">
        <div className="catalogo-page__error">
          <p>Erro: {error}</p>
          <button onClick={() => window.location.reload()}>Tentar novamente</button>
        </div>
      </div>
    );
  }

  return (
    <div className="catalogo-page">
      {/* Header */}
      <header className="catalogo-page__header">
        <div className="catalogo-page__header-content">
          <a href="/" className="catalogo-page__logo">MapaGov</a>
          <nav className="catalogo-page__nav">
            <a href="/">Início</a>
            <a href="/portal">Portal</a>
          </nav>
        </div>
      </header>

      {/* Titulo + resumo */}
      <div className="catalogo-page__hero">
        <h1>Catálogo de Procedimentos Operacionais</h1>
        <p className="catalogo-page__subtitle">
          Acervo organizado de POPs por área organizacional
        </p>

        {/* Search */}
        <div className="catalogo-page__search">
          <input
            type="text"
            className="catalogo-page__search-input"
            placeholder="Buscar POP por nome, código ou macroprocesso..."
            value={searchQuery}
            onChange={(e) => handleSearchChange(e.target.value)}
          />
          {searchQuery.length > 0 && searchQuery.length < 3 && (
            <span className="catalogo-page__search-hint">Digite ao menos 3 caracteres</span>
          )}
        </div>

        {stats && !searchResults && (
          <div className="catalogo-page__stats-bar">
            <div className="catalogo-page__stat">
              <span className="catalogo-page__stat-value">{stats.totais.publicados}</span>
              <span className="catalogo-page__stat-label">Publicados</span>
            </div>
            <div className="catalogo-page__stat">
              <span className="catalogo-page__stat-value">{stats.totais.areas}</span>
              <span className="catalogo-page__stat-label">Áreas</span>
            </div>
            <div className="catalogo-page__stat">
              <span className="catalogo-page__stat-value">{stats.totais.versoes}</span>
              <span className="catalogo-page__stat-label">Versões</span>
            </div>
            <div className="catalogo-page__stat">
              <span className="catalogo-page__stat-value">{stats.atividade_30d.publicacoes}</span>
              <span className="catalogo-page__stat-label">Publicações (30d)</span>
            </div>
          </div>
        )}
      </div>

      {/* Search results */}
      {searchResults !== null ? (
        <div className="catalogo-page__content">
          <div className="catalogo-page__search-header">
            <span className="catalogo-page__search-count">
              {searching ? 'Buscando...' : `${searchResults.length} resultado${searchResults.length !== 1 ? 's' : ''}`}
            </span>
            <button
              className="catalogo-page__search-clear"
              onClick={() => { setSearchQuery(''); setSearchResults(null); }}
            >
              Limpar busca
            </button>
          </div>

          {searchResults.length === 0 && !searching ? (
            <div className="catalogo-page__search-empty">
              Nenhum POP publicado encontrado para "{searchQuery}".
            </div>
          ) : (
            <div className="catalogo-page__search-results">
              {searchResults.map((pop) => (
                <div
                  key={pop.uuid}
                  className="catalogo-page__search-item"
                  onClick={() => navigate(`/catalogo/${pop.area_slug}/${pop.codigo_processo}`)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => e.key === 'Enter' && navigate(`/catalogo/${pop.area_slug}/${pop.codigo_processo}`)}
                >
                  <div className="catalogo-page__search-item-top">
                    <span className="catalogo-page__search-item-codigo">{pop.codigo_processo}</span>
                    <span className="catalogo-page__search-item-area">{pop.area_nome}</span>
                    <span className="catalogo-page__search-item-version">v{pop.versao}</span>
                  </div>
                  <div className="catalogo-page__search-item-nome">{pop.nome_processo}</div>
                  {pop.macroprocesso && (
                    <div className="catalogo-page__search-item-macro">{pop.macroprocesso}</div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        /* Grid de areas */
        <div className="catalogo-page__content">
          <div className="catalogo-page__grid">
            {areas.map((area) => (
              <div
                key={area.id}
                className="catalogo-page__area-card"
                onClick={() => navigate(`/catalogo/${area.slug}`)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && navigate(`/catalogo/${area.slug}`)}
              >
                <div className="catalogo-page__area-card-header">
                  <span className="catalogo-page__area-codigo">{area.codigo}</span>
                  <span className="catalogo-page__area-count">
                    {area.pop_count} {area.pop_count === 1 ? 'POP' : 'POPs'}
                  </span>
                </div>
                <h2 className="catalogo-page__area-nome">{area.nome_curto}</h2>
                {area.descricao && (
                  <p className="catalogo-page__area-desc">{area.descricao}</p>
                )}
                {area.tem_subareas && area.subareas.length > 0 && (
                  <div className="catalogo-page__subareas">
                    {area.subareas.map((sub) => (
                      <span key={sub.id} className="catalogo-page__subarea-tag">
                        {sub.nome_curto} ({sub.pop_count})
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
