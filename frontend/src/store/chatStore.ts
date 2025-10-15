import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { HelenaMessage } from '../types/simples';

export interface DadosPOP {
  area?: { codigo: string; nome: string };
  codigo_processo?: string;
  nome_processo?: string;
  processo_especifico?: string;
  entrega_esperada?: string;
  dispositivos_normativos?: string;
  sistemas?: string[];
  operadores?: string;
  etapas?: Array<{ descricao: string; responsavel: string }>;
  documentos_utilizados?: string;
  pontos_atencao?: string;
  fluxos_entrada?: string[];
  fluxos_saida?: string[];
}

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
  modoRevisao: boolean;
  
  // Actions básicas
  addMessage: (message: HelenaMessage) => void;
  removeMessage: (id: string) => void;
  setProcessing: (status: boolean) => void;
  updateProgresso: (atual: number, texto: string) => void;
  resetChat: () => void;
  
  // Actions do POP
  updateDadosPOP: (dados: Partial<DadosPOP>) => void;
  setModoRevisao: (valor: boolean) => void;
  
  // Helpers
  adicionarMensagemRapida: (tipo: 'usuario' | 'helena', texto: string, opcoes?: Record<string, unknown>) => string;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      // Estado inicial
      messages: [],
      sessionId: `user_${Date.now()}`,
      isProcessing: false,
      progresso: { atual: 0, total: 10, texto: '0/10 - Vamos começar!' },
      dadosPOP: {},
      historicoCompleto: [],
      modoRevisao: false,

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
          sessionId: `user_${Date.now()}`,
          progresso: { atual: 0, total: 10, texto: '0/10 - Vamos começar!' },
          dadosPOP: {},
          historicoCompleto: [],
          modoRevisao: false,
        }),

      // Actions do POP
      updateDadosPOP: (novosDados) =>
        set((state) => ({
          dadosPOP: { ...state.dadosPOP, ...novosDados },
        })),

      setModoRevisao: (valor) => set({ modoRevisao: valor }),

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
      }),
    }
  )
);