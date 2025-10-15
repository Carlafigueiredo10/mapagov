// questionsRiscos.ts - 20 Perguntas Otimizadas para Análise de Riscos
import type { Question } from '../components/AnaliseRiscos/types';

export const QUESTIONS_RISCOS: Question[] = [
  // CONTEXTO E ESCOPO (2 perguntas)
  {
    id: 1,
    category: 'Contexto e Escopo',
    question:
      'Esse processo depende de informações de outros órgãos ou sistemas externos não mencionados no POP? Quais?',
    type: 'text',
    required: true,
  },
  {
    id: 2,
    category: 'Contexto e Escopo',
    question: 'Há picos sazonais de demanda?',
    type: 'select',
    options: [
      { value: 'Sim', label: 'Sim' },
      { value: 'Não', label: 'Não' },
      { value: 'Parcialmente', label: 'Parcialmente' },
    ],
    required: true,
  },

  // CONFORMIDADE E NORMATIVOS (2 perguntas)
  {
    id: 3,
    category: 'Conformidade e Normativos',
    question:
      'Há risco de conflito ou desatualização normativa entre os regulamentos aplicáveis?',
    type: 'select',
    options: [
      { value: 'Alto', label: 'Alto' },
      { value: 'Médio', label: 'Médio' },
      { value: 'Baixo', label: 'Baixo' },
      { value: 'Não aplicável', label: 'Não aplicável' },
    ],
    required: true,
  },
  {
    id: 4,
    category: 'Conformidade e Normativos',
    question:
      'Há apontamentos anteriores de TCU/CGU/Ouvidoria sobre este processo? Quais?',
    type: 'text',
    required: false,
  },

  // PESSOAS E SEGREGAÇÃO (3 perguntas)
  {
    id: 5,
    category: 'Pessoas e Segregação',
    question:
      'A segregação de funções está adequada entre os operadores identificados no POP?',
    type: 'select',
    options: [
      { value: 'Sim', label: 'Sim' },
      { value: 'Não', label: 'Não' },
      { value: 'Parcialmente', label: 'Parcialmente' },
    ],
    required: true,
  },
  {
    id: 6,
    category: 'Pessoas e Segregação',
    question: 'Existe plano de substituição/back-up para operadores críticos?',
    type: 'select',
    options: [
      { value: 'Sim', label: 'Sim' },
      { value: 'Não', label: 'Não' },
    ],
    required: true,
  },
  {
    id: 7,
    category: 'Pessoas e Segregação',
    question: 'Equipe treinada e atualizada nos normativos e sistemas?',
    type: 'select',
    options: [
      { value: 'Sim', label: 'Sim' },
      { value: 'Não', label: 'Não' },
      { value: 'Parcialmente', label: 'Parcialmente' },
    ],
    required: true,
  },

  // TECNOLOGIA E SISTEMAS (3 perguntas)
  {
    id: 8,
    category: 'Tecnologia e Sistemas',
    question:
      'Para os sistemas identificados no POP, avalie o nível de risco de indisponibilidade:',
    type: 'systems_checklist',
    required: true,
    systems: [], // Preenchido dinamicamente do POP
    all_systems: [
      // MESMA LISTA de helena_pop.py (50+ sistemas)
      // Gestão de Pessoal
      'SIAPE',
      'E-SIAPE',
      'SIGEPE',
      'SIGEP - AFD',
      'SIGEP-AFD',
      'SIGEP',
      'E-Pessoal TCU',
      'E-Pessoal',
      'ePessoal',
      'SIAPNET',
      'SIGAC',
      // Documentos
      'SEI',
      'DOINET',
      'DOU',
      'SOUGOV',
      'SouGov',
      'SouGov.br',
      'PETRVS',
      // Transparência
      'Portal da Transparência',
      'CNIS',
      'Site CGU-PAD',
      'CGU-PAD',
      'Sistema de Pesquisa Integrada do TCU',
      'TCU',
      'Consulta CPF RFB',
      'RFB',
      // Previdência
      'SISTEMA COMPREV',
      'COMPREV',
      'BG COMPREV',
      // Comunicação
      'TEAMS',
      'Microsoft Teams',
      'OUTLOOK',
      'Outlook',
      // Outros sistemas governamentais
      'DW',
      'CADSIAPE',
      'SIAPE-Saúde',
      'SIGEPE-Saúde',
      'SISAC',
      'SCDP',
      'SICONV',
      'SIGEF',
      'SIAFI',
      'e-Pessoal',
      'SIAPECAD',
      'SISRH',
      'SIORG',
      'SIGPLAN',
      'SPIUNET',
    ],
    risk_levels: ['Alto', 'Médio', 'Baixo', 'Não se aplica'],
  },
  {
    id: 9,
    category: 'Tecnologia e Sistemas',
    question:
      'Há risco de inconsistência de dados entre os sistemas utilizados?',
    type: 'select',
    options: [
      { value: 'Alto', label: 'Alto' },
      { value: 'Médio', label: 'Médio' },
      { value: 'Baixo', label: 'Baixo' },
      { value: 'Não aplicável', label: 'Não aplicável' },
    ],
    required: true,
  },
  {
    id: 10,
    category: 'Tecnologia e Sistemas',
    question:
      'Existe plano de contingência documentado se algum sistema crítico ficar indisponível?',
    type: 'text',
    required: true,
  },

  // DOCUMENTOS E PROVAS (3 perguntas)
  {
    id: 11,
    category: 'Documentos e Provas',
    question:
      'Quais documentos são mais frequentemente devolvidos por inconsistência/incompletude?',
    type: 'text',
    required: true,
  },
  {
    id: 12,
    category: 'Documentos e Provas',
    question: 'A taxa de devoluções por documentação supera 10%?',
    type: 'select',
    options: [
      { value: 'Sim', label: 'Sim' },
      { value: 'Não', label: 'Não' },
      { value: 'Não sei', label: 'Não sei' },
    ],
    required: false,
  },
  {
    id: 13,
    category: 'Documentos e Provas',
    question: 'Há risco de fraude documental identificado? Em que etapas?',
    type: 'select',
    options: [
      { value: 'Alto', label: 'Alto' },
      { value: 'Médio', label: 'Médio' },
      { value: 'Baixo', label: 'Baixo' },
      { value: 'Não aplicável', label: 'Não aplicável' },
    ],
    required: true,
  },

  // FLUXO E TEMPOS (2 perguntas)
  {
    id: 14,
    category: 'Fluxo e Tempos',
    question: 'Principais gargalos do fluxo (etapas que mais causam atraso)?',
    type: 'text',
    required: true,
  },
  {
    id: 15,
    category: 'Fluxo e Tempos',
    question: 'Tempo médio de conclusão do processo (dias corridos).',
    type: 'text',
    required: true,
  },

  // FINANCEIRO (2 perguntas)
  {
    id: 16,
    category: 'Financeiro',
    question:
      'Risco de cálculo incorreto (retroatividade/proporcionalidade) é recorrente?',
    type: 'select',
    options: [
      { value: 'Alto', label: 'Alto' },
      { value: 'Médio', label: 'Médio' },
      { value: 'Baixo', label: 'Baixo' },
      { value: 'Não aplicável', label: 'Não aplicável' },
    ],
    required: true,
  },
  {
    id: 17,
    category: 'Financeiro',
    question: 'Já houve reposição ao erário relacionada a este processo?',
    type: 'select',
    options: [
      { value: 'Sim', label: 'Sim' },
      { value: 'Não', label: 'Não' },
      { value: 'Desconheço', label: 'Desconheço' },
    ],
    required: false,
  },

  // LGPD E DADOS (2 perguntas)
  {
    id: 18,
    category: 'LGPD e Dados',
    question:
      'Há tratamento de dados pessoais sensíveis neste processo? (ex: CPF, dados médicos, situação financeira)',
    type: 'select',
    options: [
      { value: 'Sim', label: 'Sim' },
      { value: 'Não', label: 'Não' },
      { value: 'Não sei', label: 'Não sei' },
    ],
    required: true,
  },
  {
    id: 19,
    category: 'LGPD e Dados',
    question:
      'Por que motivo vocês podem usar esses dados pessoais e há regras sobre compartilhamento ou retenção? (ex: lei obriga, pessoa concordou, cumprir contrato)',
    type: 'text',
    required: true,
  },

  // CONTROLES E MONITORAMENTO (2 perguntas)
  {
    id: 20,
    category: 'Controles e Monitoramento',
    question:
      'Existem controles internos neste processo? (ex: checklist, dupla conferência, assinatura digital, logs)',
    type: 'text',
    required: true,
  },
];

