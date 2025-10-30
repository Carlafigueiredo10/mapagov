export interface HelenaMessage {
  id: string;
  tipo: 'usuario' | 'helena';
  mensagem: string;
  timestamp: string;
  loading?: boolean;
  interface?: string | {  // 🔧 Pode ser string (novo formato) ou objeto (antigo)
    tipo: string;
    dados: any;
  };
  dados_interface?: any;  // 🔧 Compatibilidade com backend que envia dados separados
  metadados?: {
    badge?: {
      tipo: string;
      emoji: string;
      titulo: string;
      descricao: string;
      mostrar_animacao: boolean;
    };
    [key: string]: any;
  };
}

