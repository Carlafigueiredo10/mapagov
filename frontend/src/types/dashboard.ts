/**
 * Tipos para o Sistema de Dashboards Institucionais
 * Helena Planejamento Estratégico - Governança
 *
 * Estrutura integrada:
 * - Dashboard das Áreas (operacional)
 * - Dashboard do Diretor (executivo)
 */

// ============================================================================
// DASHBOARD DAS ÁREAS
// ============================================================================

/**
 * Pedido do Diretor associado a um projeto
 */
export interface PedidoDiretor {
  existe: boolean;
  data_pedido?: string; // ISO date format
  descricao_pedido?: string;
  canal?: string; // "Despacho SEI", "E-mail", "Reunião"
  prazo_retorno?: string; // ISO date format - prazo para atendimento
  retorno_esperado?: string;
  status_pedido?: 'Em andamento' | 'Pendente' | 'Aguardando resposta' | 'Atendido integralmente' | 'Atendido parcialmente' | 'Não atendido';
  // Campos para status "Em andamento"
  data_andamento?: string; // ISO date format - quando começou o andamento
  descricao_andamento?: string; // O que está sendo feito
  // Campos para status "Aguardando resposta"
  setor_aguardando?: string; // De qual setor está aguardando
  data_solicitacao_setor?: string; // ISO date format
  prazo_resposta_setor?: string; // ISO date format
  // Campos para status de atendimento (Atendido integralmente/parcialmente/não atendido)
  data_atendimento?: string; // ISO date format
  descricao_atendimento?: string; // Descrição de como foi atendido
}

/**
 * Fase detalhada do projeto
 */
export interface FaseDetalhada {
  numero: number;
  descricao: string;
  resultados: string;
}

/**
 * Última atualização registrada
 */
export interface UltimaAtualizacao {
  data: string; // ISO date format
  responsavel: string;
}

/**
 * Registro histórico de uma atualização
 */
export interface HistoricoAtualizacao {
  data: string; // ISO date format
  responsavel: string;
  alteracoes: string[]; // Lista de mudanças
  observacoes?: string;
}

/**
 * Projeto Estratégico (Dashboard das Áreas)
 */
export interface ProjetoEstrategico {
  id_projeto: string;
  area: string; // "CGRIS", "CGBEN", "CGPAG", etc.
  nome_projeto: string;
  resultado_esperado: string;
  fases_detalhadas?: FaseDetalhada[]; // Fases customizadas do projeto
  fase_atual: string; // "Planejamento", "Execução (Fase 2)", "Conclusão"
  proximos_encaminhamentos: string;
  pedido_diretor: PedidoDiretor;
  dependencia?: string;
  andamento: number; // 0 a 100
  ultima_atualizacao: UltimaAtualizacao;
  historico_atualizacoes: HistoricoAtualizacao[];
}

// ============================================================================
// DASHBOARD DO DIRETOR
// ============================================================================

/**
 * Movimentação histórica de um pedido
 */
export interface HistoricoMovimentacao {
  data: string; // ISO date format
  acao: string; // "Pedido criado", "Status atualizado", etc.
  detalhe: string;
}

/**
 * Pedido consolidado no Dashboard do Diretor
 */
export interface PedidoDiretorConsolidado {
  id_pedido: string;
  area: string;
  projeto: string;
  descricao_pedido: string;
  data_pedido: string; // ISO date format
  canal: string;
  prazo_retorno: string; // ISO date format
  status_pedido: 'Em andamento' | 'Atendido' | 'Pendente' | 'Aguardando resposta';
  responsavel_area: string;
  ultima_atualizacao: string; // ISO date format
  comentarios_area?: string;
  historico_movimentacoes: HistoricoMovimentacao[];
}

// ============================================================================
// UTILIDADES
// ============================================================================

/**
 * Status de alerta visual no Dashboard do Diretor
 */
export type StatusAlerta = 'verde' | 'amarelo' | 'vermelho' | 'neutro';

/**
 * Filtros disponíveis para os dashboards
 */
export interface FiltrosDashboard {
  areas?: string[];
  status?: string[];
  fases?: string[];
  busca?: string;
}

/**
 * Estatísticas consolidadas do Dashboard
 */
export interface EstatisticasDashboard {
  total_projetos: number;
  total_pedidos: number;
  pedidos_atendidos: number;
  pedidos_em_andamento: number;
  pedidos_atrasados: number;
  projetos_por_fase: Record<string, number>;
  andamento_medio: number;
}

/**
 * Áreas organizacionais disponíveis (carregadas do CSV)
 * Fonte: documentos_base/areas_organizacionais.csv
 */
export const AREAS_DISPONIVEIS = [
  'CGBEN',    // Benefícios
  'CGPAG',    // Pagamentos
  'COATE',    // Atendimento
  'CGGAF',    // Acervos Funcionais
  'DIGEP',    // Ex-Territórios
  'CGRIS',    // Riscos e Controle
  'CGCAF',    // Complementação
  'CGECO',    // Extinção e Convênio
  'COADM',    // Apoio Administrativo
  'ASDIR'     // Assessoria Diretor
] as const;

export type AreaOrganizacional = typeof AREAS_DISPONIVEIS[number];

/**
 * Fases de projeto disponíveis
 */
export const FASES_PROJETO = [
  'Planejamento',
  'Execução (Fase 1)',
  'Execução (Fase 2)',
  'Conclusão',
  'Encerrado',
  'Suspenso'
] as const;

export type FaseProjeto = typeof FASES_PROJETO[number];

/**
 * Canais de comunicação
 */
export const CANAIS_COMUNICACAO = [
  'Despacho SEI',
  'E-mail institucional',
  'Reunião de pauta',
  'Reunião extraordinária',
  'Ofício',
  'Mensagem Teams'
] as const;

export type CanalComunicacao = typeof CANAIS_COMUNICACAO[number];
