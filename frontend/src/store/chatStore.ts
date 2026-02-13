import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { HelenaMessage } from '../types/simples';
import type { Etapa } from '../types/pop.types';

// Helper para gerar UUID v4 válido
function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

export interface DadosPOP {
  // Usuário
  nome_usuario?: string;
  // Identificação e Arquitetura
  area?: { codigo: string; nome: string };
  codigo_cap?: string;  // ✅ FASE 2: CAP (Código na Arquitetura de Processos)
  codigo_processo?: string;
  macroprocesso?: string;  // ✅ FASE 2: Campos da arquitetura
  processo?: string;
  subprocesso?: string;
  atividade?: string;

  // Dados do processo
  nome_processo?: string;
  processo_especifico?: string;
  entrega_esperada?: string;
  dispositivos_normativos?: string;
  sistemas?: string[];
  operadores?: string[];  // ✅ Agora é lista igual sistemas
  etapas?: Etapa[];
  documentos_utilizados?: Array<{
    tipo_documento: string;
    descricao: string;
    tipo_uso: string;
    obrigatorio: boolean;
    sistema: string;
  }>;
  pontos_atencao?: string;
  fluxos_entrada?: string[];
  fluxos_saida?: string[];
}

export type ViewMode = 'landing' | 'chat_canvas' | 'final_review';

interface HistoricoItem {
  timestamp: string;
  tipo: 'usuario' | 'helena';
  mensagem: string;
  [key: string]: unknown;
}

interface ChatState {
  // Estado das mensagens
  messages: HelenaMessage[];
  sessionId: string;
  isProcessing: boolean;
  progresso: {
    atual: number;
    total: number;
    texto: string;
  };
  
  // Dados do formulário POP
  dadosPOP: DadosPOP;
  
  // Histórico e revisão
  historicoCompleto: HistoricoItem[];
  viewMode: ViewMode;

  // Backend POP identifiers
  popId: number | null;
  popUuid: string | null;
  integrityHash: string | null;

  // Estado atual da máquina de estados (stepper)
  estadoAtual: string;

  // Modo ajuda (não persistido)
  modoAjudaAtivo: boolean;

  // Actions básicas
  addMessage: (message: HelenaMessage) => void;
  removeMessage: (id: string) => void;
  setProcessing: (status: boolean) => void;
  updateProgresso: (atual: number, texto: string) => void;
  resetChat: () => void;
  carregarHistorico: (mensagens: Array<{
    role: string;
    content: string;
    metadados?: Record<string, unknown>;
    criado_em?: string
  }>) => void;

  // Actions do POP
  updateDadosPOP: (dados: Partial<DadosPOP>) => void;
  setViewMode: (mode: ViewMode) => void;
  setPopIdentifiers: (id: number, uuid: string, hash: string) => void;
  setEstadoAtual: (estado: string) => void;
  setModoAjudaAtivo: (ativo: boolean) => void;

  // UI
  fullscreenChat: boolean;
  setFullscreenChat: (value: boolean) => void;

  // Sincronização "Entendi" (card educativo)
  entendeuClassificacao: boolean;
  sinalizarEntendi: () => void;
  resetEntendeuClassificacao: () => void;

  // Helpers
  adicionarMensagemRapida: (tipo: 'usuario' | 'helena', texto: string, opcoes?: Record<string, unknown>) => string;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      // Estado inicial
      messages: [],
      sessionId: generateUUID(), // Gera UUID v4 válido
      isProcessing: false,
      progresso: { atual: 0, total: 10, texto: 'Etapa 0 de 10 · Início do mapeamento' },
      dadosPOP: {},
      historicoCompleto: [],
      viewMode: 'landing' as ViewMode,
      fullscreenChat: false,
      popId: null,
      popUuid: null,
      integrityHash: null,
      estadoAtual: 'nome_usuario',
      modoAjudaAtivo: false,

      // Actions básicas
      addMessage: (message) =>
        set((state) => ({
          messages: [...state.messages, message],
        })),

