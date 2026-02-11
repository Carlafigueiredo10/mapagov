import api from './api';

// ============================================================================
// Types — espelham os serializers do backend (catalogo_serializers.py)
// ============================================================================

export interface AreaSubarea {
  id: number;
  codigo: string;
  nome: string;
  nome_curto: string;
  slug: string;
  pop_count: number;
}

export interface Area {
  id: number;
  codigo: string;
  nome: string;
  nome_curto: string;
  slug: string;
  prefixo: string;
  ordem: number;
  ativo: boolean;
  descricao: string;
  area_pai: number | null;
  tem_subareas: boolean;
  pop_count: number;
  subareas: AreaSubarea[];
}

export interface POPListItem {
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

export interface POPDetail extends POPListItem {
  area_detail: Area | null;
  session_id: string;
  area_codigo: string;
  objetivo: string;
  base_legal: string;
  documentos_entrada: string;
  documentos_saida: string;
  sistemas_utilizados: string;
  observacoes: string;
  etapas: unknown[];
  fluxos_entrada: unknown[];
  fluxos_saida: unknown[];
  dados_complementares: Record<string, unknown>;
  integrity_hash: string;
}

export interface PopVersion {
  versao: number;
  published_at: string;
  motivo: string;
  is_current: boolean;
  integrity_hash: string;
  published_by_name: string;
}

export interface StatsGlobal {
  totais: {
    pops: number;
    publicados: number;
    rascunhos: number;
    arquivados: number;
    versoes: number;
    areas: number;
  };
  atividade_30d: {
    pops_criados: number;
    publicacoes: number;
  };
  areas_ranking: Array<{
    codigo: string;
    nome_curto: string;
    pop_count: number;
  }>;
}

export interface StatsArea {
  area: {
    codigo: string;
    nome: string;
    slug: string;
  };
  totais: {
    pops: number;
    por_status: Record<string, number>;
  };
}

export interface ResolveResult {
  uuid: string;
  cap: string;
  nome_processo: string;
  status: string;
  versao: number;
  published: boolean;
  published_at: string | null;
  integrity_hash: string;
  dados: Record<string, unknown>;
}

// ============================================================================
// API functions
// ============================================================================

/** GET /api/areas/ — Lista areas top-level com pop_count */
export const listarAreas = async (): Promise<Area[]> => {
  const response = await api.get('/areas/');
  return response.data;
};

/** GET /api/areas/{slug}/ — Detalhe de uma area */
export const obterArea = async (slug: string): Promise<Area> => {
  const response = await api.get(`/areas/${slug}/`);
  return response.data;
};

/** GET /api/areas/{slug}/pops/ — POPs de uma area (default: published) */
export const listarPOPsPorArea = async (
  slug: string,
  params?: { status?: string }
): Promise<POPListItem[]> => {
  const response = await api.get(`/areas/${slug}/pops/`, { params });
  return response.data;
};

/** GET /api/areas/{slug}/pops/{codigo}/ — Detalhe por area + codigo */
export const obterPOPPorCodigo = async (
  slug: string,
  codigo: string
): Promise<POPDetail> => {
  const response = await api.get(`/areas/${slug}/pops/${codigo}/`);
  return response.data;
};

/** GET /api/pops/{uuid}/ — Detalhe por UUID */
export const obterPOP = async (uuid: string): Promise<POPDetail> => {
  const response = await api.get(`/pops/${uuid}/`);
  return response.data;
};

/** GET /api/pops/{uuid}/versions/ — Historico de versoes */
export const listarVersoes = async (uuid: string): Promise<PopVersion[]> => {
  const response = await api.get(`/pops/${uuid}/versions/`);
  return response.data;
};

/** GET /api/pops/resolve/?area={slug}&codigo={codigo}&v={versao} */
export const resolverCAP = async (params: {
  area?: string;
  codigo?: string;
  cap?: string;
  v?: number;
}): Promise<ResolveResult> => {
  const response = await api.get('/pops/resolve/', { params });
  return response.data;
};

/** Constroi URL direta para download do PDF (abre em nova aba) */
export const buildPdfUrl = (slug: string, codigo: string, versao?: number): string => {
  const base = api.defaults.baseURL || '/api';
  const vParam = versao ? `?v=${versao}` : '';
  return `${base}/areas/${slug}/pops/${codigo}/pdf/${vParam}`;
};

/** GET /api/stats/ — Metricas globais */
export const obterStatsGlobal = async (): Promise<StatsGlobal> => {
  const response = await api.get('/stats/');
  return response.data;
};

/** GET /api/stats/areas/{slug}/ — Metricas de uma area */
export const obterStatsArea = async (slug: string): Promise<StatsArea> => {
  const response = await api.get(`/stats/areas/${slug}/`);
  return response.data;
};

/** GET /api/pops/search/?q=...&area=slug&status=published&limit=20 */
export const buscarPOPs = async (params: {
  q: string;
  area?: string;
  status?: string;
  limit?: number;
}): Promise<POPListItem[]> => {
  const response = await api.get('/pops/search/', { params });
  return response.data;
};
