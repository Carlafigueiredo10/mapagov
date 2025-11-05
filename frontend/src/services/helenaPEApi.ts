/**
 * Helena Planejamento Estratégico - API Service
 *
 * Serviço completo para integração com backend Django REST
 * Todos os 11 endpoints expostos com tipos TypeScript rigorosos
 */

import api from './api';

// ============================================================================
// TIPOS E INTERFACES
// ============================================================================

export type ModeloEstrategico =
  | 'tradicional'
  | 'bsc'
  | 'okr'
  | 'swot'
  | 'cenarios'
  | '5w2h'
  | 'hoshin';

export type EstadoConversa =
  | 'boas_vindas'
  | 'escolha_modo'
  | 'diagnostico_p1'
  | 'diagnostico_p2'
  | 'diagnostico_p3'
  | 'diagnostico_p4'
  | 'diagnostico_p5'
  | 'recomendacao'
  | 'contexto_organizacional'
  | 'construcao_modelo'
  | 'refinamento'
  | 'revisao'
  | 'confirmacao'
  | 'finalizado';

export type StatusPlanejamento =
  | 'diagnostico'
  | 'construcao'
  | 'revisao'
  | 'aprovado'
  | 'vigente'
  | 'concluido'
  | 'cancelado';

export interface ModeloConfig {
  id: ModeloEstrategico;
  nome: string;
  nome_completo: string;
  descricao: string;
  icone: string;
  complexidade: 'baixa' | 'media' | 'alta';
  prazo: 'curto' | 'medio' | 'longo';
  maturidade: 'iniciante' | 'intermediario' | 'avancado';
  tags: string[];
  componentes: string[];
  vantagens_publico: string[];
  quando_usar: string[];
}

export interface PerguntaDiagnostico {
  id: string;
  texto: string;
  opcoes: {
    valor: string;
    texto: string;
    pontos: {
      [key in ModeloEstrategico]?: number;
    };
  }[];
}

export interface SessionData {
  estado_atual: EstadoConversa;
  modo_entrada?: 'diagnostico' | 'explorar' | 'direto';
  diagnostico: Record<string, string>;
  pontuacao_modelos: Record<ModeloEstrategico, number>;
  modelos_recomendados: ModeloEstrategico[];
  modelo_selecionado?: ModeloEstrategico;
  contexto_organizacional: {
    orgao?: string;
    unidade?: string;
    escopo?: string;
    titulo_planejamento?: string;
  };
  estrutura_planejamento: any;
  percentual_conclusao: number;
  historico_conversa: string[];
}

export interface Validacao {
  valido: boolean;
  campos_faltantes: string[];
  percentual: number;
}

export interface Planejamento {
  id: number;
  titulo: string;
  modelo: ModeloEstrategico;
  modelo_display: string;
  descricao: string;
  orgao: string;
  unidade: string;
  escopo: string;
  diagnostico: Record<string, string>;
  estrutura: any;
  percentual_conclusao: number;
  status: StatusPlanejamento;
  status_display: string;
  criado_por: string;
  criado_em: string;
  atualizado_em: string;
  versao: number;
}

export interface Indicador {
  id: number;
  codigo: string;
  nome: string;
  tipo: string;
  meta: number;
  valor_atual: number | null;
  percentual_atingido: number;
  status_semaforo: 'verde' | 'amarelo' | 'vermelho';
}

// ============================================================================
// RESPOSTAS DA API
// ============================================================================

export interface IniciarResponse {
  session_data: SessionData;
  mensagem_inicial: string;
  modelos_disponiveis: ModeloConfig[];
  perguntas_diagnostico: PerguntaDiagnostico[];
}

export interface ProcessarResponse {
  resposta: string;
  session_data: SessionData;
  estado_atual: EstadoConversa;
  progresso: string;
  percentual_conclusao: number;
  metadados: {
    modelo_selecionado?: ModeloEstrategico;
    diagnostico_completo: boolean;
    pontuacao_modelos: Record<ModeloEstrategico, number>;
    validacao?: Validacao;
  };
}

export interface SalvarResponse {
  sucesso: boolean;
  planejamento_id: number;
  mensagem: string;
  planejamento: Planejamento;
}

export interface ListarResponse {
  total: number;
  planejamentos: Planejamento[];
}

export interface ObterResponse {
  planejamento: Planejamento;
  indicadores: Indicador[];
  comentarios: any[];
}

export interface RecomendarResponse {
  recomendacao_principal: ModeloEstrategico;
  top_3: ModeloEstrategico[];
  pontuacao: Record<ModeloEstrategico, number>;
  justificativa: string;
}

// ============================================================================
// SERVIÇO API
// ============================================================================

class HelenaPEApi {
  private baseURL = '/planejamento-estrategico';

  /**
   * Inicializa nova sessão de planejamento
   *
   * @returns Sessão inicial + modelos + perguntas diagnóstico
   */
  async iniciar(): Promise<IniciarResponse> {
    const response = await api.post<IniciarResponse>(`${this.baseURL}/iniciar/`);
    return response.data;
  }

