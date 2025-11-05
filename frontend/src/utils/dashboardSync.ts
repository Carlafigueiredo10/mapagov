/**
 * Utilitário de Sincronização de Dashboards
 * Helena PE - Sistema de Governança Integrada
 *
 * Garante consistência automática entre:
 * - Dashboard das Áreas (fonte)
 * - Dashboard do Diretor (consolidado)
 */

import {
  ProjetoEstrategico,
  PedidoDiretorConsolidado,
  StatusAlerta,
  HistoricoMovimentacao
} from '../types/dashboard';

// ============================================================================
// SINCRONIZAÇÃO: ÁREAS → DIRETOR
// ============================================================================

/**
 * Sincroniza um projeto da área para o dashboard do diretor
 * Cria ou atualiza pedido consolidado quando existe pedido_diretor
 */
export function sincronizarParaDiretor(
  projeto: ProjetoEstrategico,
  pedidosExistentes: PedidoDiretorConsolidado[]
): PedidoDiretorConsolidado | null {
  // Só sincroniza se houver pedido do diretor
  if (!projeto.pedido_diretor.existe) {
    return null;
  }

  const idPedido = `pedido_${projeto.area.toLowerCase()}_${projeto.id_projeto}`;
  const pedidoExistente = pedidosExistentes.find(p => p.id_pedido === idPedido);

  // Criar novo pedido ou atualizar existente
  const pedidoConsolidado: PedidoDiretorConsolidado = {
    id_pedido: idPedido,
    area: projeto.area,
    projeto: projeto.nome_projeto,
    descricao_pedido: projeto.pedido_diretor.descricao_pedido || '',
    data_pedido: projeto.pedido_diretor.data_pedido || new Date().toISOString().split('T')[0],
    canal: projeto.pedido_diretor.canal || 'Não especificado',
    prazo_retorno: projeto.pedido_diretor.retorno_esperado || 'A definir',
    status_pedido: projeto.pedido_diretor.status_pedido || 'Pendente',
    responsavel_area: projeto.ultima_atualizacao.responsavel,
    ultima_atualizacao: projeto.ultima_atualizacao.data,
    comentarios_area: projeto.proximos_encaminhamentos,
    historico_movimentacoes: pedidoExistente?.historico_movimentacoes || []
  };

  // Adicionar movimentação ao histórico se houver mudança
  if (pedidoExistente) {
    const mudancas = detectarMudancas(pedidoExistente, pedidoConsolidado);
    if (mudancas.length > 0) {
      pedidoConsolidado.historico_movimentacoes.push({
        data: new Date().toISOString().split('T')[0],
        acao: 'Status atualizado',
        detalhe: mudancas.join('; ')
      });
    }
  } else {
    // Primeiro registro
    pedidoConsolidado.historico_movimentacoes.push({
      data: pedidoConsolidado.data_pedido,
      acao: 'Pedido criado',
      detalhe: `Solicitado via ${pedidoConsolidado.canal}`
    });
  }

  return pedidoConsolidado;
}

/**
 * Detecta mudanças entre versão anterior e atual do pedido
 */
function detectarMudancas(
  anterior: PedidoDiretorConsolidado,
  atual: PedidoDiretorConsolidado
): string[] {
  const mudancas: string[] = [];

  if (anterior.status_pedido !== atual.status_pedido) {
    mudancas.push(`Status alterado de "${anterior.status_pedido}" para "${atual.status_pedido}"`);
  }

  if (anterior.prazo_retorno !== atual.prazo_retorno) {
    mudancas.push(`Prazo alterado de ${anterior.prazo_retorno} para ${atual.prazo_retorno}`);
  }

  if (anterior.descricao_pedido !== atual.descricao_pedido) {
    mudancas.push('Descrição do pedido foi atualizada');
  }

  if (anterior.comentarios_area !== atual.comentarios_area) {
    mudancas.push('Área adicionou novos comentários');
  }

  return mudancas;
}

// ============================================================================
// REGRAS DE EXIBIÇÃO E ALERTAS
// ============================================================================

/**
 * Calcula o status de alerta para um pedido
 */
export function calcularStatusAlerta(pedido: PedidoDiretorConsolidado): StatusAlerta {
  // Pedido atendido = verde
  if (pedido.status_pedido === 'Atendido') {
    return 'verde';
  }

  // Sem prazo definido = neutro
  if (pedido.prazo_retorno === 'A definir' || !pedido.prazo_retorno) {
    return 'neutro';
  }

  // Calcular dias restantes
  const hoje = new Date();
  const prazo = new Date(pedido.prazo_retorno);
  const diasRestantes = Math.ceil((prazo.getTime() - hoje.getTime()) / (1000 * 60 * 60 * 24));

  // Pedido atrasado = vermelho
  if (diasRestantes < 0) {
    return 'vermelho';
  }

  // Menos de 3 dias = amarelo
  if (diasRestantes <= 3) {
    return 'amarelo';
  }

  // Em andamento dentro do prazo = neutro
  return 'neutro';
}

/**
 * Retorna o ícone correspondente ao status de alerta
 */
export function getIconeAlerta(status: StatusAlerta): string {
  const icones = {
    verde: '🟢',
    amarelo: '🟡',
    vermelho: '🔴',
    neutro: '⚫'
  };
  return icones[status];
}

/**
 * Calcula dias restantes até o prazo
 */
export function calcularDiasRestantes(prazoRetorno: string): number | null {
  if (prazoRetorno === 'A definir' || !prazoRetorno) {
    return null;
  }

  const hoje = new Date();
  const prazo = new Date(prazoRetorno);
  return Math.ceil((prazo.getTime() - hoje.getTime()) / (1000 * 60 * 60 * 24));
}

