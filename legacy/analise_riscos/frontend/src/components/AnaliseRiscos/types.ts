// types.ts - Tipos para Análise de Riscos

export interface POPInfo {
  id?: string;
  uuid?: string;
  titulo: string;
  codigo: string;
  macroprocesso?: string;
  processo?: string;
  subprocesso?: string;
  atividade?: string;
  responsavel?: string;
  sistemas: string[];
  operadores: string[];
  normativos: string[];
}

export interface QuestionOption {
  value: string;
  label: string;
}

export interface Question {
  id: number;
  category: string;
  question: string;
  type: 'text' | 'select' | 'sim_nao' | 'systems_checklist';
  options?: QuestionOption[];
  required: boolean;
  systems?: string[];
  all_systems?: string[];
  risk_levels?: string[];
}

export interface Answer {
  questionId: number;
  value: string | Record<string, string>;
  timestamp: Date;
}

export interface AnswersMap {
  [questionId: number]: string | Record<string, string>;
}

export interface Risco {
  titulo: string;
  descricao: string;
  categoria: 'Operacional' | 'Tecnológico' | 'Normativo' | 'Financeiro' | 'Reputacional' | 'Integridade';
  tipo_risco: 'Inerente' | 'Residual';
  probabilidade: 'Baixa' | 'Média' | 'Alta';
  impacto: 'Baixo' | 'Médio' | 'Alto';
  severidade: 'Baixo' | 'Moderado' | 'Alto' | 'Crítico';
  apetite_status: 'Dentro do apetite' | 'Fora do apetite' | 'Não informado';
  normativo_relacionado?: string;
  controles_existentes: string[];
  tratamento_recomendado: string;
  indicadores_monitoramento: string[];
  interdependencias: string[];
}

export interface MatrizRiscos {
  criticos: number;
  altos: number;
  moderados: number;
  baixos: number;
}

export interface Cabecalho {
  titulo: string;
  pop: string;
  codigo: string;
  macroprocesso?: string;
  processo?: string;
  subprocesso?: string;
  atividade?: string;
  responsavel: string;
  data_analise: string;
}

export interface MapaContexto {
  resumo_processo: string;
  partes_interessadas: string[];
  sistemas_utilizados: string[];
  documentos_principais: string[];
  normativos_aplicaveis: string[];
  pontos_atencao: string[];
}

export interface PlanoTratamento {
  mitigacao_imediata: string[];
  monitoramento: string[];
  lacunas_controle: string[];
  sugestoes_indicadores: string[];
  interdependencias_criticas: string[];
}

export interface SumarioExecutivo {
  maiores_riscos: string[];
  areas_criticas: string[];
  acoes_urgentes: string[];
  sintese_gerencial: string;
}

export interface RelatorioRiscos {
  cabecalho: Cabecalho;
  mapa_contexto: MapaContexto;
  riscos: Risco[];
  matriz_riscos: MatrizRiscos;
  analise_categorias: {
    operacional: number;
    tecnologico: number;
    normativo: number;
    financeiro: number;
    reputacional: number;
    integridade: number;
  };
  plano_tratamento: PlanoTratamento;
  sumario_executivo: SumarioExecutivo;
  conclusoes_recomendacoes: string;
}

export interface ChatMessage {
  id: string;
  role: 'helena' | 'user';
  content: string;
  timestamp: Date;
  questionId?: number;
  isQuestion?: boolean;
}

export interface AnaliseRiscosState {
  // Upload/Seleção POP
  popText: string;
  popInfo: POPInfo | null;
  popSourceType: 'upload' | 'existing' | null;

  // Chat e Perguntas
  messages: ChatMessage[];
  currentQuestionIndex: number;
  answers: AnswersMap;
  isAnswering: boolean;

  // Análise
  isAnalyzing: boolean;
  analysisProgress: number;
  relatorio: RelatorioRiscos | null;

  // PDF
  isGeneratingPDF: boolean;
  pdfUrl: string | null;

  // Estados
  currentStep: 'upload' | 'chat' | 'relatorio' | 'pdf';
  error: string | null;
}

export interface UploadPDFResponse {
  success: boolean;
  text: string;
  pop_info: POPInfo;
  error?: string;
}

export interface AnalyzeRisksRequest {
  pop_text: string;
  pop_info: POPInfo;
  answers: AnswersMap;
}

export interface AnalyzeRisksResponse {
  success: boolean;
  data?: RelatorioRiscos;
  error?: string;
}

export interface GeneratePDFResponse {
  success: boolean;
  pdf_url?: string;
  error?: string;
}
