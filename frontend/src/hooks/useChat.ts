import { useState, useCallback } from 'react';
import { useChatStore } from '../store/chatStore';
import { chatHelena, chatAjuda, gerarPDF, type ChatRequest, type ChatResponse } from '../services/helenaApi';

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
    modoRevisao,
    setProcessing,
    updateProgresso,
    updateDadosPOP,
    setModoRevisao,
    adicionarMensagemRapida,
  } = useChatStore();

  const [error, setError] = useState<string | null>(null);

  const enviarMensagem = useCallback(async (
    texto: string,
    contexto: 'gerador_pop' | 'ajuda_mapeamento' = 'gerador_pop',
    mostrarMensagemUsuario: boolean = true
  ) => {
    if (!texto.trim() || isProcessing) return;

    setError(null);
    setProcessing(true);

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
        // Texto puro (não-JSON) e longo
        isDescricaoTextoLivre = texto.trim().length > 20;
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
        // Mostrar quadro roxo animado com descrição
        console.log('🎨 Mostrando LoadingAnaliseAtividade para descrição inicial:', texto.substring(0, 50));

        // Limpar flag (descrição foi enviada)
        sessionStorage.removeItem(`aguardando_descricao_${sessionId}`);

        loadingId = adicionarMensagemRapida('helena', '', {
          loading: true,
          interface: {
            tipo: 'loading_analise_atividade',
            dados: { descricao: texto.trim() }
          }
        });
      } else {
        // Loading simples com frase humanizada para todos os outros casos
        // (sistemas, áreas, dropdowns, confirmações, etc.)
        loadingId = adicionarMensagemRapida('helena', obterFraseAleatoria(), { loading: true });
      }

      // Fazer request
      const request: ChatRequest = {
        message: texto,
        contexto,
        session_id: sessionId,
      };

      const response: ChatResponse = contexto === 'gerador_pop'
        ? await chatHelena(request)
        : await chatAjuda(request);

      // 🔍 DEBUG ULTRA CRÍTICO: Log da response HTTP COMPLETA recebida do backend
      console.log('[useChat] 🔴🔴🔴 RESPONSE HTTP RECEBIDA DO BACKEND 🔴🔴🔴');
      console.log('[useChat] 🔴 tipo_interface =', response.tipo_interface);
      console.log('[useChat] 🔴 RESPONSE COMPLETA =', response);
      console.log('[useChat] 🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴');

      // Remover loading
      const store = useChatStore.getState();
      store.removeMessage(loadingId);

      // ✅ VALIDAÇÃO: Só adicionar resposta se texto OU interface presente
      // Modo interface: resposta pode ser null se interface substitui texto (pureza arquitetural)
      console.log('[useChat] 📥 Resposta do backend:', {
        resposta_raw: response.resposta,
        resposta_type: typeof response.resposta,
        tem_resposta: !!response.resposta,
        tem_interface: !!response.tipo_interface,
        tipo_interface: response.tipo_interface,
        dados_interface_keys: response.dados_interface ? Object.keys(response.dados_interface) : null,
        RESPONSE_COMPLETO: response  // ← 🔥 LOG COMPLETO para debug
      });

      // 🎯 FAILSAFE COM TRY-CATCH: Nunca deixar quebrar a aplicação
      try {
        const temInterface = !!response.tipo_interface;
        const temTexto = response.resposta && typeof response.resposta === 'string' && response.resposta.trim() !== '';

        console.log('[useChat] 🔍 Validação FAILSAFE:', {
          temInterface,
          temTexto,
          tipo_interface: response.tipo_interface,
          resposta_raw: response.resposta,
          resposta_type: typeof response.resposta
        });

        // ✅ Verificar se backend sinalizou que está aguardando descrição inicial
        if ((response as any).metadados?.aguardando_descricao_inicial) {
          console.log('🔔 Backend sinalizou: aguardando descrição inicial! Salvando flag...');
          sessionStorage.setItem(`aguardando_descricao_${sessionId}`, 'true');
        }

        // 🚨 FAILSAFE: Prioridade ABSOLUTA para interface
        if (temInterface) {
          console.log('[useChat] ✅ FAILSAFE: Tem interface, adicionando SEMPRE:', response.tipo_interface);
          adicionarMensagemRapida('helena', response.resposta || '', {
            interface: {
              tipo: response.tipo_interface,
              dados: response.dados_interface || {}
            }
          });
        } else if (temTexto) {
          console.log('[useChat] ✅ Tem texto, adicionando mensagem normal');
          adicionarMensagemRapida('helena', response.resposta);
        } else {
          // ⚠️ PATCH 1: Ignorar resposta vazia completamente (sem adicionar mensagem)
          console.warn('⚠️ Ignorando resposta vazia ou sem interface:', response);
          return; // impede renderização de mensagens vazias
        }
      } catch (validationError) {
        console.error('❌ ERRO CRÍTICO na validação de resposta:', validationError);
        console.error('❌ Response que causou erro:', response);

        // Fallback absoluto: tentar adicionar mensagem de qualquer jeito
        try {
          if (response.tipo_interface) {
            adicionarMensagemRapida('helena', '', {
              interface: { tipo: response.tipo_interface, dados: response.dados_interface || {} }
            });
          } else if (response.resposta) {
            adicionarMensagemRapida('helena', String(response.resposta));
          } else {
            adicionarMensagemRapida('helena', 'Erro ao processar resposta. Por favor, recarregue a página.');
          }
        } catch (fallbackError) {
          console.error('❌ ERRO FATAL no fallback:', fallbackError);
        }
      }

      // ✅ Processar dados extraídos OU formulário POP (suporte a ambos formatos)
      if (response.dados_extraidos) {
        console.log('🔵 [useChat] dados_extraidos RECEBIDO:', response.dados_extraidos);
        console.log('🔵 [useChat] Campos:', Object.keys(response.dados_extraidos));
        console.log('🔵 [useChat] CHAMANDO updateDadosPOP...');
        updateDadosPOP(response.dados_extraidos);
        console.log('🔵 [useChat] updateDadosPOP EXECUTADO');
      } else {
        console.log('⚠️ [useChat] dados_extraidos NÃO RECEBIDO');
      }

      // ✅ FASE 2: Suporte para formulario_pop (preenchimento em tempo real)
      if ((response as any).formulario_pop) {
        console.log('🟢 [useChat] formulario_pop RECEBIDO:', (response as any).formulario_pop);
        console.log('🟢 [useChat] Campos:', Object.keys((response as any).formulario_pop));
        console.log('🟢 [useChat] CHAMANDO updateDadosPOP...');
        updateDadosPOP((response as any).formulario_pop);
        console.log('🟢 [useChat] updateDadosPOP EXECUTADO');
      } else {
        console.log('⚠️ [useChat] formulario_pop NÃO RECEBIDO');
      }

      // Atualizar progresso
      if (response.progresso) {
        const [atual, total] = response.progresso.split('/').map(Number);
        const porcentagem = (atual / total) * 100;
        updateProgresso(porcentagem, response.progresso);
      }

      // 💾 Auto-save após processar resposta (se houver dados extraídos)
      if (response.dados_extraidos && onAutoSave) {
        try {
          console.log('💾 Disparando auto-save após resposta...');
          await onAutoSave();
        } catch (saveError) {
          console.error('⚠️ Erro no auto-save (não bloqueia fluxo):', saveError);
          // Não bloquear o fluxo se auto-save falhar
        }
      }

      // Verificar se conversa está completa
      if (response.conversa_completa) {
        setModoRevisao(true);

        // Se é a interface final, disparar geração de PDF automaticamente
        if (response.tipo_interface === 'final') {
          try {
            console.log('🎯 Conversa completa! Gerando PDF automaticamente...');

            const dadosCompletos = response.dados_extraidos || dadosPOP;

            const pdfResponse = await gerarPDF({
              dados_pop: dadosCompletos as Record<string, unknown>,
              session_id: sessionId
            });

            if (pdfResponse.success && pdfResponse.pdf_url) {
              console.log('✅ PDF gerado com sucesso:', pdfResponse.pdf_url);

              // Atualizar última mensagem com URL do PDF
              const store = useChatStore.getState();
              const mensagens = store.messages;
              const ultimaMensagem = mensagens[mensagens.length - 1];

              if (ultimaMensagem && ultimaMensagem.interface?.tipo === 'final') {
                // Criar nova mensagem com PDF
                store.removeMessage(ultimaMensagem.id);
                adicionarMensagemRapida('helena', ultimaMensagem.mensagem, {
                  interface: {
                    tipo: 'final',
                    dados: {
                      ...ultimaMensagem.interface.dados,
                      pdfUrl: pdfResponse.pdf_url,
                      arquivo: pdfResponse.arquivo
                    }
                  }
                });
              }
            } else {
              console.error('❌ Erro ao gerar PDF:', pdfResponse.error);
            }
          } catch (pdfError) {
            console.error('❌ Erro ao gerar PDF automaticamente:', pdfError);
            // Não bloquear o fluxo, apenas logar o erro
          }
        }
      }

      // 🚗 AUTO-CONTINUE: Se backend pedir para enviar mensagem automática
      if (response.metadados?.auto_continue) {
        const delay = response.metadados.auto_continue_delay || 1500;
        const message = response.metadados.auto_continue_message || '__continue__';

        console.log(`🚗 [AUTO-CONTINUE] Agendando envio automático de "${message}" em ${delay}ms`);

        setTimeout(() => {
          console.log(`🚗 [AUTO-CONTINUE] Enviando mensagem automática: "${message}"`);
          // Enviar mensagem sem mostrar no chat do usuário (mostrarMensagemUsuario: false)
          enviarMensagem(message, 'gerador_pop', false);
        }, delay);
      }

      return response;

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
      
      // ✅ Remover loading em caso de erro
      const store = useChatStore.getState();
      const loadingMsg = store.messages.find(m => m.loading);
      if (loadingMsg) {
        store.removeMessage(loadingMsg.id);
      }
      
      adicionarMensagemRapida('helena', '❌ Erro de conexão. Tente novamente.');
      throw err;
    } finally {
      setProcessing(false);
    }
  }, [sessionId, isProcessing, dadosPOP, adicionarMensagemRapida, updateDadosPOP, updateProgresso, setModoRevisao, setProcessing]);

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
    modoRevisao,
    sessionId,
    
    // Actions
    enviarMensagem,
    responderInterface,
    clearError: () => setError(null),
  };
};