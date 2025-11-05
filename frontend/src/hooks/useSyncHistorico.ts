import { useEffect, useRef } from 'react';
import { useChatStore } from '../store/chatStore';
import { buscarMensagensV2 } from '../services/helenaApi';

// Mensagem de boas-vindas hardcoded (mesmo tom da Helena)
const MENSAGEM_BOAS_VINDAS = `👋 Oi!

Se é a sua primeira vez por aqui, sinta-se em casa 🏠
Eu sou a Helena, sua parceira de jornada no MapaGov uma plataforma da DECIPEX criada pra transformar o que você faz no dia a dia em processos claros, seguros e vivos.

E se você já me conhece... que bom te ver de novo! 💛
Hoje, vamos começar uma das partes mais legais: mapear a sua atividade.

Mas antes de tudo, quero te conhecer melhor
**como posso te chamar por aqui?**
(só o primeiro nome já tá ótimo 😉)`;

/**
 * Hook para sincronizar histórico de mensagens com backend
 *
 * Comportamento:
 * 1. Na primeira montagem do componente, busca histórico do backend
 * 2. Se não houver histórico (sessão nova), adiciona mensagem de boas-vindas
 * 3. Se houver histórico, carrega as mensagens e adiciona boas-vindas no início
 *
 * SIMPLIFICADO: Apenas useRef para evitar re-execução (padrão React)
 */
export const useSyncHistorico = () => {
  const { sessionId, messages, carregarHistorico, adicionarMensagemRapida } = useChatStore();
  const syncedRef = useRef(false);

  useEffect(() => {
    // Executa apenas uma vez por lifecycle do componente
    if (syncedRef.current) return;
    syncedRef.current = true;

    const loadHistory = async () => {
      try {
        console.log('[useSyncHistorico] Iniciando sincronização:', sessionId);

        const response = await buscarMensagensV2(sessionId);

        if (response.session_exists && response.mensagens.length > 0) {
          console.log('[useSyncHistorico] Histórico encontrado:', response.mensagens.length, 'mensagens');

          // Carregar histórico do backend
          carregarHistorico(response.mensagens);

          // Adicionar boas-vindas no início se ainda não tiver
          const jaTemBoasVindas = messages.some(
            m => m.tipo === 'helena' && m.mensagem.includes('Eu sou a Helena, sua parceira de jornada')
          );

          if (!jaTemBoasVindas) {
            console.log('[useSyncHistorico] Adicionando boas-vindas no início do histórico');
            adicionarMensagemRapida('helena', MENSAGEM_BOAS_VINDAS);
          }
        } else {
          // Nova sessão - adicionar boas-vindas
          console.log('[useSyncHistorico] Nova sessão - adicionando boas-vindas');
          adicionarMensagemRapida('helena', MENSAGEM_BOAS_VINDAS);
        }
      } catch (error: any) {
        console.error('[useSyncHistorico] Erro ao carregar histórico:', error);

        // Se der erro (ex: 404), adicionar boas-vindas mesmo assim
        if (messages.length === 0) {
          console.log('[useSyncHistorico] Adicionando boas-vindas após erro');
          adicionarMensagemRapida('helena', MENSAGEM_BOAS_VINDAS);
        }
      }
    };

    loadHistory();
  }, [sessionId]); // Depende apenas de sessionId
};
