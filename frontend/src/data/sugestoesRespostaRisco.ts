/**
 * Catalogo de Sugestoes de Resposta a Riscos
 *
 * Estrutura:
 * 1. SUGESTOES_POR_ESTRATEGIA - Genericas, sempre aparecem
 * 2. SUGESTOES_POR_CATEGORIA_ESTRATEGIA - Especificas, aparecem se houver match
 *
 * Uso: getSugestoes(categoria, estrategia) retorna lista combinada
 */

import type { CategoriaRisco, EstrategiaResposta } from '../types/analiseRiscos.types';

// =============================================================================
// SUGESTOES GENERICAS POR ESTRATEGIA (sempre aparecem)
// =============================================================================

// 4 estrategias oficiais do Guia MGI
export const SUGESTOES_POR_ESTRATEGIA: Record<EstrategiaResposta, string[]> = {
  MITIGAR: [
    'Criar plano de contingencia',
    'Estabelecer monitoramento periodico',
    'Implementar controles preventivos',
    'Definir indicadores de alerta',
  ],
  EVITAR: [
    'Redesenhar processo para eliminar causa',
    'Suspender atividade ate resolucao',
    'Alterar escopo para remover dependencia',
  ],
  COMPARTILHAR: [
    'Formalizar acordo de responsabilidade compartilhada',
    'Contratar seguro ou garantia',
    'Estabelecer parceria com area especializada',
  ],
  ACEITAR: [
    'Documentar decisao de aceite formal',
    'Registrar justificativa tecnica',
    'Informar stakeholders sobre o risco aceito',
    // Incorporado de RESGUARDAR (documentacao e boa pratica ao aceitar)
    'Documentar evidencias para compliance',
    'Registrar em ata de reuniao',
    'Arquivar documentacao comprobatoria',
  ],
};

// =============================================================================
// SUGESTOES ESPECIFICAS POR CATEGORIA + ESTRATEGIA
// =============================================================================

type ChaveCategoria = `${CategoriaRisco}_${EstrategiaResposta}`;

export const SUGESTOES_POR_CATEGORIA_ESTRATEGIA: Partial<Record<ChaveCategoria, string[]>> = {
  // OPERACIONAL
  OPERACIONAL_MITIGAR: [
    'Criar checklist de verificacao pre-execucao',
    'Estabelecer backup de recursos criticos',
    'Documentar procedimentos alternativos',
    'Treinar equipe em procedimentos de contingencia',
  ],
  OPERACIONAL_EVITAR: [
    'Automatizar processo para eliminar erro humano',
    'Terceirizar atividade de alto risco',
  ],
  OPERACIONAL_COMPARTILHAR: [
    'Dividir responsabilidade entre areas',
    'Contratar fornecedor especializado',
  ],

  // LEGAL
  LEGAL_MITIGAR: [
    'Consultar assessoria juridica preventivamente',
    'Revisar conformidade com normas aplicaveis',
    'Atualizar documentacao legal',
    'Implementar controles de conformidade',
  ],
  LEGAL_EVITAR: [
    'Suspender atividade ate parecer juridico',
    'Alterar procedimento para atender legislacao',
  ],
  LEGAL_ACEITAR: [
    'Obter parecer juridico formal',
    'Documentar base legal da decisao',
    'Arquivar evidencias de due diligence',
  ],

  // TECNOLOGICO
  TECNOLOGICO_MITIGAR: [
    'Implementar backup automatizado',
    'Criar ambiente de contingencia',
    'Estabelecer SLA com fornecedor de TI',
    'Documentar procedimento de recuperacao',
  ],
  TECNOLOGICO_EVITAR: [
    'Migrar para sistema mais estavel',
    'Eliminar dependencia de sistema legado',
  ],
  TECNOLOGICO_COMPARTILHAR: [
    'Contratar suporte especializado',
    'Formalizar SLA com garantia de disponibilidade',
  ],

  // REPUTACIONAL
  REPUTACIONAL_MITIGAR: [
    'Preparar plano de comunicacao de crise',
    'Estabelecer canal de comunicacao transparente',
    'Monitorar midias e redes sociais',
  ],
  REPUTACIONAL_EVITAR: [
    'Revisar processo antes de divulgacao',
    'Suspender comunicacao ate alinhamento',
  ],
  REPUTACIONAL_ACEITAR: [
    'Documentar posicionamento institucional',
    'Registrar comunicados oficiais',
  ],

  // FINANCEIRO
  FINANCEIRO_MITIGAR: [
    'Criar reserva de contingencia orcamentaria',
    'Estabelecer limites de gasto',
    'Implementar aprovacoes em alcada',
  ],
  FINANCEIRO_EVITAR: [
    'Cancelar contratacao de alto risco',
    'Renegociar termos contratuais',
  ],
  FINANCEIRO_COMPARTILHAR: [
    'Contratar seguro patrimonial',
    'Dividir custos com parceiros',
  ],

  // IMPACTO_DESIGUAL
  IMPACTO_DESIGUAL_MITIGAR: [
    'Realizar consulta publica com grupos afetados',
    'Implementar canal de denuncia acessivel',
    'Criar mecanismo de compensacao',
    'Adaptar servico para grupos vulneraveis',
  ],
  IMPACTO_DESIGUAL_EVITAR: [
    'Redesenhar processo com perspectiva de equidade',
    'Incluir representantes de grupos afetados na decisao',
  ],
  IMPACTO_DESIGUAL_ACEITAR: [
    'Documentar analise de impacto distributivo',
    'Registrar medidas de inclusao adotadas',
  ],
};

// =============================================================================
// FUNCAO PRINCIPAL - Retorna sugestoes combinadas
// =============================================================================

export function getSugestoes(
  categoria: CategoriaRisco,
  estrategia: EstrategiaResposta
): string[] {
  const genericas = SUGESTOES_POR_ESTRATEGIA[estrategia] || [];
  const chave: ChaveCategoria = `${categoria}_${estrategia}`;
  const especificas = SUGESTOES_POR_CATEGORIA_ESTRATEGIA[chave] || [];

  // Especificas primeiro, depois genericas (sem duplicar)
  const todas = [...especificas];
  for (const g of genericas) {
    if (!todas.includes(g)) {
      todas.push(g);
    }
  }

  return todas;
}

// =============================================================================
// HELPER - Para debug/exibicao
// =============================================================================

export function contarSugestoes(): { total: number; porEstrategia: Record<string, number> } {
  let total = 0;
  const porEstrategia: Record<string, number> = {};

  for (const [est, sugs] of Object.entries(SUGESTOES_POR_ESTRATEGIA)) {
    porEstrategia[est] = sugs.length;
    total += sugs.length;
  }

  for (const sugs of Object.values(SUGESTOES_POR_CATEGORIA_ESTRATEGIA)) {
    if (sugs) total += sugs.length;
  }

  return { total, porEstrategia };
}
