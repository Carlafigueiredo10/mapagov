import { useState, useCallback } from 'react';
import { useChatStore } from '../store/chatStore';
import { chatHelena, chatAjuda, gerarPDF, type ChatRequest, type ChatResponse } from '../services/helenaApi';

// ✅ FIX: Ref global para "last write wins" - evita race condition
let lastRequestId: string | null = null;

// Frases humanizadas de carregamento (randomizadas)
const frasesCarregamento = [
  'Pensando...',
  'Analisando...',
  'Deixa eu ver...',
  'Hmmm...',
  'Processando sua resposta...',
  'Avaliando...',
  'Entendendo...',
  'Verificando...'
];

const obterFraseAleatoria = () => {
  const indice = Math.floor(Math.random() * frasesCarregamento.length);
  return frasesCarregamento[indice];
};

export const useChat = (onAutoSave?: () => Promise<void>) => {
  const {
    messages,
    isProcessing,
    sessionId,
    progresso,
    dadosPOP,
    viewMode,
    setProcessing,
    updateProgresso,
    updateDadosPOP,
    setViewMode,
    adicionarMensagemRapida,
  } = useChatStore();

  const [error, setError] = useState<string | null>(null);

  const enviarMensagem = useCallback(async (
    texto: string,
    contexto: 'gerador_pop' | 'ajuda_mapeamento' = 'gerador_pop',
    mostrarMensagemUsuario: boolean = true
  ) => {
    // ✅ FIX: Guard - só bloqueia clique humano, permite auto_continue
    const state = useChatStore.getState();
    if (!texto.trim()) return;
    if (mostrarMensagemUsuario && state.isProcessing) return;

    setError(null);
    setProcessing(true);

    // ✅ FIX: Gerar request_id único para detectar race conditions
    const requestId = crypto.randomUUID();
    lastRequestId = requestId;
    const reqType = mostrarMensagemUsuario ? 'USER' : 'AUTO';
    console.log(`🆔 [REQ][${reqType}] ${requestId} | msg: "${texto.substring(0, 30)}..."`);

    // ✅ Flag para auto_continue - evita finally liberar cedo
    let holdProcessing = false;

    try {
      // Adicionar mensagem do usuário (apenas se mostrarMensagemUsuario = true)
      if (mostrarMensagemUsuario) {
        adicionarMensagemRapida('usuario', texto);
      }

      // Adicionar loading - verificar se deve mostrar quadro roxo animado
      let loadingId: string;

      // ✅ Verificar se backend sinalizou que está aguardando descrição inicial
      const aguardandoDescricao = sessionStorage.getItem(`aguardando_descricao_${sessionId}`) === 'true';

      // ✅ FALLBACK: Detectar descrição inicial pela mensagem anterior (Helena perguntando sobre atividade)
      const mensagensAtual = useChatStore.getState().messages;
      const ultimaMensagemHelena = [...mensagensAtual].reverse().find(m => m.tipo === 'helena');

      // Frases que indicam que Helena está pedindo descrição de atividade
      const frasesDescricaoAtividade = [
        'me conta o que você faz',
        'me conte',
        'qual sua atividade',
        'descreva sua atividade',
        'descreva aqui o que você faz',
        'estou te ouvindo',
        'o que você faz na sua rotina',
        'o que você entrega ao finalizar'
      ];

      const helenaEstaPedindoDescricao = ultimaMensagemHelena?.mensagem &&
        frasesDescricaoAtividade.some(frase =>
          ultimaMensagemHelena.mensagem.toLowerCase().includes(frase.toLowerCase())
        );

      // ✅ Detectar se texto é puro (não-JSON) OU se é JSON mas contém descrição de atividade
      const isTextoJSON = texto.trim().startsWith('{') || texto.trim().startsWith('[');
      let isDescricaoTextoLivre = false;

      if (isTextoJSON) {
        // Se é JSON, verificar se é ação de enviar descrição (interface RAG)
        try {
          const parsed = JSON.parse(texto);
          // Interface RAG envia: {"acao":"enviar_descricao","descricao":"..."}
          isDescricaoTextoLivre = parsed.acao === 'enviar_descricao' &&
                                   parsed.descricao &&
                                   parsed.descricao.length > 20;
        } catch {
          isDescricaoTextoLivre = false;
        }
      } else {
        // Texto puro (não-JSON) — mínimo alinhado com backend (10 chars)
        isDescricaoTextoLivre = texto.trim().length >= 10;
      }

      console.log('🔍 [FALLBACK DEBUG] Detecção de descrição inicial:', {
        aguardandoDescricao,
        helenaEstaPedindoDescricao,
        ultimaMensagemHelena: ultimaMensagemHelena?.mensagem?.substring(0, 100),
        textoUsuario: texto.substring(0, 50),
        textoLength: texto.trim().length,
        startsWithJSON: texto.trim().startsWith('{') || texto.trim().startsWith('['),
        isTextoJSON,
        isDescricaoTextoLivre
      });

      // ✅ Quadro roxo APENAS se:
      // 1. Backend sinalizou que está aguardando descrição (flag salva anteriormente) OU
      // 2. Helena acabou de pedir descrição (fallback por contexto) E
      // 3. É texto livre de descrição (puro OU JSON de interface RAG) E
      // 4. É contexto gerador_pop E
      // 5. Deve mostrar mensagem do usuário (não é auto-continue)
      const isDescricaoInicial = (aguardandoDescricao || helenaEstaPedindoDescricao) &&
                                  isDescricaoTextoLivre &&
                                  contexto === 'gerador_pop' &&
                                  mostrarMensagemUsuario;

      if (isDescricaoInicial) {
        // Mostrar card educativo "Entenda como sua atividade é classificada"
        console.log('📘 Mostrando card educativo para descrição inicial:', texto.substring(0, 50));

        // Limpar flag (descrição foi enviada)
        sessionStorage.removeItem(`aguardando_descricao_${sessionId}`);

        // Reset da flag antes de mostrar card
        useChatStore.getState().resetEntendeuClassificacao();

        loadingId = adicionarMensagemRapida('helena', '', {
          loading: true,
          interface: {
            tipo: 'explicacao_classificacao',
            dados: {}
          }
        });

        // Fazer request ao backend em paralelo
        const request: ChatRequest = {
          message: texto,
          contexto,
          session_id: sessionId,
          nome_usuario: useChatStore.getState().dadosPOP.nome_usuario,
        };

        let respostaBackend: ChatResponse | null = null;
        let backendErro: unknown = null;

        // Promise do backend
        const backendDone = (contexto === 'gerador_pop'
          ? chatHelena(request)
          : chatAjuda(request)
        ).then((res) => {
          respostaBackend = res;
        }).catch((err) => {
          backendErro = err;
        });

        // Promise do "Entendi" — subscribe no store
        const userEntendeu = new Promise<void>((resolve) => {
          // Se já clicou (improvável mas seguro)
          if (useChatStore.getState().entendeuClassificacao) {
            resolve();
            return;
          }
          const unsub = useChatStore.subscribe((state) => {
            if (state.entendeuClassificacao) {
              unsub();
              resolve();
            }
          });
        });

        // Se o usuário clicar "Entendi" antes do backend, trocar para loading simples
        userEntendeu.then(() => {
          if (!respostaBackend && !backendErro) {
            const store = useChatStore.getState();
            store.removeMessage(loadingId);
            loadingId = adicionarMensagemRapida('helena', 'Quase lá...', { loading: true });
          }
        });

        // Aguardar AMBOS
        await Promise.all([backendDone, userEntendeu]);

        // Re-throw se backend deu erro
        if (backendErro) {
          const store = useChatStore.getState();
          store.removeMessage(loadingId);
          throw backendErro;
        }

        // "Last write wins"
        const store = useChatStore.getState();
        if (requestId !== lastRequestId) {
          store.removeMessage(loadingId);
          console.warn(`⚠️ [RACE] Ignorando resposta antiga: ${requestId} (atual: ${lastRequestId})`);
          return;
        }

        // Remover card educativo/loading e usar resposta guardada
        store.removeMessage(loadingId);
        // Continua com snap = respostaBackend abaixo
        var snap = respostaBackend!;

      } else {
        // Loading simples com frase humanizada para todos os outros casos
        // (sistemas, áreas, dropdowns, confirmações, etc.)
        loadingId = adicionarMensagemRapida('helena', obterFraseAleatoria(), { loading: true });

        // Fazer request
        const request: ChatRequest = {
          message: texto,
          contexto,
          session_id: sessionId,
          nome_usuario: useChatStore.getState().dadosPOP.nome_usuario,
        };

        const response: ChatResponse = contexto === 'gerador_pop'
          ? await chatHelena(request)
          : await chatAjuda(request);

        var snap = response;

        // "Last write wins" — ignora respostas antigas (race condition)
        const store = useChatStore.getState();
        if (requestId !== lastRequestId) {
          store.removeMessage(loadingId);
          console.warn(`⚠️ [RACE] Ignorando resposta antiga: ${requestId} (atual: ${lastRequestId})`);
          return;
        }

        // Remover loading
        store.removeMessage(loadingId);
      }

      const iface = (snap as any).interface as { tipo: string; dados: Record<string, unknown> } | null;
      const temInterface = !!iface?.tipo;
      const temTexto = typeof snap.resposta === 'string' && snap.resposta.trim() !== '';

      // Verificar se backend sinalizou que está aguardando descrição inicial
      if (snap.metadados?.aguardando_descricao_inicial) {
        sessionStorage.setItem(`aguardando_descricao_${sessionId}`, 'true');
      }

      // Adicionar mensagem/interface — interface já vem montada do helenaApi
      if (temInterface) {
        adicionarMensagemRapida('helena', snap.resposta || '', {
          interface: iface,
        });
      } else if (temTexto) {
        adicionarMensagemRapida('helena', snap.resposta);
      } else {
        console.warn('⚠️ Ignorando resposta vazia ou sem interface:', snap);
        return;
      }

      // ✅ FIX: holdProcessing para auto_continue (setProcessing só no finally)
      holdProcessing = !!snap.metadados?.auto_continue;

      // ✅ Processar dados extraídos (adapter já normaliza formulario_pop -> dados_extraidos)
      if (snap.dados_extraidos) {
        console.log('🔵 [useChat] dados_extraidos:', Object.keys(snap.dados_extraidos));
        updateDadosPOP(snap.dados_extraidos);
      }

      // ✅ Atualizar estado atual da máquina de estados (stepper)
      const progressoDetalhado = snap.metadados?.progresso_detalhado as { estado_atual?: string } | undefined;
      if (progressoDetalhado?.estado_atual) {
        useChatStore.getState().setEstadoAtual(progressoDetalhado.estado_atual);
      }

      // ✅ Espelhar modo ajuda do backend
      useChatStore.getState().setModoAjudaAtivo(Boolean(snap.metadados?.em_modo_duvidas));

      // Atualizar progresso
      if (snap.progresso) {
        const [atual, total] = snap.progresso.split('/').map(Number);
        const porcentagem = (atual / total) * 100;
        const textoProgresso = `Etapa ${atual} de ${total}`;
        updateProgresso(porcentagem, textoProgresso);
      }

      // 💾 Auto-save após processar resposta
      if (snap.dados_extraidos && onAutoSave) {
        try {
          await onAutoSave();
        } catch (saveError) {
          console.error('⚠️ Erro no auto-save:', saveError);
        }
      }

      // Verificar se conversa está completa
      if (snap.conversa_completa) {
        setViewMode('final_review');

        // Se é a interface final, disparar geração de PDF automaticamente
        if (iface?.tipo === 'final') {
          try {
            console.log('🎯 Conversa completa! Gerando PDF...');
            const dadosCompletos = snap.dados_extraidos || dadosPOP;

            const pdfResponse = await gerarPDF({
              dados_pop: dadosCompletos as Record<string, unknown>,
              session_id: sessionId
            });

            if (pdfResponse.success && pdfResponse.pdf_url) {
              console.log('✅ PDF gerado:', pdfResponse.pdf_url);
              const storeAtual = useChatStore.getState();
              const mensagens = storeAtual.messages;
              const ultimaMensagem = mensagens[mensagens.length - 1];

              const iface = ultimaMensagem?.interface as { tipo: string; dados: Record<string, unknown> } | undefined;
              if (iface?.tipo === 'final') {
                storeAtual.removeMessage(ultimaMensagem.id);
                adicionarMensagemRapida('helena', ultimaMensagem.mensagem, {
                  interface: {
                    tipo: 'final',
                    dados: {
                      ...iface.dados,
                      pdfUrl: pdfResponse.pdf_url,
                      arquivo: pdfResponse.arquivo
                    }
                  }
                });
              }
            }
          } catch (pdfError) {
            console.error('❌ Erro ao gerar PDF:', pdfError);
          }
        }
      }

      // 🚗 AUTO-CONTINUE: Se backend pedir para enviar mensagem automática
      if (snap.metadados?.auto_continue) {
        const delay = snap.metadados.auto_continue_delay || 1500;
        const message = snap.metadados.auto_continue_message || '__continue__';

        console.log(`🚗 [AUTO-CONTINUE] Agendando envio automático de "${message}" em ${delay}ms`);

        setTimeout(() => {
          console.log(`🚗 [AUTO-CONTINUE] Enviando mensagem automática: "${message}"`);
          // Enviar mensagem sem mostrar no chat do usuário (mostrarMensagemUsuario: false)
          enviarMensagem(message, 'gerador_pop', false);
        }, delay);
      }

      return snap;

    } catch (err: unknown) {
      // --- Diagnóstico: logar detalhes reais do erro ---
      const axiosErr = err as { response?: { status?: number; data?: Record<string, unknown> }; message?: string };
      const status = axiosErr?.response?.status;
      const data = axiosErr?.response?.data;
      const msg = axiosErr?.message || (err instanceof Error ? err.message : 'Erro desconhecido');

      console.error('🔴 [useChat] Erro na request:', { status, data, msg, err });

      setError(msg);

      // ✅ Remover loading em caso de erro
      const store = useChatStore.getState();
      const loadingMsg = store.messages.find(m => m.loading);
      if (loadingMsg) {
        store.removeMessage(loadingMsg.id);
      }

      // Mostrar mensagem real se backend retornou detalhes (_diag em DEBUG)
      const diag = data?._diag as { req_id?: string; elapsed_s?: number; exception?: string } | undefined;
      const backendErro = data?.erro || data?.error;
      let userMsg = 'Erro de conexão. Tente novamente.';
      if (diag) {
        userMsg = `Erro técnico (req=${diag.req_id}, ${diag.elapsed_s}s): ${diag.exception || backendErro || msg}`;
      } else if (backendErro) {
        userMsg = `Erro: ${backendErro}`;
      } else if (status) {
        userMsg = `Erro ${status}: ${msg}`;
      }

      adicionarMensagemRapida('helena', `❌ ${userMsg}`);
      throw err;
    } finally {
      // ✅ FIX: Respeitar holdProcessing - só libera se não for auto_continue
      if (!holdProcessing) {
        setProcessing(false);
      }
    }
  }, [sessionId, isProcessing, dadosPOP, adicionarMensagemRapida, updateDadosPOP, updateProgresso, setViewMode, setProcessing]);

  const responderInterface = useCallback(async (resposta: string) => {
    // ✅ Não mostrar mensagem do usuário para respostas de interface (botões, dropdowns, etc)
    return enviarMensagem(resposta, 'gerador_pop', false);
  }, [enviarMensagem]);

  return {
    // Estado
    messages,
    isProcessing,
    error,
    progresso,
    dadosPOP,
    viewMode,
    sessionId,
    
    // Actions
    enviarMensagem,
    responderInterface,
    clearError: () => setError(null),
  };
};