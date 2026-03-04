/**
 * PopHubSection — Hub de gestao documental do modulo POP
 *
 * Exibido na landing de Mapeamento de Atividades.
 * Permite: criar novo POP, retomar draft, submeter para revisao,
 *          revisar in_review, homologar/rejeitar (gestor), ver publicados.
 *
 * Consome: GET /api/pops/?mine=true + GET /api/pops/?review_queue=true
 * Trata: 401/403 (sessao expirada) -> fallback "Entre para ver seus POPs"
 * Tolera: resposta como lista direta [] ou paginada { results: [] }
 */
import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Copy, FolderOpen, BookOpen, Clock, LogIn, CheckCircle } from 'lucide-react';
import api from '../../services/api';
import { useAuthStore } from '../../store/authStore';
import { hasRole } from '../../services/authApi';
import { resolveCAP, clonePOP } from '../../services/helenaApi';
import { buscarPOPs } from '../../services/catalogoApi';
import styles from './PopHubSection.module.css';

interface POPResumo {
  id: number;
  uuid: string;
  codigo_processo: string;
  nome_processo: string;
  macroprocesso: string;
  area_nome: string;
  area_slug: string;
  status: 'draft' | 'in_review' | 'published' | 'archived';
  versao: number;
  created_at: string;
  updated_at: string;
  submitted_for_review_at: string | null;
}

interface PopHubSectionProps {
  onCriarNovo: () => void;
  onRetomar: (uuid: string) => void;
  onRevisar: (uuid: string) => void;
  onClonar: (popData: Record<string, unknown>) => void;
}

/** Extrai lista de POPs independente do shape (array direto ou { results: [] }) */
function extrairLista(data: unknown): POPResumo[] {
  if (Array.isArray(data)) return data;
  if (data && typeof data === 'object' && 'results' in data && Array.isArray((data as { results: unknown[] }).results)) {
    return (data as { results: POPResumo[] }).results;
  }
  return [];
}

/** Dedup por uuid: preferir objeto com submitted_for_review_at presente */
function deduplicarPops(lista: POPResumo[]): POPResumo[] {
  const mapa = new Map<string, POPResumo>();
  for (const pop of lista) {
    const existente = mapa.get(pop.uuid);
    if (!existente) {
      mapa.set(pop.uuid, pop);
    } else if (pop.submitted_for_review_at && !existente.submitted_for_review_at) {
      mapa.set(pop.uuid, pop);
    }
  }
  return Array.from(mapa.values());
}

function formatarData(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  } catch {
    return iso;
  }
}

type HubEstado = 'loading' | 'ok' | 'nao_autenticado' | 'erro';

