/**
 * Types para Analise de Riscos
 *
 * Espelha enums e estruturas do backend Django
 */

// Enums espelhados do backend
export type StatusAnalise = 'RASCUNHO' | 'EM_ANALISE' | 'FINALIZADA';

export type ModoEntrada = 'QUESTIONARIO' | 'PDF' | 'ID';

// =============================================================================
// CAMADA DE LEITURA INSTITUCIONAL - GUIA DE GR DO MGI
// =============================================================================
// Esta camada NAO substitui a classificacao original do sistema.
// Serve para leitura gerencial e reporte institucional conforme MGI.

export type CategoriaMGI = 'ESTRATEGICO' | 'OPERACIONAL' | 'INTEGRIDADE';

export type NivelMGI = 'PEQUENO' | 'MODERADO' | 'ALTO' | 'CRITICO';

export interface LeituraMGI {
  categoria_mgi: CategoriaMGI;
  nivel_mgi: NivelMGI;
  is_integridade: boolean;
  fora_do_apetite: boolean;
  justificativa_categoria: string;
  justificativa_apetite: string;
  // Rastreabilidade de integridade (quando is_integridade=true)
  integridade_motivo: string;
  integridade_gatilhos: string[];
}

// Descricoes das categorias MGI
export const DESCRICOES_CATEGORIA_MGI: Record<CategoriaMGI, string> = {
  ESTRATEGICO: 'Riscos que afetam objetivos de longo prazo e imagem institucional',
  OPERACIONAL: 'Riscos relacionados a processos, recursos e operacoes do dia-a-dia',
  INTEGRIDADE: 'Riscos de fraude, corrupcao, conflito de interesses (apetite ZERO)',
};

// Cores para visualizacao dos niveis MGI
export const CORES_NIVEL_MGI: Record<NivelMGI, string> = {
  PEQUENO: '#22c55e',   // verde
  MODERADO: '#3b82f6',  // azul (apetite institucional)
  ALTO: '#f97316',      // laranja
  CRITICO: '#ef4444',   // vermelho
};

// Apetite institucional padrao conforme MGI
export const APETITE_INSTITUCIONAL_MGI: NivelMGI = 'MODERADO';

export type TipoOrigem = 'PROJETO' | 'PROCESSO' | 'POP' | 'POLITICA' | 'NORMA' | 'PLANO';

export type CategoriaRisco =
  | 'OPERACIONAL'
  | 'FINANCEIRO'
  | 'LEGAL'
  | 'REPUTACIONAL'
  | 'TECNOLOGICO'
  | 'IMPACTO_DESIGUAL';

export type NivelRisco = 'BAIXO' | 'MEDIO' | 'ALTO' | 'CRITICO';

// 4 estrategias oficiais do Guia de Gestao de Riscos do MGI
export type EstrategiaResposta =
  | 'MITIGAR'
  | 'EVITAR'
  | 'COMPARTILHAR'
  | 'ACEITAR';

// Status de tratamento do risco (derivado, nao persistido)
export type StatusTratamento = 'PENDENTE_DE_DELIBERACAO' | 'RESPONDIDO';

// Estruturas de dados
export interface RiscoIdentificado {
  id: string;
  titulo: string;
  descricao?: string;
  categoria: CategoriaRisco;
  probabilidade?: number; // 1-5, undefined = pendente de avaliacao
  impacto?: number; // 1-5, undefined = pendente de avaliacao
  score_risco?: number; // 1-25, undefined = pendente de avaliacao
  nivel_risco?: NivelRisco | ''; // vazio = pendente de avaliacao
  estrategia?: EstrategiaResposta;
  acao_resposta?: string;
  ativo: boolean;
  // Status de tratamento (derivado, transparencia gerencial)
  status_tratamento?: StatusTratamento;
  resposta_definida?: boolean;
  // Camada de leitura institucional MGI (derivada, nao substitui dados originais)
  leitura_mgi?: LeituraMGI;
}

export interface RespostaRisco {
  id: string;
  risco_id: string;
  estrategia: EstrategiaResposta;
  descricao_acao: string;
  responsavel_nome?: string;
  responsavel_area?: string;
  prazo?: string;
}

export interface AnaliseRiscos {
  id: string;
  modo_entrada: ModoEntrada;
  tipo_origem: TipoOrigem;
  origem_id?: string;
  status: StatusAnalise;
  etapa_atual: number; // 0-6
  contexto_estruturado: ContextoEstruturado;
  respostas_blocos: Record<string, Record<string, string | string[]>>;
  questoes_respondidas: Record<string, string>;
  area_decipex?: string;
  riscos: RiscoIdentificado[];
  criado_em: string;
  atualizado_em: string;
}

