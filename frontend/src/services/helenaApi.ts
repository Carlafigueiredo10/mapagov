import api from './api';

export interface ChatRequest {
  message: string;
  contexto: 'gerador_pop' | 'ajuda_mapeamento';
  session_id: string;
  nome_usuario?: string;
}

export interface ChatResponse {
  resposta: string;
  tipo_interface?: string;
  dados_interface?: Record<string, unknown>;
  dados_extraidos?: Record<string, unknown>;
  progresso?: string;
  conversa_completa?: boolean;
  schema_version?: string;
  metadados?: {
    auto_continue?: boolean;
    auto_continue_delay?: number;
    auto_continue_message?: string;
    [key: string]: unknown;
  };
  // ⚠️ Compat legado: backend às vezes envia esses ao invés dos acima
  interface?: string;
  dados?: Record<string, unknown>;
}

export interface ValidationRequest {
  campo: string;
  valor: string;
}

export interface ValidationResponse {
  valido: boolean;
  mensagem?: string;
}

export interface PDFRequest {
  dados_pop: Record<string, unknown>;
  session_id: string;
}

export interface PDFResponse {
  success: boolean;
  pdf_url?: string;
  arquivo?: string;
  error?: string;
}

// Parse seguro: só age se Axios devolveu string (NaN no JSON do backend)
function parseIfString(data: unknown): Record<string, unknown> {
  if (typeof data === 'string') {
    return JSON.parse(data.replace(/\bNaN\b/g, 'null'));
  }
  return data as Record<string, unknown>;
}

/**
 * POP — Chat principal com Helena (state machine conversacional)
 *
 * Padrao: POST /chat/ com contexto='gerador_pop'
 * Estado gerenciado server-side via Django sessions + POPStateMachine.
 * Retorna dados_extraidos que alimentam o formulario POP em tempo real.
 *
 * @see docs/api-patterns.md#1-pop-mapeamento-de-processos
 */
export const chatHelena = async (request: ChatRequest): Promise<ChatResponse> => {
  console.log("[helenaApi.ts] 📤 Enviando para /chat/:", {
    message: request.message,
    contexto: request.contexto,
    session_id: request.session_id
  });

  const response = await api.post('/chat/', {
    message: request.message,
    contexto: request.contexto,
    session_id: request.session_id,
    nome_usuario: request.nome_usuario,
  });

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const raw: any = parseIfString(response.data);

  // Contrato único: montar interface como { tipo, dados }
  const tipo = (raw.tipo_interface ?? raw.interface ?? null) as string | null;
  const dados = raw.dados_interface ?? raw.dados;

  if (tipo && !dados) {
    console.error('[helenaApi] tipo_interface presente mas dados_interface ausente:', tipo);
  }

  const normalized = {
    ...raw,
    interface: tipo
      ? { tipo, dados: dados ?? {} }
      : null,
  };

  console.log("[API normalized.interface]", normalized.interface);

  return normalized;
};

/** POP — Chat de ajuda sobre mapeamento de processos. POST /helena-mapeamento/ */
export const chatAjuda = async (request: ChatRequest): Promise<ChatResponse> => {
  const response = await api.post('/helena-mapeamento/', request);
  return response.data;
};

/** POP — Validacao de campo em tempo real. POST /validar-dados-pop/ */
export const validarCampo = async (request: ValidationRequest): Promise<ValidationResponse> => {
  const response = await api.post('/validar-dados-pop/', request);
  return response.data;
};

/** POP — Geracao de PDF do formulario. POST /gerar-pdf-pop/ (sincrono) */
export const gerarPDF = async (request: PDFRequest): Promise<PDFResponse> => {
  const response = await api.post('/gerar-pdf-pop/', request);
  return response.data;
};

/**
 * POP — Carrega POP salvo do backend.
 * GET /pop/<identifier>/ onde identifier e UUID ou session_id.
 *
 * @see docs/api-patterns.md#1-pop-mapeamento-de-processos
 */
export const loadPOP = async (identifier: string): Promise<{
  success: boolean;
  pop?: {
    id: number;
    uuid: string;
    session_id: string;
    integrity_hash: string;
    autosave_sequence: number;
    status: string;
    dados: Record<string, unknown>;
    updated_at: string | null;
  };
  error?: string;
}> => {
  const response = await api.get(`/pop/${identifier}/`);
  return response.data;
};