  /**
   * Processa mensagem do usuário
   *
   * @param mensagem - Texto digitado pelo usuário
   * @param sessionData - Estado atual da sessão
   * @returns Resposta da Helena + novo estado
   */
  async processar(mensagem: string, sessionData: SessionData): Promise<ProcessarResponse> {
    const response = await api.post<ProcessarResponse>(`${this.baseURL}/processar/`, {
      mensagem,
      session_data: sessionData
    });
    return response.data;
  }

  /**
   * Salva planejamento no banco de dados
   *
   * @param sessionData - Estado completo da sessão
   * @param usuarioId - ID do usuário (opcional)
   * @returns Planejamento salvo
   */
  async salvar(sessionData: SessionData, usuarioId?: number): Promise<SalvarResponse> {
    const response = await api.post<SalvarResponse>(`${this.baseURL}/salvar/`, {
      session_data: sessionData,
      usuario_id: usuarioId
    });
    return response.data;
  }

  /**
   * Lista planejamentos com filtros
   *
   * @param filtros - Filtros opcionais
   * @returns Lista de planejamentos
   */
  async listar(filtros?: {
    modelo?: ModeloEstrategico;
    status?: StatusPlanejamento;
    limit?: number;
    offset?: number;
  }): Promise<ListarResponse> {
    const params = new URLSearchParams();

    if (filtros?.modelo) params.append('modelo', filtros.modelo);
    if (filtros?.status) params.append('status', filtros.status);
    if (filtros?.limit) params.append('limit', filtros.limit.toString());
    if (filtros?.offset) params.append('offset', filtros.offset.toString());

    const response = await api.get<ListarResponse>(
      `${this.baseURL}/listar/?${params.toString()}`
    );
    return response.data;
  }

  /**
   * Obtém planejamento por ID
   *
   * @param planejamentoId - ID do planejamento
   * @returns Planejamento completo + indicadores + comentários
   */
  async obter(planejamentoId: number): Promise<ObterResponse> {
    const response = await api.get<ObterResponse>(`${this.baseURL}/${planejamentoId}/`);
    return response.data;
  }

  /**
   * Aprova planejamento
   *
   * @param planejamentoId - ID do planejamento
   * @param usuarioId - ID do usuário aprovador
   * @returns Planejamento aprovado
   */
  async aprovar(planejamentoId: number, usuarioId?: number): Promise<SalvarResponse> {
    const response = await api.post<SalvarResponse>(
      `${this.baseURL}/${planejamentoId}/aprovar/`,
      { usuario_id: usuarioId }
    );
    return response.data;
  }

  /**
   * Cria nova versão do planejamento
   *
   * @param planejamentoId - ID do planejamento original
   * @param usuarioId - ID do usuário
   * @returns Nova versão criada
   */
  async criarRevisao(planejamentoId: number, usuarioId?: number): Promise<{
    sucesso: boolean;
    nova_versao_id: number;
    mensagem: string;
    planejamento: Planejamento;
  }> {
    const response = await api.post(
      `${this.baseURL}/${planejamentoId}/revisar/`,
      { usuario_id: usuarioId }
    );
    return response.data;
  }

  /**
   * Exporta planejamento
   *
   * @param planejamentoId - ID do planejamento
   * @param formato - 'json' ou 'pdf'
   * @returns Dados exportados
   */
  async exportar(planejamentoId: number, formato: 'json' | 'pdf' = 'json'): Promise<any> {
    const response = await api.get(
      `${this.baseURL}/${planejamentoId}/exportar/?formato=${formato}`
    );
    return response.data;
  }

  /**
   * Lista todos os modelos disponíveis
   *
   * @returns Array de modelos configurados
   */
  async listarModelos(): Promise<{ modelos: ModeloConfig[] }> {
    const response = await api.get<{ modelos: ModeloConfig[] }>(`${this.baseURL}/modelos/`);
    return response.data;
  }

  /**
   * Obtém perguntas do diagnóstico
   *
   * @returns Array de perguntas
   */
  async obterDiagnostico(): Promise<{ perguntas: PerguntaDiagnostico[] }> {
    const response = await api.get<{ perguntas: PerguntaDiagnostico[] }>(
      `${this.baseURL}/diagnostico/`
    );
    return response.data;
  }

  /**
   * Calcula recomendação de modelo baseado em respostas
   *
   * @param respostas - Respostas do diagnóstico
   * @returns Modelo recomendado + justificativa
   */
  async calcularRecomendacao(respostas: Record<string, string>): Promise<RecomendarResponse> {
    const response = await api.post<RecomendarResponse>(`${this.baseURL}/recomendar/`, {
      respostas
    });
    return response.data;
  }
}

// Singleton
export const helenaPEApi = new HelenaPEApi();

// Export default para compatibilidade
export default helenaPEApi;
