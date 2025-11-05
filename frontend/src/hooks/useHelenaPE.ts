/**
 * useHelenaPE - Hook React para Helena Planejamento Estratégico
 *
 * Gerencia estado da sessão, mensagens, auto-save e todas interações com backend
 * Fundação para todos os componentes da interface
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  helenaPEApi,
  SessionData,
  EstadoConversa,
  ModeloEstrategico,
  ProcessarResponse,
  Planejamento,
  ModeloConfig,
  PerguntaDiagnostico
} from '../services/helenaPEApi';

// ============================================================================
// TIPOS E INTERFACES
// ============================================================================

export interface Mensagem {
  id: string;
  tipo: 'usuario' | 'helena';
  texto: string;
  timestamp: Date;
  metadados?: {
    progresso?: string;
    percentual?: number;
    modelo_selecionado?: ModeloEstrategico;
  };
}

interface UseHelenaPEState {
  // Estado da sessão
  sessionData: SessionData | null;
  mensagens: Mensagem[];

  // Estado de carregamento
  isLoading: boolean;
  isInitialized: boolean;
  isSaving: boolean;

  // Dados auxiliares
  modelosDisponiveis: ModeloConfig[];
  perguntasDiagnostico: PerguntaDiagnostico[];

  // Planejamento salvo
  planejamentoId: number | null;
  ultimoSave: Date | null;

  // Erros
  erro: string | null;
}

interface UseHelenaPEActions {
  // Inicialização
  iniciarSessao: () => Promise<void>;

  // Envio de mensagens
  enviarMensagem: (texto: string) => Promise<void>;

  // Manipulação de modelo
  selecionarModelo: (modelo: ModeloEstrategico) => Promise<void>;
  selecionarModoEntrada: (modo: 'diagnostico' | 'explorar' | 'direto') => Promise<void>;

  // Diagnóstico
  responderDiagnostico: (perguntaId: string, resposta: string) => Promise<void>;

  // Salvamento
  salvarProgresso: () => Promise<number | null>;
  carregarPlanejamento: (id: number) => Promise<void>;

  // Utilidades
  resetarSessao: () => void;
  limparErro: () => void;
}

// ============================================================================
// HOOK PRINCIPAL
// ============================================================================

export const useHelenaPE = (): UseHelenaPEState & UseHelenaPEActions => {
  // Estado principal
  const [state, setState] = useState<UseHelenaPEState>({
    sessionData: null,
    mensagens: [],
    isLoading: false,
    isInitialized: false,
    isSaving: false,
    modelosDisponiveis: [],
    perguntasDiagnostico: [],
    planejamentoId: null,
    ultimoSave: null,
    erro: null
  });

  // Refs para auto-save
  const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null);
  const lastChangeRef = useRef<Date>(new Date());

  // ============================================================================
  // INICIALIZAÇÃO
  // ============================================================================

  const iniciarSessao = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, erro: null }));

    try {
      const response = await helenaPEApi.iniciar();

      // Criar mensagem inicial da Helena
      const mensagemInicial: Mensagem = {
        id: `helena-${Date.now()}`,
        tipo: 'helena',
        texto: response.mensagem_inicial,
        timestamp: new Date()
      };

      setState(prev => ({
        ...prev,
        sessionData: response.session_data,
        mensagens: [mensagemInicial],
        modelosDisponiveis: response.modelos_disponiveis,
        perguntasDiagnostico: response.perguntas_diagnostico,
        isLoading: false,
        isInitialized: true
      }));
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        erro: error.response?.data?.error || 'Erro ao iniciar sessão'
      }));
    }
  }, []);

  // ============================================================================
  // ENVIO DE MENSAGENS
  // ============================================================================

  const enviarMensagem = useCallback(async (texto: string) => {
    if (!state.sessionData) {
      setState(prev => ({ ...prev, erro: 'Sessão não inicializada' }));
      return;
    }

    // Adicionar mensagem do usuário
    const mensagemUsuario: Mensagem = {
      id: `user-${Date.now()}`,
      tipo: 'usuario',
      texto,
      timestamp: new Date()
    };

    setState(prev => ({
      ...prev,
      mensagens: [...prev.mensagens, mensagemUsuario],
      isLoading: true,
      erro: null
    }));

    try {
      const response = await helenaPEApi.processar(texto, state.sessionData);

      // Criar mensagem de resposta da Helena
      const mensagemHelena: Mensagem = {
        id: `helena-${Date.now()}`,
        tipo: 'helena',
        texto: response.resposta,
        timestamp: new Date(),
        metadados: {
          progresso: response.progresso,
          percentual: response.percentual_conclusao,
          modelo_selecionado: response.metadados.modelo_selecionado
        }
      };

      setState(prev => ({
        ...prev,
        sessionData: response.session_data,
        mensagens: [...prev.mensagens, mensagemHelena],
        isLoading: false
      }));

      // Marcar mudança para auto-save
      lastChangeRef.current = new Date();
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        erro: error.response?.data?.error || 'Erro ao processar mensagem'
      }));
    }
  }, [state.sessionData]);

  // ============================================================================
  // SELEÇÃO DE MODELO E MODO
  // ============================================================================

  const selecionarModelo = useCallback(async (modelo: ModeloEstrategico) => {
    if (!state.sessionData) return;

    await enviarMensagem(`Quero usar o modelo ${modelo}`);
  }, [state.sessionData, enviarMensagem]);

  const selecionarModoEntrada = useCallback(async (modo: 'diagnostico' | 'explorar' | 'direto') => {
    if (!state.sessionData) return;

    const mensagens = {
      diagnostico: 'Quero fazer o diagnóstico',
      explorar: 'Quero explorar os modelos',
      direto: 'Já sei qual modelo quero usar'
    };

    await enviarMensagem(mensagens[modo]);
  }, [state.sessionData, enviarMensagem]);

  // ============================================================================
  // DIAGNÓSTICO
  // ============================================================================

  const responderDiagnostico = useCallback(async (perguntaId: string, resposta: string) => {
    if (!state.sessionData) return;

    await enviarMensagem(resposta);
  }, [state.sessionData, enviarMensagem]);

  // ============================================================================
  // SALVAMENTO E CARREGAMENTO
  // ============================================================================

  const salvarProgresso = useCallback(async (): Promise<number | null> => {
    if (!state.sessionData) return null;

    setState(prev => ({ ...prev, isSaving: true, erro: null }));

    try {
      const response = await helenaPEApi.salvar(state.sessionData);

      setState(prev => ({
        ...prev,
        planejamentoId: response.planejamento_id,
        ultimoSave: new Date(),
        isSaving: false
      }));

      return response.planejamento_id;
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        isSaving: false,
        erro: error.response?.data?.error || 'Erro ao salvar progresso'
      }));
      return null;
    }
  }, [state.sessionData]);

  const carregarPlanejamento = useCallback(async (id: number) => {
    setState(prev => ({ ...prev, isLoading: true, erro: null }));

    try {
      const response = await helenaPEApi.obter(id);
      const planejamento = response.planejamento;

      // Reconstruir sessionData a partir do planejamento salvo
      const sessionData: SessionData = {
        estado_atual: planejamento.status === 'aprovado' ? 'finalizado' : 'construcao_modelo',
        modo_entrada: 'direto',
        diagnostico: planejamento.diagnostico,
        pontuacao_modelos: {} as Record<ModeloEstrategico, number>,
        modelos_recomendados: [planejamento.modelo],
        modelo_selecionado: planejamento.modelo,
        contexto_organizacional: {
          orgao: planejamento.orgao,
          unidade: planejamento.unidade,
          escopo: planejamento.escopo,
          titulo_planejamento: planejamento.titulo
        },
        estrutura_planejamento: planejamento.estrutura,
        percentual_conclusao: planejamento.percentual_conclusao,
        historico_conversa: []
      };

      // Criar mensagem inicial de carregamento
      const mensagemCarregamento: Mensagem = {
        id: `helena-${Date.now()}`,
        tipo: 'helena',
        texto: `Planejamento "${planejamento.titulo}" carregado com sucesso! Você pode continuar de onde parou.`,
        timestamp: new Date()
      };

      setState(prev => ({
        ...prev,
        sessionData,
        mensagens: [mensagemCarregamento],
        planejamentoId: id,
        isLoading: false,
        isInitialized: true
      }));
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        erro: error.response?.data?.error || 'Erro ao carregar planejamento'
      }));
    }
  }, []);

  // ============================================================================
  // UTILIDADES
  // ============================================================================

  const resetarSessao = useCallback(() => {
    if (autoSaveTimerRef.current) {
      clearInterval(autoSaveTimerRef.current);
      autoSaveTimerRef.current = null;
    }

    setState({
      sessionData: null,
      mensagens: [],
      isLoading: false,
      isInitialized: false,
      isSaving: false,
      modelosDisponiveis: [],
      perguntasDiagnostico: [],
      planejamentoId: null,
      ultimoSave: null,
      erro: null
    });
  }, []);

  const limparErro = useCallback(() => {
    setState(prev => ({ ...prev, erro: null }));
  }, []);

  // ============================================================================
  // AUTO-SAVE (a cada 5 segundos após mudança)
  // ============================================================================

  useEffect(() => {
    if (!state.isInitialized || !state.sessionData) return;

    // Configurar timer de auto-save
    autoSaveTimerRef.current = setInterval(() => {
      const agora = new Date();
      const tempoDesdeUltimaMudanca = agora.getTime() - lastChangeRef.current.getTime();

      // Se passou 5 segundos desde última mudança, salvar
      if (tempoDesdeUltimaMudanca >= 5000 && !state.isSaving) {
        salvarProgresso().catch(console.error);
        lastChangeRef.current = agora; // Reset timer
      }
    }, 1000); // Checar a cada segundo

    return () => {
      if (autoSaveTimerRef.current) {
        clearInterval(autoSaveTimerRef.current);
      }
    };
  }, [state.isInitialized, state.sessionData, state.isSaving, salvarProgresso]);

  // ============================================================================
  // PERSISTÊNCIA LOCAL (backup em localStorage)
  // ============================================================================

  useEffect(() => {
    if (state.sessionData && state.mensagens.length > 0) {
      localStorage.setItem('helenaPE_session', JSON.stringify({
        sessionData: state.sessionData,
        mensagens: state.mensagens,
        planejamentoId: state.planejamentoId
      }));
    }
  }, [state.sessionData, state.mensagens, state.planejamentoId]);

  // Recuperar sessão ao montar componente
  useEffect(() => {
    const savedSession = localStorage.getItem('helenaPE_session');
    if (savedSession && !state.isInitialized) {
      try {
        const parsed = JSON.parse(savedSession);
        setState(prev => ({
          ...prev,
          sessionData: parsed.sessionData,
          mensagens: parsed.mensagens.map((m: any) => ({
            ...m,
            timestamp: new Date(m.timestamp)
          })),
          planejamentoId: parsed.planejamentoId,
          isInitialized: true
        }));
      } catch (e) {
        console.error('Erro ao recuperar sessão:', e);
      }
    }
  }, [state.isInitialized]);

  // ============================================================================
  // RETORNO
  // ============================================================================

  return {
    // Estado
    ...state,

    // Ações
    iniciarSessao,
    enviarMensagem,
    selecionarModelo,
    selecionarModoEntrada,
    responderDiagnostico,
    salvarProgresso,
    carregarPlanejamento,
    resetarSessao,
    limparErro
  };
};

export default useHelenaPE;