/**
 * Helper: Detectar sistemas mencionados no texto do POP
 */
export function detectSystemsFromPOPText(
  popText: string,
  popInfo: { sistemas?: string[] }
): string[] {
  const question8 = QUESTIONS_RISCOS.find((q) => q.id === 8);
  if (!question8 || !question8.all_systems) return [];

  const detectedSystems = new Set<string>();

  // 1. Usar sistemas já detectados na extração do PDF
  if (popInfo.sistemas && popInfo.sistemas.length > 0) {
    popInfo.sistemas.forEach((s) => detectedSystems.add(s));
  }

  // 2. Buscar outros sistemas no texto completo do POP
  const popTextUpper = popText.toUpperCase();
  question8.all_systems.forEach((system) => {
    if (popTextUpper.includes(system.toUpperCase())) {
      detectedSystems.add(system);
    }
  });

  return Array.from(detectedSystems);
}

/**
 * Helper: Personalizar pergunta 1 com sistemas do POP
 */
export function customizeQuestion1(popInfo: { sistemas?: string[] }): Question {
  const q1 = QUESTIONS_RISCOS.find((q) => q.id === 1);
  if (!q1) return QUESTIONS_RISCOS[0];

  if (popInfo.sistemas && popInfo.sistemas.length > 0) {
    const sistemasPOP = popInfo.sistemas.join(', ');
    return {
      ...q1,
      question: `Além dos sistemas identificados no POP (${sistemasPOP}), esse processo depende de informações de outros órgãos ou sistemas externos? Quais?`,
    };
  }

  return q1;
}

/**
 * Helper: Obter pergunta por ID
 */
export function getQuestionById(id: number): Question | undefined {
  return QUESTIONS_RISCOS.find((q) => q.id === id);
}

/**
 * Helper: Validar se todas as obrigatórias foram respondidas
 */
export function validateRequiredAnswers(
  answers: Record<number, any>
): { valid: boolean; missingIds: number[] } {
  const missingIds: number[] = [];

  QUESTIONS_RISCOS.forEach((q) => {
    if (!q.required) return;

    const answer = answers[q.id];

    if (q.type === 'systems_checklist') {
      // Validar checklist de sistemas
      if (!answer || (!answer.systems && !answer.others)) {
        missingIds.push(q.id);
      }
    } else {
      // Validar perguntas normais
      if (!answer || answer === '') {
        missingIds.push(q.id);
      }
    }
  });

  return {
    valid: missingIds.length === 0,
    missingIds,
  };
}
