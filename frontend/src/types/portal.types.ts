// Tipos para o Portal MapaGov

export type ProductStatus = 'disponivel' | 'homologacao' | 'desenvolvimento' | 'planejado';

export type ProductCode =
  | 'geral'
  | 'pop'
  | 'fluxograma'
  | 'riscos'
  | 'planejamento'
  | 'acao'
  | 'dashboard'
  | 'dossie'
  | 'conformidade'
  | 'documentos'
  | 'artefatos';

export interface Product {
  code: ProductCode;
  title: string;
  icon: string;
  status: ProductStatus;
  statusLabel: string;
  description?: string;
  route?: string;
}

export interface PortalChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'helena';
  timestamp: Date;
  tipo_interface?: string;
  dados_interface?: Record<string, unknown>;
}

export interface PortalChatRequest {
  message: string;
  produto: ProductCode;
  session_id: string;
}

export interface PortalChatResponse {
  resposta: string;
  produto_sugerido?: ProductCode;
  acao?: string;
  route?: string;
  tipo_interface?: string;
  dados_interface?: Record<string, unknown>;
}
