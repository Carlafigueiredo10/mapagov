/**
 * API Service para Analise de Riscos
 *
 * Endpoints:
 * - POST /api/analise-riscos/criar/
 * - GET  /api/analise-riscos/listar/
 * - GET  /api/analise-riscos/<id>/
 * - PATCH /api/analise-riscos/<id>/questionario/
 * - PATCH /api/analise-riscos/<id>/etapa/
 * - POST /api/analise-riscos/<id>/riscos/
 * - PATCH /api/analise-riscos/<id>/riscos/<risco_id>/analise/
 * - DELETE /api/analise-riscos/<id>/riscos/<risco_id>/
 * - POST /api/analise-riscos/<id>/riscos/<risco_id>/respostas/
 * - PATCH /api/analise-riscos/<id>/finalizar/
 */
import api from './api';
import type {
  AnaliseRiscos,
  RiscoIdentificado,
  CategoriaRisco,
  EstrategiaResposta,
} from '../types/analiseRiscos.types';

// ============================================================================
// Request/Response Types
// ============================================================================

export interface CriarAnaliseRequest {
  tipo_origem: string;
  origem_id: string;
}

export interface CriarAnaliseResponse {
  resposta: string;
  dados: {
    id: string;
    status: string;
  };
}

export interface ListarAnalisesResponse {
  resposta: string;
  dados: {
    analises: Array<{
      id: string;
      tipo_origem: string;
      status: string;
      etapa_atual: number;
      area_decipex?: string;
      criado_em: string;
    }>;
  };
}

export interface DetalharAnaliseResponse {
  resposta: string;
  dados: AnaliseRiscos;
}

export interface AtualizarQuestionarioRequest {
  questoes_respondidas?: Record<string, string>;
  area_decipex?: string;
  etapa_atual?: number;
}

export interface AtualizarEtapaRequest {
  etapa: number;
}

export interface AdicionarRiscoRequest {
  titulo: string;
  descricao?: string;
  categoria?: CategoriaRisco;
  probabilidade?: number;
  impacto?: number;
  fonte_sugestao?: string;
}

export interface AdicionarRiscoResponse {
  resposta: string;
  dados: {
    id: string;
    titulo: string;
    score_risco: number;
    nivel_risco: string;
  };
}

export interface AnalisarRiscoRequest {
  probabilidade?: number;
  impacto?: number;
}

export interface AnalisarRiscoResponse {
  resposta: string;
  dados: {
    id: string;
    probabilidade: number;
    impacto: number;
    score_risco: number;
    nivel_risco: string;
  };
}

export interface AdicionarRespostaRequest {
  estrategia: EstrategiaResposta;
  descricao_acao?: string;
  responsavel_nome?: string;
  responsavel_area?: string;
  prazo?: string;
}

export interface AdicionarRespostaResponse {
  resposta: string;
  dados: {
    id: string;
    estrategia: string;
  };
}

export interface FinalizarAnaliseResponse {
  resposta: string;
  dados: {
    id: string;
    status: string;
  };
}

export interface ApiErrorResponse {
  erro: string;
  codigo: string;
}

// ============================================================================
// API Functions
// ============================================================================

/**
 * Criar nova analise de riscos
 */
export const criarAnalise = async (
  request: CriarAnaliseRequest
): Promise<CriarAnaliseResponse> => {
  const response = await api.post('/analise-riscos/criar/', request);
  return response.data;
};

/**
 * Listar analises do orgao
 */
export const listarAnalises = async (): Promise<ListarAnalisesResponse> => {
  const response = await api.get('/analise-riscos/listar/');
  return response.data;
};

/**
 * Detalhar analise especifica
 */
export const detalharAnalise = async (
  analiseId: string
): Promise<DetalharAnaliseResponse> => {
  const response = await api.get(`/analise-riscos/${analiseId}/`);
  return response.data;
};

/**
 * Atualizar questionario da analise
 */
export const atualizarQuestionario = async (
  analiseId: string,
  request: AtualizarQuestionarioRequest
): Promise<{ resposta: string; dados: { id: string; etapa_atual: number } }> => {
  const response = await api.patch(
    `/analise-riscos/${analiseId}/questionario/`,
    request
  );
  return response.data;
};