const PopHubSection: React.FC<PopHubSectionProps> = ({
  onCriarNovo,
  onRetomar,
  onRevisar,
  onClonar,
}) => {
  const [pops, setPops] = useState<POPResumo[]>([]);
  const [estado, setEstado] = useState<HubEstado>('loading');
  const [actionLoading, setActionLoading] = useState(false);

  // Clone state
  const [cloneMode, setCloneMode] = useState(false);
  const [cloneCap, setCloneCap] = useState('');
  const [cloneAtividade, setCloneAtividade] = useState('');
  const [cloneSearchResult, setCloneSearchResult] = useState<{
    uuid: string; nome_processo: string; status: string; cap: string;
    area_id: number | null; area_nome: string;
  } | null>(null);
  const [cloneNameResults, setCloneNameResults] = useState<{ uuid: string; codigo_processo: string; nome_processo: string; area_nome: string }[]>([]);
  const [cloneLoading, setCloneLoading] = useState(false);
  const [cloneError, setCloneError] = useState('');

  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const isGestor = hasRole(user, 'area_manager') || (user?.is_superuser ?? false);

  const carregarPops = useCallback(async () => {
    if (!user) {
      setEstado('nao_autenticado');
      return;
    }
    try {
      // Chamada 1: meus POPs (todos os status)
      const mineResp = await api.get('/pops/', { params: { mine: 'true' } });
      const meusPops = extrairLista(mineResp.data);

      // Chamada 2: fila de revisao do setor (se usuario tem area)
      let filaPops: POPResumo[] = [];
      if (user?.area) {
        try {
          const queueResp = await api.get('/pops/', { params: { review_queue: 'true' } });
          filaPops = extrairLista(queueResp.data);
        } catch {
          // Falha silenciosa — nao bloqueia hub
          console.warn('[PopHubSection] Falha ao carregar fila de revisao');
        }
      }

      setPops(deduplicarPops([...meusPops, ...filaPops]));
      setEstado('ok');
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      if (status === 401 || status === 403) {
        setEstado('nao_autenticado');
      } else {
        console.warn('[PopHubSection] Erro ao carregar POPs (degradando):', err);
        setEstado('ok');
      }
    }
  }, [user]);

  useEffect(() => {
    let cancelled = false;
    carregarPops().then(() => { if (cancelled) return; });
    return () => { cancelled = true; };
  }, [carregarPops]);

  const handleSubmitReview = async (uuid: string) => {
    if (actionLoading) return;
    setActionLoading(true);
    try {
      await api.post(`/pops/${uuid}/submit-review/`);
      await carregarPops();
    } catch (err) {
      console.error('[PopHubSection] Erro ao submeter para revisao:', err);
    } finally {
      setActionLoading(false);
    }
  };

  // ----- Clone handlers -----

  const CAP_REGEX = /^\d+\.\d+\.\d+(\.\d+)?$/;

  const handleCloneSearch = async () => {
    const query = cloneCap.trim();
    if (cloneLoading || query.length < 3) return;
    setCloneLoading(true);
    setCloneError('');
    setCloneSearchResult(null);
    setCloneNameResults([]);

    // Auto-detect: CAP pattern → resolveCAP; else → name search
    if (CAP_REGEX.test(query)) {
      try {
        const result = await resolveCAP(query);
        if (!result) {
          setCloneError('Codigo CAP nao encontrado.');
          return;
        }
        if (result.status !== 'published' && result.status !== 'in_review') {
          setCloneError(`POP encontrado mas com status "${result.status}". Somente POPs publicados ou em revisao podem ser clonados.`);
          return;
        }
        const userAreaId = user?.area;
        if (!user?.is_superuser && userAreaId && result.area_id && userAreaId !== result.area_id) {
          setCloneError('Voce so pode clonar POPs do seu setor.');
          return;
        }
        setCloneSearchResult(result);
      } catch {
        setCloneError('Codigo CAP nao encontrado.');
      } finally {
        setCloneLoading(false);
      }
    } else {
      // Name search
      try {
        const results = await buscarPOPs({ q: query, status: 'published', limit: 10 });
        if (results.length === 0) {
          setCloneError('Nenhum POP publicado encontrado.');
        } else {
          setCloneNameResults(results.map((r) => ({
            uuid: r.uuid,
            codigo_processo: r.codigo_processo,
            nome_processo: r.nome_processo,
            area_nome: r.area_nome,
          })));
        }
      } catch {
        setCloneError('Erro ao buscar POPs.');
      } finally {
        setCloneLoading(false);
      }
    }
  };

  const handleCloneSelectFromList = async (item: { codigo_processo: string }) => {
    setCloneCap(item.codigo_processo);
    setCloneNameResults([]);
    setCloneLoading(true);
    setCloneError('');
    try {
      const result = await resolveCAP(item.codigo_processo);
      if (!result) {
        setCloneError('Codigo CAP nao encontrado.');
        return;
      }
      setCloneSearchResult(result);
    } catch {
      setCloneError('Erro ao resolver codigo CAP.');
    } finally {
      setCloneLoading(false);
    }
  };

  const handleCloneConfirm = async () => {
    if (!cloneSearchResult || cloneLoading) return;
    const atividade = cloneAtividade.trim();
    if (atividade.length < 5) return;
    setCloneLoading(true);
    setCloneError('');
    try {
      const result = await clonePOP(cloneSearchResult.uuid, atividade);
      if (result.success && result.pop) {
        onClonar(result.pop);
        setCloneMode(false);
        setCloneCap('');
        setCloneAtividade('');
        setCloneSearchResult(null);
      } else {
        setCloneError(result.error || 'Erro ao clonar POP.');
      }
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { error?: string } } };
      setCloneError(axiosErr?.response?.data?.error || 'Erro inesperado ao clonar.');
    } finally {
      setCloneLoading(false);
    }
  };

  const drafts = pops.filter((p) => p.status === 'draft' && p.codigo_processo);
  const inReview = pops.filter((p) => p.status === 'in_review');
  const published = pops.filter((p) => p.status === 'published');

  return (
    <section className={styles.hub}>
      <h2 className={styles.hubTitle}>Meus POPs</h2>

      {/* Criar novo — exige autenticação */}
      {user ? (
        <button type="button" className={styles.criarNovo} onClick={onCriarNovo}>
          <span className={styles.criarNovoIcone}>
            <Plus size={20} />
          </span>
          <div className={styles.criarNovoTexto}>
            <p className={styles.criarNovoLabel}>Criar novo POP</p>
            <p className={styles.criarNovoDesc}>Inicie um novo mapeamento de atividade</p>
          </div>
        </button>
      ) : (
        <div className={styles.naoAutenticado}>
          <LogIn size={18} />
          <p>Faça login para criar e gerenciar seus POPs.</p>
        </div>
      )}

      {/* Clonar POP existente */}
      {user && (
        <>
          <button
            type="button"
            className={styles.criarNovo}
            onClick={() => {
              setCloneMode(!cloneMode);
              setCloneError('');
              setCloneSearchResult(null);
              setCloneNameResults([]);
              setCloneCap('');
              setCloneAtividade('');
            }}
          >
            <span className={styles.criarNovoIcone}>
              <Copy size={20} />
            </span>
            <div className={styles.criarNovoTexto}>
              <p className={styles.criarNovoLabel}>Clonar POP existente</p>
              <p className={styles.criarNovoDesc}>Busque por codigo CAP ou nome da atividade</p>
            </div>
          </button>

          {cloneMode && (
            <div className={styles.cloneForm}>
              {/* Busca por CAP */}
              <div className={styles.cloneSearchRow}>
                <input
                  type="text"
                  placeholder="Codigo CAP ou nome da atividade"
                  value={cloneCap}
                  onChange={(e) => setCloneCap(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter') handleCloneSearch(); }}
                  className={styles.cloneInput}
                />
                <button
                  type="button"
                  className={styles.btnBuscar}
                  onClick={handleCloneSearch}
                  disabled={cloneLoading || cloneCap.trim().length < 3}
                >
                  {cloneLoading ? 'Buscando...' : 'Buscar'}
                </button>
              </div>

              {/* Resultados de busca por nome */}
              {cloneNameResults.length > 0 && (
                <div className={styles.cloneResults}>
                  <p className={styles.cloneResultInfo}>Selecione o POP para clonar:</p>
                  {cloneNameResults.map((item) => (
                    <button
                      key={item.uuid}
                      type="button"
                      className={styles.cloneResultItem}
                      onClick={() => handleCloneSelectFromList(item)}
                    >
                      <span className={styles.cloneResultItemCap}>{item.codigo_processo}</span>
                      <span className={styles.cloneResultItemNome}>{item.nome_processo}</span>
                      {item.area_nome && <span className={styles.cloneResultItemArea}>{item.area_nome}</span>}
                    </button>
                  ))}
                </div>
              )}

              {/* Resultado da busca por CAP */}
              {cloneSearchResult && (
                <div className={styles.cloneResult}>
                  <p className={styles.cloneResultInfo}>
                    POP encontrado: <strong>{cloneSearchResult.nome_processo}</strong>
                  </p>
                  <p className={styles.cloneResultMeta}>
                    CAP: {cloneSearchResult.cap}
                    {cloneSearchResult.area_nome && ` | Area: ${cloneSearchResult.area_nome}`}
                    {` | Status: ${cloneSearchResult.status}`}
                  </p>

                  <input
                    type="text"
                    placeholder="Nome da nova atividade"
                    value={cloneAtividade}
                    onChange={(e) => setCloneAtividade(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter' && cloneAtividade.trim().length >= 5) handleCloneConfirm(); }}
                    className={styles.cloneInput}
                  />
                  <p className={styles.cloneNota}>
                    O nome da atividade definira o CAP e nao podera ser alterado depois.
                  </p>

                  <button
                    type="button"
                    className={styles.btnClonar}
                    onClick={handleCloneConfirm}
                    disabled={cloneLoading || cloneAtividade.trim().length < 5}
                  >
                    {cloneLoading ? 'Clonando...' : 'Clonar'}
                  </button>
                </div>
              )}

              {cloneError && <p className={styles.erro}>{cloneError}</p>}
            </div>
          )}
        </>
      )}

      {/* Loading */}
      {estado === 'loading' && (
        <div className={styles.loading}>
          <div className={styles.skeleton} />
          <div className={styles.skeleton} />
        </div>
      )}

      {/* Nao autenticado — fallback amigavel */}
      {estado === 'nao_autenticado' && (
        <div className={styles.naoAutenticado}>
          <LogIn size={18} />
          <p>Entre na plataforma para visualizar seus POPs.</p>
        </div>
      )}

      {/* Erro generico */}
      {estado === 'erro' && (
        <p className={styles.erro}>Nao foi possivel carregar seus POPs.</p>
      )}

      {/* Em andamento (draft) */}
      {estado === 'ok' && (
        <div className={styles.grupo}>
          <div className={styles.grupoHeader}>
            <FolderOpen size={18} className={styles.grupoIcone} />
            <h3 className={styles.grupoTitulo}>Em andamento</h3>
            {drafts.length > 0 && (
              <span className={styles.grupoContagem}>{drafts.length}</span>
            )}
          </div>

          {drafts.length === 0 ? (
            <p className={styles.vazio}>Nenhum POP em andamento.</p>
          ) : (
            <div className={styles.lista}>
              {drafts.map((pop) => (
                <div key={pop.uuid} className={styles.popCard}>
                  <div className={styles.popInfo}>
                    <p className={styles.popNome}>
                      {pop.codigo_processo && <span className={styles.popCap}>{pop.codigo_processo}</span>}
                      {pop.nome_processo || 'POP sem nome'}
                    </p>
                    <p className={styles.popMeta}>
                      {pop.area_nome && (
                        <>
                          <span>{pop.area_nome}</span>
                          <span className={styles.popSeparador}>|</span>
                        </>
                      )}
                      <span>Ultima edicao: {formatarData(pop.updated_at)}</span>
                      <span className={styles.popSeparador}>|</span>
                      <span className={`${styles.badgeStatus} ${styles.badgeDraft}`}>
                        Rascunho
                      </span>
                    </p>
                  </div>
                  <div className={styles.popAcoes}>
                    <button
                      type="button"
                      className={styles.btnAcao}
                      onClick={() => onRetomar(pop.uuid)}
                    >
                      Retomar
                    </button>
                    {pop.nome_processo && (
                      <button
                        type="button"
                        className={`${styles.btnAcao} ${styles.btnAcaoSecundario}`}
                        onClick={() => handleSubmitReview(pop.uuid)}
                        disabled={actionLoading}
                      >
                        Submeter p/ revisao
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Aguardando Homologacao (in_review) */}
      {estado === 'ok' && (
        <div className={styles.grupo}>
          <div className={styles.grupoHeader}>
            <Clock size={18} className={styles.grupoIcone} />
            <h3 className={styles.grupoTitulo}>Aguardando Homologacao</h3>
            {inReview.length > 0 && (
              <span className={styles.grupoContagem}>{inReview.length}</span>
            )}
          </div>

          {inReview.length === 0 ? (
            <p className={styles.vazio}>Nenhum POP aguardando homologacao.</p>
          ) : (
            <div className={styles.lista}>
              {inReview.map((pop) => (
                <div key={pop.uuid} className={styles.popCard}>
                  <div className={styles.popInfo}>
                    <p className={styles.popNome}>
                      {pop.codigo_processo && <span className={styles.popCap}>{pop.codigo_processo}</span>}
                      {pop.nome_processo || 'POP sem nome'}
                    </p>
                    <p className={styles.popMeta}>
                      {pop.area_nome && (
                        <>
                          <span>{pop.area_nome}</span>
                          <span className={styles.popSeparador}>|</span>
                        </>
                      )}
                      {pop.submitted_for_review_at && (
                        <>
                          <span>Submetido em {formatarData(pop.submitted_for_review_at)}</span>
                          <span className={styles.popSeparador}>|</span>
                        </>
                      )}
                      <span className={`${styles.badgeStatus} ${styles.badgeInReview}`}>
                        Em Revisao
                      </span>
                    </p>
                  </div>
                  <div className={styles.popAcoes}>
                    <button
                      type="button"
                      className={styles.btnAcao}
                      onClick={() => onRetomar(pop.uuid)}
                    >
                      Retomar
                    </button>
                    {isGestor && pop.area_slug && pop.codigo_processo && (
                      <button
                        type="button"
                        className={`${styles.btnAcao} ${styles.btnHomologar}`}
                        onClick={() => navigate(`/catalogo/${pop.area_slug}/${pop.codigo_processo}?review=true`)}
                      >
                        <CheckCircle size={14} style={{ marginRight: 4, verticalAlign: 'middle' }} />
                        Verificar para homologacao
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Publicados */}
      {estado === 'ok' && (
        <div className={styles.grupo}>
          <div className={styles.grupoHeader}>
            <BookOpen size={18} className={styles.grupoIcone} />
            <h3 className={styles.grupoTitulo}>Publicados</h3>
            {published.length > 0 && (
              <span className={styles.grupoContagem}>{published.length}</span>
            )}
          </div>

          {published.length === 0 ? (
            <p className={styles.vazio}>Nenhum POP publicado.</p>
          ) : (
            <div className={styles.lista}>
              {published.map((pop) => (
                <div key={pop.uuid} className={styles.popCard}>
                  <div className={styles.popInfo}>
                    <p className={styles.popNome}>
                      {pop.codigo_processo && <span className={styles.popCap}>{pop.codigo_processo}</span>}
                      {pop.nome_processo || 'POP sem nome'}
                    </p>
                    <p className={styles.popMeta}>
                      {pop.area_nome && (
                        <>
                          <span>{pop.area_nome}</span>
                          <span className={styles.popSeparador}>|</span>
                        </>
                      )}
                      <span>v{pop.versao}</span>
                      <span className={styles.popSeparador}>|</span>
                      <span>Atualizado em {formatarData(pop.updated_at)}</span>
                      <span className={styles.popSeparador}>|</span>
                      <span className={`${styles.badgeStatus} ${styles.badgePublished}`}>
                        Publicado
                      </span>
                    </p>
                  </div>
                  <div className={styles.popAcoes}>
                    <button
                      type="button"
                      className={styles.btnAcao}
                      onClick={() => onRevisar(pop.uuid)}
                    >
                      Revisar
                    </button>
                    {pop.area_slug && pop.codigo_processo ? (
                      <button
                        type="button"
                        className={`${styles.btnAcao} ${styles.btnAcaoSecundario}`}
                        onClick={() => navigate(`/catalogo/${pop.area_slug}/${pop.codigo_processo}`)}
                      >
                        Ver
                      </button>
                    ) : (
                      <span title="POP sem codigo para abrir no catalogo">
                        <button
                          type="button"
                          className={`${styles.btnAcao} ${styles.btnAcaoSecundario}`}
                          disabled
                          aria-label="POP sem codigo para abrir no catalogo"
                        >
                          Ver
                        </button>
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Link para catalogo completo */}
      {estado === 'ok' && user && (
        <div className={styles.catalogoLink}>
          <BookOpen size={16} />
          <button
            type="button"
            className={styles.catalogoLinkBtn}
            onClick={() => navigate('/catalogo')}
          >
            Ver catalogo completo de POPs
          </button>
        </div>
      )}

    </section>
  );
};

export default PopHubSection;
