export interface HelenaMessage {
  id: string;
  tipo: 'usuario' | 'helena';
  mensagem: string;
  timestamp: string;
  loading?: boolean;
  interface?: {
    tipo: string;
    dados: any;
  };
}

