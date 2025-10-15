// Tipos para o Portal MapaGov

export type ProductStatus = 'disponivel' | 'desenvolvimento' | 'planejado';

export type ProductCode =
  | 'geral'
  | 'pop'
  | 'fluxograma'
  | 'dossie'
  | 'dashboard'
  | 'riscos'
  | 'relatorio'
  | 'acao'
  | 'governanca'
  | 'documentos'
  | 'conformidade'
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
}

export interface PortalChatRequest {
  message: string;
  produto: ProductCode;
  session_id: string;
}

export interface PortalChatResponse {
  resposta: string;
  produto_sugerido?: ProductCode;
  acao?: 'redirecionar' | 'continuar';
  route?: string;
}
