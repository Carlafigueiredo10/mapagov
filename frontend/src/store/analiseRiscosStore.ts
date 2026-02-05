/**
 * Store Zustand para Analise de Riscos
 *
 * Segue padrao de chatStore.ts com persist
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  AnaliseRiscos,
  CategoriaRisco,
  EstrategiaResposta,
  ModoEntrada,
  TipoOrigem,
  ContextoEstruturado,
} from '../types/analiseRiscos.types';
import * as api from '../services/analiseRiscosApi';

// ============================================================================
// Estado
// ============================================================================

interface AnaliseRiscosState {
  // Estado
  currentAnaliseId: string | null;
  currentAnalise: AnaliseRiscos | null;
  analises: Array<{
    id: string;
    tipo_origem: string;
    status: string;
    etapa_atual: number;
    area_decipex?: string;
    criado_em: string;
  }>;
  loading: boolean;
  error: { erro: string; codigo?: string } | null;

  // Actions
  criarAnalise: (tipoOrigem: string, origemId: string) => Promise<string | null>;
  listarAnalises: () => Promise<void>;
  carregarAnalise: (analiseId: string) => Promise<void>;
  salvarQuestionario: (
    questoesRespondidas?: Record<string, string>,
    areaDecipex?: string,
    etapaAtual?: number
  ) => Promise<void>;
  mudarEtapa: (etapa: number) => Promise<void>;
  adicionarRisco: (
    titulo: string,
    descricao?: string,
    categoria?: CategoriaRisco,
    probabilidade?: number,
    impacto?: number
  ) => Promise<string | null>;
  analisarRisco: (
    riscoId: string,
    probabilidade?: number,
    impacto?: number
  ) => Promise<void>;
  removerRisco: (riscoId: string) => Promise<void>;
  adicionarResposta: (
    riscoId: string,
    estrategia: EstrategiaResposta,
    descricaoAcao?: string,
    responsavelNome?: string,
    responsavelArea?: string,
    prazo?: string
  ) => Promise<void>;
  finalizarAnalise: () => Promise<void>;
  limparErro: () => void;
  resetStore: () => void;

  // Actions v2
  criarAnaliseV2: (modoEntrada: ModoEntrada, tipoOrigem: TipoOrigem, origemId?: string) => Promise<string | null>;
  salvarContexto: (contexto: ContextoEstruturado, validar?: boolean) => Promise<boolean>;
  salvarBlocos: (blocos: Record<string, Record<string, string | string[]>>) => Promise<boolean>;
  inferirRiscos: () => Promise<number>;
}

// ============================================================================
// Store
// ============================================================================

export const useAnaliseRiscosStore = create<AnaliseRiscosState>()(
  persist(
    (set, get) => ({
      // Estado inicial
      currentAnaliseId: null,
      currentAnalise: null,
      analises: [],
      loading: false,
      error: null,

      // Criar nova analise
      criarAnalise: async (tipoOrigem, origemId) => {
        set({ loading: true, error: null });
        try {
          const response = await api.criarAnalise({
            tipo_origem: tipoOrigem,
            origem_id: origemId,
          });
          const novoId = response.dados.id;
          set({
            currentAnaliseId: novoId,
            loading: false,
          });
          // Recarregar lista
          await get().listarAnalises();
          return novoId;
        } catch (err: unknown) {
          const error = err as { response?: { data?: { erro?: string; codigo?: string } } };
          set({
            loading: false,
            error: error.response?.data || { erro: 'Erro ao criar analise' },
          });
          return null;
        }
      },

      // Listar analises
      listarAnalises: async () => {
        set({ loading: true, error: null });
        try {
          const response = await api.listarAnalises();
          set({
            analises: response.dados.analises,
            loading: false,
          });
        } catch (err: unknown) {
          const error = err as { response?: { data?: { erro?: string; codigo?: string } } };
          set({
            loading: false,
            error: error.response?.data || { erro: 'Erro ao listar analises' },
          });
        }
      },

      // Carregar analise especifica
      carregarAnalise: async (analiseId) => {
        set({ loading: true, error: null });
        try {
          const response = await api.detalharAnalise(analiseId);
          set({
            currentAnaliseId: analiseId,
            currentAnalise: response.dados,
            loading: false,
          });
        } catch (err: unknown) {
          const error = err as { response?: { data?: { erro?: string; codigo?: string } } };
          set({
            loading: false,
            error: error.response?.data || { erro: 'Erro ao carregar analise' },
          });
        }
      },

      // Salvar questionario
      salvarQuestionario: async (questoesRespondidas, areaDecipex, etapaAtual) => {
        const { currentAnaliseId } = get();
        if (!currentAnaliseId) return;

        set({ loading: true, error: null });
        try {
          await api.atualizarQuestionario(currentAnaliseId, {
            questoes_respondidas: questoesRespondidas,
            area_decipex: areaDecipex,
            etapa_atual: etapaAtual,
          });
          // Recarregar analise
          await get().carregarAnalise(currentAnaliseId);
        } catch (err: unknown) {
          const error = err as { response?: { data?: { erro?: string; codigo?: string } } };
          set({
            loading: false,
            error: error.response?.data || { erro: 'Erro ao salvar questionario' },
          });
        }
      },

      // Mudar etapa
      mudarEtapa: async (etapa) => {
        const { currentAnaliseId } = get();
        if (!currentAnaliseId) return;

        set({ loading: true, error: null });
        try {
          await api.atualizarEtapa(currentAnaliseId, { etapa });
          // Recarregar analise
          await get().carregarAnalise(currentAnaliseId);
        } catch (err: unknown) {
          const error = err as { response?: { data?: { erro?: string; codigo?: string } } };
          set({
            loading: false,
            error: error.response?.data || { erro: 'Erro ao mudar etapa' },
          });
        }
      },

      // Adicionar risco
      adicionarRisco: async (titulo, descricao, categoria, probabilidade, impacto) => {
        const { currentAnaliseId } = get();
        if (!currentAnaliseId) return null;

        set({ loading: true, error: null });
        try {
          const response = await api.adicionarRisco(currentAnaliseId, {
            titulo,
            descricao,
            categoria,
            probabilidade,
            impacto,
          });
          // Recarregar analise
          await get().carregarAnalise(currentAnaliseId);
          return response.dados.id;
        } catch (err: unknown) {
          const error = err as { response?: { data?: { erro?: string; codigo?: string } } };
          set({
            loading: false,
            error: error.response?.data || { erro: 'Erro ao adicionar risco' },
          });
          return null;
        }
      },

      // Analisar risco (prob/impacto)
      analisarRisco: async (riscoId, probabilidade, impacto) => {
        const { currentAnaliseId } = get();
        if (!currentAnaliseId) return;

        set({ loading: true, error: null });
        try {
          await api.analisarRisco(currentAnaliseId, riscoId, {
            probabilidade,
            impacto,
          });
          // Recarregar analise
          await get().carregarAnalise(currentAnaliseId);
        } catch (err: unknown) {
          const error = err as { response?: { data?: { erro?: string; codigo?: string } } };
          set({
            loading: false,
            error: error.response?.data || { erro: 'Erro ao analisar risco' },
          });
        }
      },

      // Remover risco
      removerRisco: async (riscoId) => {
        const { currentAnaliseId } = get();
        if (!currentAnaliseId) return;

        set({ loading: true, error: null });
        try {
          await api.removerRisco(currentAnaliseId, riscoId);
          // Recarregar analise
          await get().carregarAnalise(currentAnaliseId);
        } catch (err: unknown) {
          const error = err as { response?: { data?: { erro?: string; codigo?: string } } };
          set({
            loading: false,
            error: error.response?.data || { erro: 'Erro ao remover risco' },
          });
        }
      },

      // Adicionar resposta ao risco
      adicionarResposta: async (
        riscoId,
        estrategia,
        descricaoAcao,
        responsavelNome,
        responsavelArea,
        prazo
      ) => {
        const { currentAnaliseId } = get();
        if (!currentAnaliseId) return;

        set({ loading: true, error: null });
        try {
          await api.adicionarResposta(currentAnaliseId, riscoId, {
            estrategia,
            descricao_acao: descricaoAcao,
            responsavel_nome: responsavelNome,
            responsavel_area: responsavelArea,
            prazo,
          });
          // Recarregar analise
          await get().carregarAnalise(currentAnaliseId);
        } catch (err: unknown) {
          const error = err as { response?: { data?: { erro?: string; codigo?: string } } };
          set({
            loading: false,
            error: error.response?.data || { erro: 'Erro ao adicionar resposta' },
          });
        }
      },

      // Finalizar analise
      finalizarAnalise: async () => {
        const { currentAnaliseId } = get();
        if (!currentAnaliseId) return;

        set({ loading: true, error: null });
        try {
          await api.finalizarAnalise(currentAnaliseId);
          // Recarregar analise
          await get().carregarAnalise(currentAnaliseId);
        } catch (err: unknown) {
          const error = err as { response?: { data?: { erro?: string; codigo?: string } } };
          set({
            loading: false,
            error: error.response?.data || { erro: 'Erro ao finalizar analise' },
          });
        }
      },

      // Limpar erro
      limparErro: () => set({ error: null }),

      // Reset completo
      resetStore: () =>
        set({
          currentAnaliseId: null,
          currentAnalise: null,
          analises: [],
          loading: false,
          error: null,
        }),

      // ========================================
      // Actions v2
      // ========================================

      // Criar analise v2
      criarAnaliseV2: async (modoEntrada, tipoOrigem, origemId) => {
        set({ loading: true, error: null });
        try {
          const response = await api.criarAnaliseV2({
            modo_entrada: modoEntrada,
            tipo_origem: tipoOrigem,
            origem_id: origemId,
          });
          const novoId = response.dados.id;
          // Manter loading=true enquanto carrega os dados da analise criada
          set({ currentAnaliseId: novoId });

          // Carregar dados completos da analise
          const analiseResponse = await api.detalharAnalise(novoId);
          set({
            currentAnalise: analiseResponse.dados,
            loading: false,
          });

          return novoId;
        } catch (err: unknown) {
          const error = err as { response?: { data?: { erro?: string; codigo?: string } } };
          set({
            loading: false,
            error: { erro: error.response?.data?.erro || 'Erro ao criar analise', codigo: error.response?.data?.codigo },
          });
          return null;
        }
      },

      // Salvar contexto (validar=true para exigir contexto minimo)
      salvarContexto: async (contexto, validar = true) => {
        const { currentAnaliseId } = get();
        if (!currentAnaliseId) return false;

        set({ loading: true, error: null });
        try {
          await api.salvarContexto(currentAnaliseId, {
            contexto_estruturado: contexto,
            validar,  // Backend so valida se true
          });
          await get().carregarAnalise(currentAnaliseId);
          return true;
        } catch (err: unknown) {
          const error = err as { response?: { data?: { erro?: string; codigo?: string } } };
          set({
            loading: false,
            error: { erro: error.response?.data?.erro || 'Erro ao salvar contexto', codigo: error.response?.data?.codigo },
          });
          return false;
        }
      },

      // Salvar blocos
      salvarBlocos: async (blocos) => {
        const { currentAnaliseId } = get();
        if (!currentAnaliseId) return false;

        set({ loading: true, error: null });
        try {
          await api.salvarBlocos(currentAnaliseId, { respostas_blocos: blocos });
          await get().carregarAnalise(currentAnaliseId);
          return true;
        } catch (err: unknown) {
          const error = err as { response?: { data?: { erro?: string; codigo?: string } } };
          set({
            loading: false,
            error: { erro: error.response?.data?.erro || 'Erro ao salvar blocos', codigo: error.response?.data?.codigo },
          });
          return false;
        }
      },

      // Inferir riscos
      inferirRiscos: async () => {
        const { currentAnaliseId } = get();
        if (!currentAnaliseId) return 0;

        set({ loading: true, error: null });
        try {
          const response = await api.inferirRiscos(currentAnaliseId);
          await get().carregarAnalise(currentAnaliseId);
          return response.dados.riscos_criados;
        } catch (err: unknown) {
          const error = err as { response?: { data?: { erro?: string; codigo?: string } } };
          set({
            loading: false,
            error: { erro: error.response?.data?.erro || 'Erro ao inferir riscos', codigo: error.response?.data?.codigo },
          });
          return 0;
        }
      },
    }),
    {
      name: 'analise-riscos-storage',
      partialize: (state) => ({
        currentAnaliseId: state.currentAnaliseId,
        analises: state.analises,
      }),
    }
  )
);
