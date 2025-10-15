export interface POPData {
  area_nome?: string;
  macroprocesso?: string;
  codigo_arquitetura?: string;
  nome_processo?: string;
  processo_especifico?: string;
  entrega_esperada?: string;
  dispositivos_normativos?: string;
  sistemas_utilizados?: string | string[];
  operadores?: string;
  etapas?: Etapa[];
  documentos_utilizados?: string;
  pontos_atencao?: string;
  fluxos_entrada?: string | string[];
  fluxos_saida?: string | string[];
}

export interface Etapa {
  descricao: string;
  detalhes?: string[];
  operador?: string;
}