// =============================================================================
// BLOCO B - CAMPOS ESTRUTURADOS (ADITIVOS v2)
// =============================================================================
// Estes tipos sao ADITIVOS - coexistem com os campos de texto antigos
// Chave ausente = nao respondeu (diferente de [] ou NAO_SEI)

export type BlocoBRecurso =
  | 'PESSOAS'
  | 'TI'
  | 'ORCAMENTO'
  | 'EQUIPAMENTOS'
  | 'INFRAESTRUTURA'
  | 'MATERIAIS';

export type BlocoBFrequencia =
  | 'CONTINUO'
  | 'PERIODICO'
  | 'PONTUAL'
  | 'SOB_DEMANDA';

// NAO_SEI e valor valido - indica incerteza do usuario
export type BlocoBSLA = 'SIM' | 'NAO' | 'NAO_SEI';

export type BlocoBDependencia =
  | 'NAO'
  | 'SISTEMAS'
  | 'TERCEIROS'
  | 'AMBOS'
  | 'NAO_SEI';

export type BlocoBIncidentes = 'SIM' | 'NAO' | 'NAO_SEI';

// Interface para campos estruturados do Bloco B
export interface BlocoBEstruturado {
  // Checklist de recursos ([] = nenhum/nao se aplica)
  recursos?: BlocoBRecurso[];
  recursos_outros?: string;

  // Texto livre para atores
  atores_envolvidos_texto?: string;

  // Frequencia estruturada
  frequencia?: BlocoBFrequencia;

  // SLA com opcao NAO_SEI
  sla?: BlocoBSLA;
  sla_detalhe?: string;

  // Dependencia com opcao NAO_SEI
  dependencia?: BlocoBDependencia;
  dependencia_detalhe?: string;

  // Incidentes com opcao NAO_SEI
  incidentes?: BlocoBIncidentes;
  incidentes_detalhe?: string;

  // Texto livre para consequencias
  consequencia_texto?: string;
}

// Labels para recursos
export const BLOCO_B_RECURSOS: Array<{ valor: BlocoBRecurso; label: string }> = [
  { valor: 'PESSOAS', label: 'Pessoas/Equipe' },
  { valor: 'TI', label: 'Sistemas/TI' },
  { valor: 'ORCAMENTO', label: 'Orçamento/Verba' },
  { valor: 'EQUIPAMENTOS', label: 'Equipamentos' },
  { valor: 'INFRAESTRUTURA', label: 'Infraestrutura' },
  { valor: 'MATERIAIS', label: 'Materiais' },
];

// Labels para dependência
export const BLOCO_B_DEPENDENCIAS: Array<{ valor: BlocoBDependencia; label: string }> = [
  { valor: 'NAO', label: 'Não há dependência externa' },
  { valor: 'SISTEMAS', label: 'Apenas sistemas externos' },
  { valor: 'TERCEIROS', label: 'Apenas terceiros/fornecedores' },
  { valor: 'AMBOS', label: 'Sistemas e terceiros' },
  { valor: 'NAO_SEI', label: 'Não sei/Não tenho certeza' },
];

// Labels para SLA
export const BLOCO_B_SLA: Array<{ valor: BlocoBSLA; label: string }> = [
  { valor: 'SIM', label: 'Sim, existem prazos' },
  { valor: 'NAO', label: 'Não existem prazos' },
  { valor: 'NAO_SEI', label: 'Não sei/Não tenho certeza' },
];

// Labels para incidentes
export const BLOCO_B_INCIDENTES: Array<{ valor: BlocoBIncidentes; label: string }> = [
  { valor: 'SIM', label: 'Sim, houve incidentes' },
  { valor: 'NAO', label: 'Não houve incidentes' },
  { valor: 'NAO_SEI', label: 'Não sei/Não tenho certeza' },
];

// Contexto estruturado (Etapa 1)
// Interface RETROCOMPATIVEL - campos antigos + novos estruturados
export interface ContextoEstruturado {
  bloco_a: {
    nome_objeto?: string;
    objetivo_finalidade?: string;
    area_responsavel?: string;
    descricao_escopo?: string;
  };
  bloco_b: {
    // Campos antigos (texto) - mantidos para retrocompat
    recursos_necessarios?: string;
    areas_atores_envolvidos?: string;
    frequencia_execucao?: string;
    prazos_slas?: string;
    dependencias_externas?: string;
    historico_problemas?: string;
    impacto_se_falhar?: string;
  } & Partial<BlocoBEstruturado>;  // Campos novos estruturados (aditivos)
}

