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

// Chat principal com Helena
export const chatHelena = async (request: ChatRequest): Promise<ChatResponse> => {
  const response = await api.post('/chat/', request);
  console.log("[helenaApi.ts] Resposta CRUA da API:", response.data);
  return response.data;
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