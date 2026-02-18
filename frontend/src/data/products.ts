import type { Product } from '../types/portal.types';

export const products: Product[] = [
  {
    code: 'geral',
    title: 'Helena - Assistente',
    icon: '🤖',
    status: 'disponivel',
    statusLabel: 'Orientação Geral',
    description: 'Assistente para orientação sobre os produtos e serviços do MapaGov.',
  },

  // ── Disponíveis ──────────────────────────────────────────────────
  {
    code: 'pop',
    title: 'Gerador de POP',
    icon: '📋',
    status: 'disponivel',
    statusLabel: 'Disponível',
    description: 'Estrutura o processo e gera o Procedimento Operacional Padrão.',
    route: '/pop',
  },
  {
    code: 'riscos',
    title: 'Análise de Riscos',
    icon: '⚠️',
    status: 'disponivel',
    statusLabel: 'Disponível',
    description: 'Identifica, avalia e sugere tratamento de riscos do processo.',
    route: '/riscos',
  },

  // ── Em homologação ───────────────────────────────────────────────
  {
    code: 'fluxograma',
    title: 'Gerador de Fluxograma',
    icon: '🔄',
    status: 'homologacao',
    statusLabel: 'Em homologação',
    description: 'Representa visualmente o fluxo do processo mapeado.',
    route: '/fluxograma',
  },
  {
    code: 'planejamento',
    title: 'Planejamento Estratégico',
    icon: '🎯',
    status: 'homologacao',
    statusLabel: 'Em homologação',
    description: 'Organiza objetivos, metas e diretrizes institucionais.',
    route: '/planejamento-estrategico',
  },

  // ── Em desenvolvimento ───────────────────────────────────────────
  {
    code: 'dashboard',
    title: 'Painel Executivo',
    icon: '📊',
    status: 'desenvolvimento',
    statusLabel: 'Em desenvolvimento',
    description: 'Apresenta indicadores e visão consolidada das iniciativas.',
    route: '/painel',
  },

  // ── Previstos (desabilitados) ────────────────────────────────────
  {
    code: 'acao',
    title: 'Plano de Ação e Acompanhamento',
    icon: '🛡️',
    status: 'planejado',
    statusLabel: 'Previsto',
    description: 'Define ações, responsáveis e prazos para execução e monitoramento.',
  },
  {
    code: 'dossie',
    title: 'Dossiê Consolidado de Governança',
    icon: '📄',
    status: 'planejado',
    statusLabel: 'Previsto',
    description: 'Reúne todos os documentos e análises gerados pelo sistema.',
  },
  {
    code: 'documentos',
    title: 'Relatório Técnico Consolidado',
    icon: '📝',
    status: 'planejado',
    statusLabel: 'Previsto',
    description: 'Formaliza o histórico completo do processo para arquivamento.',
  },
  {
    code: 'conformidade',
    title: 'Relatório de Conformidade',
    icon: '✅',
    status: 'planejado',
    statusLabel: 'Previsto',
    description: 'Verifica se o processo seguiu etapas e prazos previstos.',
  },
  {
    code: 'artefatos',
    title: 'Revisão e Adequação de Documentos',
    icon: '🔍',
    status: 'planejado',
    statusLabel: 'Previsto',
    description: 'Ajusta documentos à linguagem simples e padrões institucionais.',
  },
];

// Mensagens padrão da Helena para cada produto
export const productMessages: Record<string, string> = {
  geral: 'Estou em modo de orientação geral. Como posso te ajudar hoje?',
  pop: 'Vamos criar um POP estruturado. Qual processo você quer mapear?',
  fluxograma: 'Vou te ajudar a criar um fluxograma visual. Faça upload de um PDF de POP ou descreva o processo.',
  riscos: 'Para analisar riscos, primeiro precisamos de um processo mapeado. Já tem algum POP?',
  planejamento: 'Vamos estruturar o planejamento estratégico. Qual é o contexto institucional?',
  acao: 'O Plano de Ação e Acompanhamento está em desenvolvimento.',
  dashboard: 'O Painel Executivo está em desenvolvimento.',
  dossie: 'O Dossiê Consolidado de Governança está em desenvolvimento.',
  conformidade: 'O Relatório de Conformidade está em desenvolvimento.',
  documentos: 'O Relatório Técnico Consolidado está em desenvolvimento.',
  artefatos: 'A Revisão e Adequação de Documentos está em desenvolvimento.',
};
