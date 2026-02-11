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
  // --- Identidade ---
  id: string;              // UUID estavel — obrigatorio para edicao granular
  ordem: number;           // Posicao explicita (nao depende de index do array)
  schema_version: number;  // 1 = formato canonico

  // --- Campos canonicos ---
  numero: string;              // "1", "2" etc. (display, derivado de ordem)
  acao_principal: string;      // Acao principal da etapa (ERA descricao)
  operador_nome: string;       // Padronizado (nunca "operador")
  tempo_estimado?: string;
  sistemas: string[];
  docs_requeridos: string[];
  docs_gerados: string[];
  verificacoes?: string[];     // Sub-itens / o que confere/verifica (ERA detalhes)

  // --- Condicionais ---
  tipo?: 'condicional';
  tipo_condicional?: 'binario' | 'multiplos';
  antes_decisao?: { numero: string; descricao: string };
  cenarios?: Cenario[];

  // --- Retrocompat (POPs antigos — normalizador preenche canonicos) ---
  descricao?: string;
  detalhes?: string[];
}
