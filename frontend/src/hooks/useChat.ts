import { useState, useCallback } from 'react';
import { useChatStore } from '../store/chatStore';
import { chatHelena, chatAjuda, gerarPDF, type ChatRequest, type ChatResponse } from '../services/helenaApi';

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

      // Adicionar loading
      const loadingId = adicionarMensagemRapida('helena', 'Processando...', { loading: true });

      // Fazer request
      const request: ChatRequest = {
        message: texto,
        contexto,
        session_id: sessionId,
      };

      const response: ChatResponse = contexto === 'gerador_pop' 
        ? await chatHelena(request)
        : await chatAjuda(request);

      // Remover loading
      const store = useChatStore.getState();
      store.removeMessage(loadingId);

      // ✅ VALIDAÇÃO: Só adicionar resposta se não estiver vazia
      if (response.resposta && response.resposta.trim() !== '') {
        adicionarMensagemRapida('helena', response.resposta, {
          interface: response.tipo_interface ? {
            tipo: response.tipo_interface,
            dados: response.dados_interface
          } : undefined
        });
      } else {
        // ⚠️ LOG: Resposta vazia detectada
        console.error('❌ Resposta vazia do backend:', response);
        
        // Adicionar mensagem de fallback
        adicionarMensagemRapida('helena', 'Desculpe, não consegui processar sua mensagem. Pode repetir?');
      }

      // Processar dados extraídos
      if (response.dados_extraidos) {
        updateDadosPOP(response.dados_extraidos);
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