/**
 * Tipos comuns do módulo de Planejamento Estratégico
 * Compartilhados entre componentes, hooks e services
 */

export interface ModeloPlanejamento {
  id: string;
  nome: string;
  descricao: string;
  icone: string;
  complexidade: 'Baixa' | 'Média' | 'Alta';
  prazo: 'Curto' | 'Médio' | 'Longo';
  tags: string[];
  cor?: string; // Cor institucional do modelo (hex)
}

export interface PerguntaDiagnostico {
  id: string;
  texto: string;
  opcoes: {
    valor: string;
    texto: string;
  }[];
}

export interface Mensagem {
  tipo: 'user' | 'helena';
  texto: string;
  timestamp?: number;
}

export interface SessionData {
  session_id: string;
  estado_atual: string;
  modelo_selecionado?: string;
  percentual_conclusao: number;
  estrutura_planejamento?: any;
  diagnostico?: any;
}

export type EstadoFluxo = 'inicial' | 'painel' | 'diagnostico' | 'modelos' | 'chat';
