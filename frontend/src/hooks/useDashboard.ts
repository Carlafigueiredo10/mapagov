/**
 * useDashboard - Hook para gerenciar Dashboards
 * Helena PE - Sistema de Governança
 *
 * Gerencia estado de projetos e pedidos com sincronização automática
 */

import { useState, useEffect, useCallback } from 'react';
import {
  ProjetoEstrategico,
  PedidoDiretorConsolidado,
  FiltrosDashboard,
  EstatisticasDashboard
} from '../types/dashboard';
import {
  sincronizarParaDiretor,
  calcularEstatisticas,
  filtrarPedidos,
  ordenarPorPrioridade,
  removerPedidosAtendidos
} from '../utils/dashboardSync';

// ============================================================================
// TIPOS
// ============================================================================

interface UseDashboardState {
  // Dados
  projetos: ProjetoEstrategico[];
  pedidos: PedidoDiretorConsolidado[];
  pedidosArquivados: PedidoDiretorConsolidado[];

  // Filtros
  filtros: FiltrosDashboard;

  // Estatísticas
  estatisticas: EstatisticasDashboard | null;

  // Estado
  isLoading: boolean;
  erro: string | null;
}

interface UseDashboardActions {
  // Projetos
  adicionarProjeto: (projeto: ProjetoEstrategico) => void;
  atualizarProjeto: (id: string, projeto: Partial<ProjetoEstrategico>) => void;
  removerProjeto: (id: string) => void;

  // Pedidos
  sincronizarPedidos: () => void;

  // Filtros
  aplicarFiltros: (filtros: FiltrosDashboard) => void;
  limparFiltros: () => void;

  // Exportação
  exportarDados: () => { projetos: ProjetoEstrategico[]; pedidos: PedidoDiretorConsolidado[] };

  // Utilidades
  recarregar: () => Promise<void>;
}

// ============================================================================
// HOOK PRINCIPAL
// ============================================================================

