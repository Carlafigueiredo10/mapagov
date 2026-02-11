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

  // ── Fase 1 — Disponíveis ──────────────────────────────────────
  {
    code: 'pop',
    title: 'P1 - Gerador de POP',
    icon: '📋',
    status: 'disponivel',
    statusLabel: '✅ Disponível',
    description: 'Estrutura o processo e gera o Procedimento Operacional Padrão.',
    route: '/pop',
  },
  {
    code: 'fluxograma',
    title: 'P2 - Gerador de Fluxograma',
    icon: '🔄',
    status: 'disponivel',
    statusLabel: '✅ Disponível',
    description: 'Representa visualmente o fluxo do processo mapeado.',
    route: '/fluxograma',
  },
  {
    code: 'riscos',
    title: 'P3 - Análise de Riscos',
    icon: '⚠️',
    status: 'disponivel',
    statusLabel: '✅ Disponível',
    description: 'Identifica, avalia e sugere tratamento de riscos do processo.',
    route: '/riscos',
  },
  {
    code: 'planejamento',
    title: 'P4 - Planejamento Estratégico',
    icon: '🎯',
    status: 'disponivel',
    statusLabel: '✅ Disponível',
    description: 'Organiza objetivos, metas e diretrizes institucionais.',
    route: '/planejamento-estrategico',
  },

  // ── Fase 2 — Planejados ───────────────────────────────────────
  {
    code: 'acao',
    title: 'P5 - Plano de Ação e Acompanhamento',
    icon: '🛡️',
    status: 'planejado',
    statusLabel: '📅 Planejado',
    description: 'Define ações, responsáveis e prazos para execução e monitoramento.',
  },
  {
    code: 'dashboard',
    title: 'P6 - Painel Executivo',
    icon: '📊',
    status: 'planejado',
    statusLabel: '📅 Planejado',
    description: 'Apresenta indicadores e visão consolidada das iniciativas.',
  },

  // ── Fase 3 — Planejados ───────────────────────────────────────
  {
    code: 'dossie',
    title: 'P7 - Dossiê Consolidado de Governança',
    icon: '📄',
    status: 'planejado',
    statusLabel: '📅 Planejado',
    description: 'Reúne todos os documentos e análises gerados pelo sistema.',
  },
  {
    code: 'conformidade',
    title: 'P8 - Relatório de Conformidade',
    icon: '✅',
    status: 'planejado',
    statusLabel: '📅 Planejado',
    description: 'Verifica se o processo seguiu etapas e prazos previstos.',
  },

  // ── Fase 4 — Planejados ───────────────────────────────────────
  {
    code: 'documentos',
    title: 'P9 - Relatório Técnico Consolidado',
    icon: '📝',
    status: 'planejado',
    statusLabel: '📅 Planejado',
    description: 'Formaliza o histórico completo do processo para arquivamento.',
  },
  {
    code: 'artefatos',
    title: 'P10 - Revisão e Adequação de Documentos',
    icon: '🔍',
    status: 'planejado',
    statusLabel: '📅 Planejado',
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
