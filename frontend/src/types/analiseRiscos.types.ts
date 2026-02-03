/**
 * Types para Analise de Riscos
 *
 * Espelha enums e estruturas do backend Django
 */

// Enums espelhados do backend
export type StatusAnalise = 'RASCUNHO' | 'EM_ANALISE' | 'FINALIZADA';

export type ModoEntrada = 'QUESTIONARIO' | 'PDF' | 'ID';

export type TipoOrigem = 'PROJETO' | 'PROCESSO' | 'POP' | 'POLITICA' | 'NORMA' | 'PLANO';

export type CategoriaRisco =
  | 'OPERACIONAL'
  | 'FINANCEIRO'
  | 'LEGAL'
  | 'REPUTACIONAL'
  | 'TECNOLOGICO'
  | 'IMPACTO_DESIGUAL';

export type NivelRisco = 'BAIXO' | 'MEDIO' | 'ALTO' | 'CRITICO';

export type EstrategiaResposta =
  | 'MITIGAR'
  | 'EVITAR'
  | 'COMPARTILHAR'
  | 'ACEITAR'
  | 'RESGUARDAR';

// Estruturas de dados
export interface RiscoIdentificado {
  id: string;
  titulo: string;
  descricao?: string;
  categoria: CategoriaRisco;
  probabilidade: number; // 1-5
  impacto: number; // 1-5
  score_risco: number; // 1-25
  nivel_risco: NivelRisco;
  estrategia?: EstrategiaResposta;
  acao_resposta?: string;
  ativo: boolean;
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

// Contexto estruturado (Etapa 1)
export interface ContextoEstruturado {
  bloco_a: {
    nome_objeto?: string;
    objetivo_finalidade?: string;
    area_responsavel?: string;
    descricao_escopo?: string;
  };
  bloco_b: {
    recursos_necessarios?: string;
    areas_atores_envolvidos?: string;
    frequencia_execucao?: string;
    prazos_slas?: string;
    dependencias_externas?: string;
    historico_problemas?: string;
    impacto_se_falhar?: string;
  };
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
  FINANCEIRO: 'Perdas orcamentarias',
  LEGAL: 'Descumprimento normativo',
  REPUTACIONAL: 'Dano a imagem institucional',
  TECNOLOGICO: 'Falhas em sistemas/TI',
  IMPACTO_DESIGUAL: 'Impacto desigual por ausencia de analise distributiva',
};

// Descricoes das estrategias
export const DESCRICOES_ESTRATEGIA: Record<EstrategiaResposta, string> = {
  MITIGAR: 'Reduzir probabilidade ou impacto',
  EVITAR: 'Eliminar a causa do risco',
  COMPARTILHAR: 'Compartilhar/transferir parte do risco',
  ACEITAR: 'Reconhecer sem acao',
  RESGUARDAR: 'Documentar para compliance',
};

// Areas DECIPEX disponiveis (do CSV areas_organizacionais.csv)
export const AREAS_DECIPEX: Array<{ codigo: string; nome: string; prefixo: string }> = [
  { prefixo: '1', codigo: 'CGBEN', nome: 'Beneficios' },
  { prefixo: '2', codigo: 'CGPAG', nome: 'Pagamentos' },
  { prefixo: '3', codigo: 'COATE', nome: 'Atendimento' },
  { prefixo: '4', codigo: 'CGGAF', nome: 'Acervos Funcionais' },
  { prefixo: '5', codigo: 'DIGEP', nome: 'Ex-Territorios' },
  { prefixo: '5.1', codigo: 'DIGEP-RO', nome: 'Rondonia' },
  { prefixo: '5.2', codigo: 'DIGEP-RR', nome: 'Roraima' },
  { prefixo: '5.3', codigo: 'DIGEP-AP', nome: 'Amapa' },
  { prefixo: '6', codigo: 'CGRIS', nome: 'Riscos e Controle' },
  { prefixo: '7', codigo: 'CGCAF', nome: 'Complementacao' },
  { prefixo: '8', codigo: 'CGECO', nome: 'Extincao e Convenio' },
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

// Frequencias de execucao (Bloco B)
export const FREQUENCIAS_EXECUCAO = [
  { valor: 'CONTINUO', label: 'Continuo (diario/semanal)' },
  { valor: 'PERIODICO', label: 'Periodico (mensal/trimestral)' },
  { valor: 'PONTUAL', label: 'Pontual (evento unico)' },
  { valor: 'SOB_DEMANDA', label: 'Sob demanda' },
];