      removeMessage: (id) =>
        set((state) => ({
          messages: state.messages.filter((m) => m.id !== id),
        })),

      setProcessing: (status) => set({ isProcessing: status }),

      updateProgresso: (atual, texto) =>
        set((state) => ({
          progresso: { ...state.progresso, atual, texto },
        })),

      resetChat: () =>
        set({
          messages: [],
          sessionId: generateUUID(), // Gera novo UUID v4 válido
          progresso: { atual: 0, total: 10, texto: 'Etapa 0 de 10 · Início do mapeamento' },
          dadosPOP: {},
          historicoCompleto: [],
          viewMode: 'chat_canvas' as ViewMode,
          popId: null,
          popUuid: null,
          integrityHash: null,
          estadoAtual: 'nome_usuario',
          modoAjudaAtivo: false,
        }),

      carregarHistorico: (mensagens) => {
        const helenaMessages: HelenaMessage[] = mensagens.map((msg, idx) => {
          // ✅ BUGFIX: Recuperar interface completa dos metadados
          const tipoInterface = msg.metadados?.tipo_interface;
          const dadosInterface = msg.metadados?.dados_interface;

          return {
            id: `history_${Date.now()}_${idx}`,
            tipo: msg.role === 'user' ? 'usuario' : 'helena',
            mensagem: msg.content,
            timestamp: msg.criado_em || new Date().toISOString(),
            // ✅ Restaurar interface se existir nos metadados
            ...(tipoInterface && {
              interface: {
                tipo: tipoInterface,
                dados: dadosInterface || {}
              }
            }),
            // ✅ Restaurar metadados completos (exceto interface para evitar duplicação)
            ...(msg.metadados && {
              metadados: Object.fromEntries(
                Object.entries(msg.metadados).filter(
                  ([key]) => key !== 'tipo_interface' && key !== 'dados_interface'
                )
              )
            })
          };
        });

        set({ messages: helenaMessages });
      },

      // Actions do POP
      updateDadosPOP: (novosDados) =>
        set((state) => ({
          dadosPOP: { ...state.dadosPOP, ...novosDados },
        })),

      setViewMode: (mode) => set({ viewMode: mode }),
      setFullscreenChat: (value) => set({ fullscreenChat: value }),

      setPopIdentifiers: (id, uuid, hash) => set({
        popId: id,
        popUuid: uuid,
        integrityHash: hash,
      }),

      setEstadoAtual: (estado) => set({ estadoAtual: estado }),
      setModoAjudaAtivo: (ativo) => set({ modoAjudaAtivo: ativo }),

      // Sincronização "Entendi" (card educativo)
      entendeuClassificacao: false,
      sinalizarEntendi: () => set({ entendeuClassificacao: true }),
      resetEntendeuClassificacao: () => set({ entendeuClassificacao: false }),

      // Helper para adicionar mensagem rapidamente
      adicionarMensagemRapida: (tipo, texto, opcoes = {}) => {
        const novaMensagem: HelenaMessage = {
          id: `msg_${Date.now()}_${Math.random()}`,
          tipo,
          mensagem: texto,
          timestamp: new Date().toISOString(),
          ...opcoes,
        };

        set((state) => ({
          messages: [...state.messages, novaMensagem],
          historicoCompleto: [
            ...state.historicoCompleto,
            {
              timestamp: novaMensagem.timestamp,
              tipo,
              mensagem: texto,
              ...opcoes,
            },
          ],
        }));

        return novaMensagem.id;
      },
    }),
    {
      name: 'helena-chat-storage',
      // Persistir apenas dados importantes
      partialize: (state) => ({
        dadosPOP: state.dadosPOP,
        sessionId: state.sessionId,
        historicoCompleto: state.historicoCompleto,
        // Persistir mensagens renderizadas (últimas 50 para evitar overflow)
        messages: state.messages.slice(-50),
        // Backend POP identifiers
        popId: state.popId,
        popUuid: state.popUuid,
        integrityHash: state.integrityHash,
      }),
    }
  )
);