/**
 * Formata dias restantes em texto legível
 */
export function formatarDiasRestantes(dias: number | null): string {
  if (dias === null) {
    return 'Sem prazo definido';
  }

  if (dias < 0) {
    return `Atrasado há ${Math.abs(dias)} dias`;
  }

  if (dias === 0) {
    return 'Vence hoje';
  }

  if (dias === 1) {
    return 'Vence amanhã';
  }

  return `${dias} dias restantes`;
}

// ============================================================================
// FILTROS E ORDENAÇÃO
// ============================================================================

/**
 * Filtra pedidos por critérios
 */
export function filtrarPedidos(
  pedidos: PedidoDiretorConsolidado[],
  filtros: {
    area?: string;
    status?: string;
    busca?: string;
  }
): PedidoDiretorConsolidado[] {
  return pedidos.filter(pedido => {
    // Filtro por área
    if (filtros.area && pedido.area !== filtros.area) {
      return false;
    }

    // Filtro por status
    if (filtros.status && pedido.status_pedido !== filtros.status) {
      return false;
    }

    // Filtro por busca textual
    if (filtros.busca) {
      const termoBusca = filtros.busca.toLowerCase();
      const camposBusca = [
        pedido.projeto,
        pedido.descricao_pedido,
        pedido.area,
        pedido.responsavel_area
      ].map(c => c.toLowerCase());

      if (!camposBusca.some(campo => campo.includes(termoBusca))) {
        return false;
      }
    }

    return true;
  });
}

/**
 * Ordena pedidos por prioridade (atrasados primeiro)
 */
export function ordenarPorPrioridade(
  pedidos: PedidoDiretorConsolidado[]
): PedidoDiretorConsolidado[] {
  return [...pedidos].sort((a, b) => {
    const alertaA = calcularStatusAlerta(a);
    const alertaB = calcularStatusAlerta(b);

    // Ordem de prioridade: vermelho > amarelo > neutro > verde
    const prioridades = { vermelho: 0, amarelo: 1, neutro: 2, verde: 3 };

    if (prioridades[alertaA] !== prioridades[alertaB]) {
      return prioridades[alertaA] - prioridades[alertaB];
    }

    // Se mesma prioridade, ordenar por prazo
    const diasA = calcularDiasRestantes(a.prazo_retorno) ?? 999;
    const diasB = calcularDiasRestantes(b.prazo_retorno) ?? 999;

    return diasA - diasB;
  });
}

// ============================================================================
// REMOÇÃO E ARQUIVAMENTO
// ============================================================================

/**
 * Remove pedidos atendidos da lista ativa
 * Mantém no histórico
 */
export function removerPedidosAtendidos(
  pedidos: PedidoDiretorConsolidado[]
): {
  ativos: PedidoDiretorConsolidado[];
  arquivados: PedidoDiretorConsolidado[];
} {
  const ativos = pedidos.filter(p => p.status_pedido !== 'Atendido');
  const arquivados = pedidos.filter(p => p.status_pedido === 'Atendido');

  return { ativos, arquivados };
}

// ============================================================================
// ESTATÍSTICAS
// ============================================================================

/**
 * Calcula estatísticas consolidadas do dashboard
 */
export function calcularEstatisticas(
  pedidos: PedidoDiretorConsolidado[]
): {
  total: number;
  atendidos: number;
  em_andamento: number;
  atrasados: number;
  pendentes: number;
  por_area: Record<string, number>;
} {
  const estatisticas = {
    total: pedidos.length,
    atendidos: 0,
    em_andamento: 0,
    atrasados: 0,
    pendentes: 0,
    por_area: {} as Record<string, number>
  };

  pedidos.forEach(pedido => {
    // Contadores por status
    if (pedido.status_pedido === 'Atendido') {
      estatisticas.atendidos++;
    } else if (pedido.status_pedido === 'Em andamento') {
      estatisticas.em_andamento++;
    } else if (pedido.status_pedido === 'Pendente') {
      estatisticas.pendentes++;
    }

    // Pedidos atrasados
    if (calcularStatusAlerta(pedido) === 'vermelho') {
      estatisticas.atrasados++;
    }

    // Contadores por área
    estatisticas.por_area[pedido.area] = (estatisticas.por_area[pedido.area] || 0) + 1;
  });

  return estatisticas;
}

/**
 * Exporta dados para formato de relatório
 */
export function exportarParaRelatorio(
  pedidos: PedidoDiretorConsolidado[]
): {
  data: any[];
  resumo: string;
} {
  const stats = calcularEstatisticas(pedidos);

  const data = pedidos.map(p => ({
    area: p.area,
    projeto: p.projeto,
    descricao: p.descricao_pedido,
    data_pedido: p.data_pedido,
    prazo: p.prazo_retorno,
    status: p.status_pedido,
    responsavel: p.responsavel_area,
    alerta: getIconeAlerta(calcularStatusAlerta(p)),
    dias_restantes: formatarDiasRestantes(calcularDiasRestantes(p.prazo_retorno))
  }));

  const resumo = `
📊 Resumo Executivo do Dashboard
─────────────────────────────────
Total de pedidos: ${stats.total}
✅ Atendidos: ${stats.atendidos}
🟡 Em andamento: ${stats.em_andamento}
🔴 Atrasados: ${stats.atrasados}
⚪ Pendentes: ${stats.pendentes}

📍 Por área:
${Object.entries(stats.por_area)
  .map(([area, count]) => `  ${area}: ${count}`)
  .join('\n')}
  `.trim();

  return { data, resumo };
}