/** POP — Reinicia conversa e state machine. POST /reiniciar-conversa-helena/ */
export const reiniciarConversa = async (sessionId: string): Promise<void> => {
  await api.post('/reiniciar-conversa-helena/', {
    session_id: sessionId
  });
};

/** POP — Sugestoes via RAG para campos do formulario. POST /consultar-rag-sugestoes/ */
export const obterSugestoes = async (campo: string, area: string, contexto: string) => {
  const response = await api.post('/consultar-rag-sugestoes/', {
    campo,
    area,
    contexto
  });
  return response.data;
};

/** Portal — Chat de recepcao/triagem. POST /chat-recepcao/ */
export interface PortalChatRequest {
  message: string;
  produto: string;
  session_id: string;
}

export interface PortalChatResponse {
  resposta: string;
  produto_sugerido?: string;
  acao?: string;
  route?: string;
  tipo_interface?: string;
  dados_interface?: Record<string, unknown>;
}

export const chatRecepcao = async (request: PortalChatRequest): Promise<PortalChatResponse> => {
  const response = await api.post('/chat-recepcao/', request);
  return response.data;
};

// ==========================================
// 🚀 FASE 1 - Nova API HelenaCore
// ==========================================

export interface ChatV2Request {
  mensagem: string;
  session_id?: string;
}

export interface ChatV2Response {
  resposta: string;
  session_id: string;
  contexto_atual: string;
  agentes_disponiveis: string[];
  progresso?: string;
  sugerir_contexto?: string | null;
  metadados: {
    agent_version: string;
    agent_name: string;
  };
  erro?: boolean;
}

export interface MudarContextoRequest {
  session_id: string;
  novo_contexto: string;
}

export interface InfoSessaoResponse {
  session_id: string;
  contexto_atual: string;
  estados: Record<string, unknown>;
  agent_versions: Record<string, string>;
  criado_em: string;
  atualizado_em: string;
}

export interface ListaProdutosResponse {
  produtos: Array<{
    nome: string;
    descricao: string;
    versao: string;
  }>;
}

/**
 * 🆕 Chat V2 - Endpoint unificado FASE 1
 * Usa HelenaCore com roteamento automático entre produtos
 */
export const chatV2 = async (request: ChatV2Request): Promise<ChatV2Response> => {
  const response = await api.post('/chat-v2/', request);
  console.log("[chatV2] Resposta da nova API:", response.data);
  return response.data;
};

/**
 * Mudar contexto explicitamente (ex: 'etapas' -> 'pop')
 */
export const mudarContextoV2 = async (request: MudarContextoRequest): Promise<ChatV2Response> => {
  const response = await api.post('/chat-v2/mudar-contexto/', request);
  return response.data;
};

/**
 * Listar produtos Helena disponíveis
 */
export const listarProdutosV2 = async (): Promise<ListaProdutosResponse> => {
  const response = await api.get('/chat-v2/produtos/');
  return response.data;
};

/**
 * Obter informações da sessão
 */
export const infoSessaoV2 = async (sessionId: string): Promise<InfoSessaoResponse> => {
  const response = await api.get(`/chat-v2/sessao/${sessionId}/`);
  return response.data;
};

/**
 * Finalizar sessão
 */
export const finalizarSessaoV2 = async (sessionId: string): Promise<{ success: boolean }> => {
  const response = await api.post('/chat-v2/finalizar/', { session_id: sessionId });
  return response.data;
};

/**
 * Buscar histórico de mensagens da sessão
 */
export interface BuscarMensagensResponse {
  session_id: string;
  contexto_atual: string;
  session_exists: boolean;
  mensagens: Array<{
    role: 'user' | 'assistant' | 'system';
    content: string;
    contexto: string;
    metadados?: Record<string, unknown>;
    criado_em: string;
  }>;
}

export const buscarMensagensV2 = async (sessionId: string): Promise<BuscarMensagensResponse> => {
  const response = await api.get(`/chat-v2/sessao/${sessionId}/mensagens/`);
  return response.data;
};