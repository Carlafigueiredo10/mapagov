import api from './api';

export interface ChatRequest {
  message: string;
  contexto: 'gerador_pop' | 'ajuda_mapeamento';
  session_id: string;
}

export interface ChatResponse {
  resposta: string;
  tipo_interface?: string;
  dados_interface?: Record<string, unknown>;
  dados_extraidos?: Record<string, unknown>;
  progresso?: string;
  conversa_completa?: boolean;
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

// ✅ FIX: Converte string para objeto (backend às vezes retorna string com NaN)
const toObjectSafe = (raw: unknown): Record<string, unknown> => {
  if (typeof raw === 'string') {
    // Corrigir NaN → null para virar JSON válido
    const patched = raw.replace(/\bNaN\b/g, 'null');
    try {
      return JSON.parse(patched);
    } catch {
      console.error('[helenaApi] Erro ao parsear resposta como JSON:', raw.substring(0, 200));
      return {};
    }
  }
  return (raw as Record<string, unknown>) ?? {};
};

// ✅ FIX: Sanitiza NaN em objetos já parseados
const sanitizeNaN = (value: unknown): unknown => {
  if (typeof value === 'number' && Number.isNaN(value)) return null;
  if (Array.isArray(value)) return value.map(sanitizeNaN);
  if (value && typeof value === 'object') {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(value)) out[k] = sanitizeNaN(v);
    return out;
  }
  return value;
};

// Chat principal com Helena (USA /chat/ com POPStateMachine corrigido)
export const chatHelena = async (request: ChatRequest): Promise<ChatResponse> => {
  console.log("[helenaApi.ts] 📤 Enviando para /chat/:", {
    message: request.message,
    contexto: request.contexto,
    session_id: request.session_id
  });

  const response = await api.post('/chat/', {
    message: request.message,
    contexto: request.contexto,
    session_id: request.session_id
  });

  // ✅ FIX: Converter para objeto (backend às vezes retorna string com NaN)
  const raw: any = toObjectSafe(response.data);
  console.log("[helenaApi.ts] 📥 Resposta (objeto):", raw);

  // ✅ FIX: Normalização robusta (interface/dados -> tipo_interface/dados_interface)
  const normalized: ChatResponse = {
    resposta: String(raw.resposta ?? ''),
    tipo_interface: raw.tipo_interface ?? raw.interface ?? undefined,
    dados_interface: sanitizeNaN(raw.dados_interface ?? raw.dados ?? {}) as Record<string, unknown>,
    dados_extraidos: raw.dados_extraidos ?? raw.formulario_pop ?? undefined,
    progresso: raw.progresso ?? undefined,
    conversa_completa: raw.conversa_completa ?? undefined,
    metadados: raw.metadados ?? {}
  };

  // ✅ FIX: Retornar snapshot limpo (evita referências/mutações)
  const snap = JSON.parse(JSON.stringify(normalized));
  console.log("[helenaApi.ts] ✅ Normalized SNAP:", snap);

  return snap;
};

// Chat de ajuda/mapeamento
export const chatAjuda = async (request: ChatRequest): Promise<ChatResponse> => {
  const response = await api.post('/helena-mapeamento/', request);
  return response.data;
};

// Validação de campos em tempo real
export const validarCampo = async (request: ValidationRequest): Promise<ValidationResponse> => {
  const response = await api.post('/validar-dados-pop/', request);
  return response.data;
};

// Geração de PDF
export const gerarPDF = async (request: PDFRequest): Promise<PDFResponse> => {
  const response = await api.post('/gerar-pdf-pop/', request);
  return response.data;
};

// Reiniciar conversa
export const reiniciarConversa = async (sessionId: string): Promise<void> => {
  await api.post('/reiniciar-conversa-helena/', {
    session_id: sessionId
  });
};

// Obter sugestões da IA
export const obterSugestoes = async (campo: string, area: string, contexto: string) => {
  const response = await api.post('/consultar-rag-sugestoes/', {
    campo,
    area,
    contexto
  });
  return response.data;
};

// Chat de recepção (Portal)
export interface PortalChatRequest {
  message: string;
  produto: string;
  session_id: string;
}

export interface PortalChatResponse {
  resposta: string;
  produto_sugerido?: string;
  acao?: 'redirecionar' | 'continuar';
  route?: string;
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