/**
 * Atualizar etapa da analise
 */
export const atualizarEtapa = async (
  analiseId: string,
  request: AtualizarEtapaRequest
): Promise<{ resposta: string; dados: { id: string; etapa_atual: number } }> => {
  const response = await api.patch(
    `/analise-riscos/${analiseId}/etapa/`,
    request
  );
  return response.data;
};

/**
 * Adicionar risco a analise
 */
export const adicionarRisco = async (
  analiseId: string,
  request: AdicionarRiscoRequest
): Promise<AdicionarRiscoResponse> => {
  const response = await api.post(
    `/analise-riscos/${analiseId}/riscos/`,
    request
  );
  return response.data;
};

/**
 * Analisar risco (atualizar probabilidade/impacto)
 */
export const analisarRisco = async (
  analiseId: string,
  riscoId: string,
  request: AnalisarRiscoRequest
): Promise<AnalisarRiscoResponse> => {
  const response = await api.patch(
    `/analise-riscos/${analiseId}/riscos/${riscoId}/analise/`,
    request
  );
  return response.data;
};

/**
 * Remover risco (soft delete)
 */
export const removerRisco = async (
  analiseId: string,
  riscoId: string
): Promise<{ resposta: string; dados: { id: string } }> => {
  const response = await api.delete(
    `/analise-riscos/${analiseId}/riscos/${riscoId}/`
  );
  return response.data;
};

/**
 * Adicionar resposta ao risco
 */
export const adicionarResposta = async (
  analiseId: string,
  riscoId: string,
  request: AdicionarRespostaRequest
): Promise<AdicionarRespostaResponse> => {
  const response = await api.post(
    `/analise-riscos/${analiseId}/riscos/${riscoId}/respostas/`,
    request
  );
  return response.data;
};

/**
 * Finalizar analise
 */
export const finalizarAnalise = async (
  analiseId: string
): Promise<FinalizarAnaliseResponse> => {
  const response = await api.patch(`/analise-riscos/${analiseId}/finalizar/`);
  return response.data;
};

// ============================================================================
// API v2 - NOVO FLUXO
// ============================================================================

export interface CriarAnaliseV2Request {
  modo_entrada: string;
  tipo_origem: string;
  origem_id?: string;
}

export interface SalvarContextoRequest {
  contexto_estruturado: {
    bloco_a: Record<string, string>;
    bloco_b: Record<string, string>;
  };
}

export interface SalvarBlocosRequest {
  respostas_blocos: Record<string, Record<string, string | string[]>>;
}

/**
 * Criar analise v2 com modo_entrada
 */
export const criarAnaliseV2 = async (
  request: CriarAnaliseV2Request
): Promise<CriarAnaliseResponse> => {
  const response = await api.post('/analise-riscos/v2/criar/', request);
  return response.data;
};

/**
 * Salvar contexto estruturado (Etapa 1)
 */
export const salvarContexto = async (
  analiseId: string,
  request: SalvarContextoRequest
): Promise<{ resposta: string; dados: { id: string; etapa_atual: number } }> => {
  const response = await api.patch(`/analise-riscos/${analiseId}/contexto/`, request);
  return response.data;
};

/**
 * Salvar blocos de identificacao (Etapa 2)
 */
export const salvarBlocos = async (
  analiseId: string,
  request: SalvarBlocosRequest
): Promise<{ resposta: string; dados: { id: string; etapa_atual: number; blocos_salvos: string[] } }> => {
  const response = await api.patch(`/analise-riscos/${analiseId}/blocos/`, request);
  return response.data;
};

/**
 * Inferir riscos baseado nas respostas dos blocos
 */
export const inferirRiscos = async (
  analiseId: string
): Promise<{ resposta: string; dados: { riscos_criados: number; riscos: Array<{ id: string; titulo: string; categoria: string }> } }> => {
  const response = await api.post(`/analise-riscos/${analiseId}/inferir/`);
  return response.data;
};
