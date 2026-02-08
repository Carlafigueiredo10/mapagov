export interface POPData {
  area_nome?: string;
  macroprocesso?: string;
  codigo_arquitetura?: string;
  nome_processo?: string;
  processo_especifico?: string;
  entrega_esperada?: string;
  dispositivos_normativos?: string;
  sistemas_utilizados?: string | string[];
  operadores?: string | string[];
  etapas?: Etapa[];
  documentos_utilizados?: string;
  pontos_atencao?: string;
  fluxos_entrada?: string | string[];
  fluxos_saida?: string | string[];
}

// Schema completo de etapas (inline collection)

export interface Subetapa {
  numero: string;
  descricao: string;
}

export interface Cenario {
  numero: string;
  descricao: string;
  subetapas: Subetapa[];
}

export interface Etapa {
  numero: string;
  descricao: string;
  operador_nome: string;  // TODO: futuro {id, nome}
  sistemas: string[];
  docs_requeridos: string[];
  docs_gerados: string[];
  tempo_estimado?: string;
  tipo?: 'condicional';
  tipo_condicional?: 'binario' | 'multiplos';
  antes_decisao?: { numero: string; descricao: string };
  cenarios?: Cenario[];
  detalhes?: string[];
}