// Estruturas auxiliares
export interface AreaDECIPEX {
  codigo: string;
  nome: string;
}

export interface EtapaAnalise {
  numero: number;
  nome: string;
  descricao: string;
}

// Cores para visualizacao da matriz
export const CORES_NIVEL: Record<NivelRisco, string> = {
  BAIXO: '#22c55e',
  MEDIO: '#eab308',
  ALTO: '#f97316',
  CRITICO: '#ef4444',
};

// Descricoes das categorias
export const DESCRICOES_CATEGORIA: Record<CategoriaRisco, string> = {
  OPERACIONAL: 'Falhas em processos ou recursos',
  FINANCEIRO: 'Perdas orçamentárias',
  LEGAL: 'Descumprimento normativo',
  REPUTACIONAL: 'Dano à imagem institucional',
  TECNOLOGICO: 'Falhas em sistemas/TI',
  IMPACTO_DESIGUAL: 'Impacto desigual por ausência de análise distributiva',
};

// Descrições das estratégias (4 oficiais do Guia MGI)
export const DESCRICOES_ESTRATEGIA: Record<EstrategiaResposta, string> = {
  MITIGAR: 'Reduzir probabilidade ou impacto',
  EVITAR: 'Eliminar a causa do risco',
  COMPARTILHAR: 'Compartilhar/transferir parte do risco',
  ACEITAR: 'Reconhecer sem ação (requer justificativa para ALTO/CRÍTICO)',
};

// Áreas DECIPEX disponíveis (do CSV areas_organizacionais.csv)
export const AREAS_DECIPEX: Array<{ codigo: string; nome: string; prefixo: string }> = [
  { prefixo: '1', codigo: 'CGBEN', nome: 'Benefícios' },
  { prefixo: '2', codigo: 'CGPAG', nome: 'Pagamentos' },
  { prefixo: '3', codigo: 'COATE', nome: 'Atendimento' },
  { prefixo: '4', codigo: 'CGGAF', nome: 'Acervos Funcionais' },
  { prefixo: '5', codigo: 'DIGEP', nome: 'Ex-Territórios' },
  { prefixo: '5.1', codigo: 'DIGEP-RO', nome: 'Rondônia' },
  { prefixo: '5.2', codigo: 'DIGEP-RR', nome: 'Roraima' },
  { prefixo: '5.3', codigo: 'DIGEP-AP', nome: 'Amapá' },
  { prefixo: '6', codigo: 'CGRIS', nome: 'Riscos e Controle' },
  { prefixo: '7', codigo: 'CGCAF', nome: 'Complementação' },
  { prefixo: '8', codigo: 'CGECO', nome: 'Extinção e Convênio' },
  { prefixo: '9', codigo: 'COADM', nome: 'Apoio Administrativo' },
  { prefixo: '10', codigo: 'ASDIR', nome: 'Assessoria Diretor' },
];

// Etapas do fluxo v2
export const ETAPAS_ANALISE: EtapaAnalise[] = [
  { numero: 0, nome: 'Entrada', descricao: 'Selecionar tipo de objeto' },
  { numero: 1, nome: 'Contexto', descricao: 'Descrever o objeto analisado' },
  { numero: 2, nome: 'Identificacao', descricao: 'Responder perguntas orientadas' },
  { numero: 3, nome: 'Analise', descricao: 'Avaliar probabilidade e impacto' },
  { numero: 4, nome: 'Avaliacao', descricao: 'Visualizar matriz de riscos' },
  { numero: 5, nome: 'Resposta', descricao: 'Definir estrategias de resposta' },
];

// Tipos de origem disponiveis
export const TIPOS_ORIGEM: Array<{ valor: TipoOrigem; label: string }> = [
  { valor: 'PROJETO', label: 'Projeto' },
  { valor: 'PROCESSO', label: 'Processo' },
  { valor: 'POP', label: 'POP' },
  { valor: 'POLITICA', label: 'Politica' },
  { valor: 'NORMA', label: 'Norma' },
  { valor: 'PLANO', label: 'Plano' },
];

// Frequências de execução (Bloco B)
export const FREQUENCIAS_EXECUCAO = [
  { valor: 'CONTINUO', label: 'Contínuo (diário/semanal)' },
  { valor: 'PERIODICO', label: 'Periódico (mensal/trimestral)' },
  { valor: 'PONTUAL', label: 'Pontual (evento único)' },
  { valor: 'SOB_DEMANDA', label: 'Sob demanda' },
];
