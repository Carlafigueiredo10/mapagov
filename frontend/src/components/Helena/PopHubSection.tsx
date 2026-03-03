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
import { Plus, FolderOpen, BookOpen, Clock, History, LogIn, CheckCircle, XCircle } from 'lucide-react';
import api from '../../services/api';
import { useAuthStore } from '../../store/authStore';
import { hasRole } from '../../services/authApi';
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
  onVerVersoes: (uuid: string) => void;
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
  onVerVersoes,
}) => {
  const [pops, setPops] = useState<POPResumo[]>([]);
  const [estado, setEstado] = useState<HubEstado>('loading');
  const [rejectModal, setRejectModal] = useState<{ uuid: string; nome: string } | null>(null);
  const [rejectMotivo, setRejectMotivo] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

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

  const handleHomologar = async (uuid: string) => {
    if (actionLoading) return;
    setActionLoading(true);
    try {
      await api.post(`/pops/${uuid}/homologar/`);
      await carregarPops();
    } catch (err) {
      console.error('[PopHubSection] Erro ao homologar:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleRejeitar = async () => {
    if (!rejectModal || actionLoading) return;
    const motivo = rejectMotivo.trim();
    if (!motivo) return;
    setActionLoading(true);
    try {
      await api.post(`/pops/${rejectModal.uuid}/reject-review/`, { motivo });
      setRejectModal(null);
      setRejectMotivo('');
      await carregarPops();
    } catch (err) {
      console.error('[PopHubSection] Erro ao rejeitar:', err);
    } finally {
      setActionLoading(false);
    }
  };

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

  const drafts = pops.filter((p) => p.status === 'draft');
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
                      Abrir para revisao
                    </button>
                    {isGestor && (
                      <>
                        <button
                          type="button"
                          className={`${styles.btnAcao} ${styles.btnHomologar}`}
                          onClick={() => handleHomologar(pop.uuid)}
                          disabled={actionLoading}
                        >
                          <CheckCircle size={14} style={{ marginRight: 4, verticalAlign: 'middle' }} />
                          Homologar
                        </button>
                        <button
                          type="button"
                          className={`${styles.btnAcao} ${styles.btnRejeitar}`}
                          onClick={() => setRejectModal({ uuid: pop.uuid, nome: pop.nome_processo || 'POP sem nome' })}
                          disabled={actionLoading}
                        >
                          <XCircle size={14} style={{ marginRight: 4, verticalAlign: 'middle' }} />
                          Rejeitar
                        </button>
                      </>
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
                      Ver
                    </button>
                    <button
                      type="button"
                      className={`${styles.btnAcao} ${styles.btnAcaoSecundario}`}
                      onClick={() => onVerVersoes(pop.uuid)}
                    >
                      <History size={14} style={{ marginRight: 4, verticalAlign: 'middle' }} />
                      Versoes
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Modal de rejeicao */}
      {rejectModal && (
        <div className={styles.modalOverlay} onClick={() => { setRejectModal(null); setRejectMotivo(''); }}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <h3 className={styles.modalTitulo}>Rejeitar revisao</h3>
            <p className={styles.modalDesc}>
              POP: <strong>{rejectModal.nome}</strong>
            </p>
            <label className={styles.modalLabel}>
              Motivo (obrigatorio):
              <textarea
                className={styles.modalTextarea}
                value={rejectMotivo}
                onChange={(e) => setRejectMotivo(e.target.value)}
                rows={3}
                placeholder="Descreva o motivo da rejeicao..."
              />
            </label>
            <div className={styles.modalBotoes}>
              <button
                type="button"
                className={styles.btnAcaoSecundario}
                onClick={() => { setRejectModal(null); setRejectMotivo(''); }}
              >
                Cancelar
              </button>
              <button
                type="button"
                className={styles.btnRejeitar}
                onClick={handleRejeitar}
                disabled={!rejectMotivo.trim() || actionLoading}
              >
                Confirmar rejeicao
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};

export default PopHubSection;