export const useDashboard = (): UseDashboardState & UseDashboardActions => {
  const [state, setState] = useState<UseDashboardState>({
    projetos: [],
    pedidos: [],
    pedidosArquivados: [],
    filtros: {},
    estatisticas: null,
    isLoading: false,
    erro: null
  });

  // ============================================================================
  // INICIALIZAÇÃO E PERSISTÊNCIA
  // ============================================================================

  /**
   * Carrega dados do localStorage ao montar
   */
  useEffect(() => {
    const carregarDados = () => {
      try {
        const projetosStr = localStorage.getItem('helena_dashboard_projetos');
        const pedidosStr = localStorage.getItem('helena_dashboard_pedidos');

        if (projetosStr) {
          const projetos = JSON.parse(projetosStr);
          setState(prev => ({ ...prev, projetos }));
        }

        if (pedidosStr) {
          const pedidos = JSON.parse(pedidosStr);
          setState(prev => ({ ...prev, pedidos }));
        }
      } catch (error) {
        console.error('[useDashboard] Erro ao carregar dados:', error);
        setState(prev => ({ ...prev, erro: 'Erro ao carregar dados salvos' }));
      }
    };

    carregarDados();
  }, []);

  /**
   * Persiste dados no localStorage quando mudarem
   */
  useEffect(() => {
    if (state.projetos.length > 0) {
      localStorage.setItem('helena_dashboard_projetos', JSON.stringify(state.projetos));
    }

    if (state.pedidos.length > 0) {
      localStorage.setItem('helena_dashboard_pedidos', JSON.stringify(state.pedidos));
    }
  }, [state.projetos, state.pedidos]);

  /**
   * Calcula estatísticas quando dados mudarem
   */
  useEffect(() => {
    const stats: EstatisticasDashboard = {
      total_projetos: state.projetos.length,
      total_pedidos: state.pedidos.length,
      pedidos_atendidos: state.pedidos.filter(p => p.status_pedido === 'Atendido').length,
      pedidos_em_andamento: state.pedidos.filter(p => p.status_pedido === 'Em andamento').length,
      pedidos_atrasados: calcularEstatisticas(state.pedidos).atrasados,
      projetos_por_fase: {},
      andamento_medio: 0
    };

    // Calcular projetos por fase
    state.projetos.forEach(proj => {
      stats.projetos_por_fase[proj.fase_atual] =
        (stats.projetos_por_fase[proj.fase_atual] || 0) + 1;
    });

    // Calcular andamento médio
    if (state.projetos.length > 0) {
      const somaAndamento = state.projetos.reduce((acc, proj) => acc + proj.andamento, 0);
      stats.andamento_medio = Math.round(somaAndamento / state.projetos.length);
    }

    setState(prev => ({ ...prev, estatisticas: stats }));
  }, [state.projetos, state.pedidos]);

  // ============================================================================
  // AÇÕES - PROJETOS
  // ============================================================================

  const adicionarProjeto = useCallback((projeto: ProjetoEstrategico) => {
    setState(prev => ({
      ...prev,
      projetos: [...prev.projetos, projeto]
    }));
  }, []);

  const atualizarProjeto = useCallback(
    (id: string, atualizacao: Partial<ProjetoEstrategico>) => {
      setState(prev => {
        const projetos = prev.projetos.map(proj => {
          if (proj.id_projeto !== id) return proj;

          // Criar entrada no histórico
          const novaAtualizacao: ProjetoEstrategico = {
            ...proj,
            ...atualizacao,
            historico_atualizacoes: [
              ...proj.historico_atualizacoes,
              {
                data: new Date().toISOString().split('T')[0],
                responsavel: atualizacao.ultima_atualizacao?.responsavel || proj.ultima_atualizacao.responsavel,
                alteracoes: Object.keys(atualizacao).map(
                  key => `${key} atualizado`
                ),
                observacoes: 'Atualização via dashboard'
              }
            ]
          };

          return novaAtualizacao;
        });

        return { ...prev, projetos };
      });

      // Sincronizar com Dashboard do Diretor
      sincronizarPedidos();
    },
    []
  );

  const removerProjeto = useCallback((id: string) => {
    setState(prev => ({
      ...prev,
      projetos: prev.projetos.filter(p => p.id_projeto !== id)
    }));
  }, []);

  // ============================================================================
  // AÇÕES - PEDIDOS
  // ============================================================================

  const sincronizarPedidos = useCallback(() => {
    setState(prev => {
      const pedidosAtualizados: PedidoDiretorConsolidado[] = [];

      // Sincronizar cada projeto que tenha pedido do diretor
      prev.projetos.forEach(projeto => {
        if (projeto.pedido_diretor.existe) {
          const pedidoConsolidado = sincronizarParaDiretor(projeto, prev.pedidos);
          if (pedidoConsolidado) {
            pedidosAtualizados.push(pedidoConsolidado);
          }
        }
      });

      // Manter pedidos existentes que não foram atualizados
      const idsAtualizados = new Set(pedidosAtualizados.map(p => p.id_pedido));
      const pedidosNaoAtualizados = prev.pedidos.filter(p => !idsAtualizados.has(p.id_pedido));

      const todosPedidos = [...pedidosNaoAtualizados, ...pedidosAtualizados];

      // Separar ativos e arquivados
      const { ativos, arquivados } = removerPedidosAtendidos(todosPedidos);

      return {
        ...prev,
        pedidos: ordenarPorPrioridade(ativos),
        pedidosArquivados: arquivados
      };
    });
  }, []);

  /**
   * Sincroniza automaticamente quando projetos mudarem
   */
  useEffect(() => {
    sincronizarPedidos();
  }, [state.projetos.length]); // Só dispara quando número de projetos mudar

  // ============================================================================
  // AÇÕES - FILTROS
  // ============================================================================

  const aplicarFiltros = useCallback((filtros: FiltrosDashboard) => {
    setState(prev => ({ ...prev, filtros }));
  }, []);

  const limparFiltros = useCallback(() => {
    setState(prev => ({ ...prev, filtros: {} }));
  }, []);

  // ============================================================================
  // AÇÕES - EXPORTAÇÃO
  // ============================================================================

  const exportarDados = useCallback(() => {
    return {
      projetos: state.projetos,
      pedidos: state.pedidos
    };
  }, [state.projetos, state.pedidos]);

  // ============================================================================
  // AÇÕES - UTILIDADES
  // ============================================================================

  const recarregar = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, erro: null }));

    try {
      // Aqui você pode adicionar lógica para buscar dados do backend
      // Por enquanto, apenas recarrega do localStorage
      const projetosStr = localStorage.getItem('helena_dashboard_projetos');
      const pedidosStr = localStorage.getItem('helena_dashboard_pedidos');

      const projetos = projetosStr ? JSON.parse(projetosStr) : [];
      const pedidos = pedidosStr ? JSON.parse(pedidosStr) : [];

      setState(prev => ({
        ...prev,
        projetos,
        pedidos,
        isLoading: false
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        erro: 'Erro ao recarregar dados'
      }));
    }
  }, []);

  // ============================================================================
  // RETORNO
  // ============================================================================

  return {
    // Estado
    ...state,

    // Ações
    adicionarProjeto,
    atualizarProjeto,
    removerProjeto,
    sincronizarPedidos,
    aplicarFiltros,
    limparFiltros,
    exportarDados,
    recarregar
  };
};

export default useDashboard;
