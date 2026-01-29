// riscosStore.ts - Store Zustand para Análise de Riscos
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type {
  AnaliseRiscosState,
  POPInfo,
  ChatMessage,
  AnswersMap,
  RelatorioRiscos,
} from '../components/AnaliseRiscos/types';

interface RiscosStore extends AnaliseRiscosState {
  // Actions - Upload/Seleção
  setPOPFromUpload: (text: string, info: POPInfo) => void;
  setPOPFromExisting: (info: POPInfo) => void;
  clearPOP: () => void;

  // Actions - Chat
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  setCurrentQuestion: (index: number) => void;
  saveAnswer: (questionId: number, value: string | Record<string, string>) => void;
  setIsAnswering: (isAnswering: boolean) => void;

  // Actions - Análise
  startAnalysis: () => void;
  setAnalysisProgress: (progress: number) => void;
  setRelatorio: (relatorio: RelatorioRiscos) => void;
  finishAnalysis: () => void;

  // Actions - PDF
  startPDFGeneration: () => void;
  setPDFUrl: (url: string) => void;
  finishPDFGeneration: () => void;

  // Actions - Navegação
  setStep: (step: AnaliseRiscosState['currentStep']) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState: AnaliseRiscosState = {
  popText: '',
  popInfo: null,
  popSourceType: null,
  messages: [],
  currentQuestionIndex: 0,
  answers: {},
  isAnswering: false,
  isAnalyzing: false,
  analysisProgress: 0,
  relatorio: null,
  isGeneratingPDF: false,
  pdfUrl: null,
  currentStep: 'upload',
  error: null,
};

export const useRiscosStore = create<RiscosStore>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // Upload/Seleção
        setPOPFromUpload: (text, info) =>
          set({
            popText: text,
            popInfo: info,
            popSourceType: 'upload',
            currentStep: 'chat',
            error: null,
            messages: [
              {
                id: crypto.randomUUID(),
                role: 'helena',
                content: `Olá! 👋 Recebi o POP "${info.titulo}". Vou te fazer 20 perguntas para analisar os riscos de forma completa. Pronto para começar?`,
                timestamp: new Date(),
              },
            ],
          }),

        setPOPFromExisting: (info) =>
          set({
            popInfo: info,
            popSourceType: 'existing',
            currentStep: 'chat',
            error: null,
            messages: [
              {
                id: crypto.randomUUID(),
                role: 'helena',
                content: `Olá! 👋 Selecionaste o POP "${info.titulo}". Vou te fazer 20 perguntas para analisar os riscos. Vamos começar?`,
                timestamp: new Date(),
              },
            ],
          }),

        clearPOP: () =>
          set({
            popText: '',
            popInfo: null,
            popSourceType: null,
            messages: [],
            answers: {},
            currentQuestionIndex: 0,
          }),

        // Chat
        addMessage: (message) =>
          set((state) => ({
            messages: [
              ...state.messages,
              {
                ...message,
                id: crypto.randomUUID(),
                timestamp: new Date(),
              },
            ],
          })),

        setCurrentQuestion: (index) =>
          set({ currentQuestionIndex: index }),

        saveAnswer: (questionId, value) =>
          set((state) => ({
            answers: {
              ...state.answers,
              [questionId]: value,
            },
          })),

        setIsAnswering: (isAnswering) => set({ isAnswering }),

        // Análise
        startAnalysis: () =>
          set({
            isAnalyzing: true,
            analysisProgress: 0,
            currentStep: 'relatorio',
            error: null,
          }),

        setAnalysisProgress: (progress) =>
          set({ analysisProgress: progress }),

        setRelatorio: (relatorio) =>
          set({ relatorio }),

        finishAnalysis: () =>
          set({
            isAnalyzing: false,
            analysisProgress: 100,
          }),

        // PDF
        startPDFGeneration: () =>
          set({
            isGeneratingPDF: true,
            pdfUrl: null,
            error: null,
          }),

        setPDFUrl: (url) =>
          set({
            pdfUrl: url,
            currentStep: 'pdf',
          }),

        finishPDFGeneration: () =>
          set({ isGeneratingPDF: false }),

        // Navegação
        setStep: (step) => set({ currentStep: step }),

        setError: (error) => set({ error }),

        reset: () => set(initialState),
      }),
      {
        name: 'riscos-storage',
        partialize: (state) => ({
          // Persistir apenas dados essenciais
          popInfo: state.popInfo,
          answers: state.answers,
          currentQuestionIndex: state.currentQuestionIndex,
        }),
      }
    ),
    { name: 'RiscosStore' }
  )
);
