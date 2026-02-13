/**
 * PopHubSection — Hub de gestão documental do módulo POP
 *
 * Exibido na landing de Mapeamento de Atividades.
 * Permite: criar novo POP, retomar draft, revisar publicado, ver versões.
 *
 * Consome: GET /api/pops/?mine=true
 * Trata: 401/403 (sessão expirada) → fallback "Entre para ver seus POPs"
 * Tolera: resposta como lista direta [] ou paginada { results: [] }
 */
import React, { useEffect, useState } from 'react';
import { Plus, FolderOpen, BookOpen, History, LogIn } from 'lucide-react';
import api from '../../services/api';
import styles from './PopHubSection.module.css';

interface POPResumo {
  id: number;
  uuid: string;
  codigo_processo: string;
  nome_processo: string;
  macroprocesso: string;
  area_nome: string;
  area_slug: string;
  status: 'draft' | 'published' | 'archived';
  versao: number;
  created_at: string;
  updated_at: string;
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

  useEffect(() => {
    let cancelled = false;

    async function carregarPops() {
      try {
        const resp = await api.get('/pops/', {
          params: { mine: 'true' },
        });
        if (!cancelled) {
          setPops(extrairLista(resp.data));
          setEstado('ok');
        }
      } catch (err: unknown) {
        if (cancelled) return;
        const status = (err as { response?: { status?: number } })?.response?.status;
        if (status === 401 || status === 403) {
          setEstado('nao_autenticado');
        } else {
          // Erro genérico (backend indisponível, 500, etc.)
          // Degrada silenciosamente: mostra seções vazias em vez de bloquear hub
          console.warn('[PopHubSection] Erro ao carregar POPs (degradando):', err);
          setEstado('ok');
        }
      }
    }

    carregarPops();
    return () => { cancelled = true; };
  }, []);

  const drafts = pops.filter((p) => p.status === 'draft');
  const published = pops.filter((p) => p.status === 'published');

  return (
    <section className={styles.hub}>
      <h2 className={styles.hubTitle}>Meus POPs</h2>

      {/* Criar novo — sempre visível */}
      <button type="button" className={styles.criarNovo} onClick={onCriarNovo}>
        <span className={styles.criarNovoIcone}>
          <Plus size={20} />
        </span>
        <div className={styles.criarNovoTexto}>
          <p className={styles.criarNovoLabel}>Criar novo POP</p>
          <p className={styles.criarNovoDesc}>Inicie um novo mapeamento de atividade</p>
        </div>
      </button>

      {/* Loading */}
      {estado === 'loading' && (
        <div className={styles.loading}>
          <div className={styles.skeleton} />
          <div className={styles.skeleton} />
        </div>
      )}

      {/* Não autenticado — fallback amigável */}
      {estado === 'nao_autenticado' && (
        <div className={styles.naoAutenticado}>
          <LogIn size={18} />
          <p>Entre na plataforma para visualizar seus POPs em andamento e consolidados.</p>
        </div>
      )}

      {/* Erro genérico */}
      {estado === 'erro' && (
        <p className={styles.erro}>Nao foi possivel carregar seus POPs.</p>
      )}

      {/* Em andamento */}
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
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Consolidados */}
      {estado === 'ok' && (
        <div className={styles.grupo}>
          <div className={styles.grupoHeader}>
            <BookOpen size={18} className={styles.grupoIcone} />
            <h3 className={styles.grupoTitulo}>Consolidados</h3>
            {published.length > 0 && (
              <span className={styles.grupoContagem}>{published.length}</span>
            )}
          </div>

          {published.length === 0 ? (
            <p className={styles.vazio}>Nenhum POP consolidado.</p>
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
                      Revisar
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
    </section>
  );
};

export default PopHubSection;
