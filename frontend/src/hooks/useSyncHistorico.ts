import { useEffect, useRef } from 'react';
import { useChatStore } from '../store/chatStore';
import { buscarMensagensV2 } from '../services/helenaApi';

// Mensagem de boas-vindas hardcoded (mesmo tom da Helena)
const MENSAGEM_BOAS_VINDAS = `👋 Olá! Sou a Helena, assistente de IA da DECIPEX especializada em mapeamento de processos.

Vou te ajudar a documentar seu procedimento de forma clara e estruturada, pergunta por pergunta.

Para começarmos, qual seu nome?`;

// ✅ Lock global para impedir execuções concorrentes (StrictMode React 18+)
let globalSyncLock = false;

/**
 * Hook para sincronizar histórico de mensagens com backend
 *
 * ✅ FIX DUPLICAÇÃO: Sistema de defesa em profundidade com 4 camadas:
 * 1. Lock global: Impede execuções concorrentes (React StrictMode)
 * 2. useRef: Impede re-execução no mesmo ciclo de vida do componente
 * 3. sessionStorage: Impede re-injeção por sessão (sobrevive remount/hot-reload)
 * 4. Verificação no histórico: Impede duplicar se outra fonte já injetou
 *
 * Carrega mensagens do backend quando:
 * 1. Componente monta pela primeira vez
 * 2. sessionId existe no localStorage
 * 3. Ainda não há mensagens no store
 *
 * Para sessões novas do POP, adiciona mensagem de boas-vindas hardcoded (UMA VEZ)
 */
export const useSyncHistorico = () => {
  const { sessionId, messages, carregarHistorico, adicionarMensagemRapida } = useChatStore();
  const syncedRef = useRef(false);  // ✅ Camada 2: Guard por render

  useEffect(() => {
    // ✅ Camada 1: Lock global (impede double render do StrictMode)
    if (globalSyncLock) {
      console.log('[useSyncHistorico] 🔒 Lock global ativo - bloqueando execução concorrente');
      return;
    }

    // ✅ Camada 2: Só sincroniza uma vez por lifecycle do componente
    if (syncedRef.current) return;

    // ✅ Camada 2: Guard por sessão (sessionStorage)
    // Sobrevive a hot-reloads, remounts, e múltiplos pontos de injeção
    const storageKey = `helena:welcome:${sessionId}`;
    const welcomeAlreadyInjected = sessionStorage.getItem(storageKey);

    // ✅ Camada 3: Verificar se mensagem já existe no histórico atual
    // (proteção contra múltiplas fontes no frontend)
    const jaTemWelcome = messages.some(
      m =>
        m.tipo === 'helena' &&
        typeof m.mensagem === 'string' &&
        m.mensagem.includes('Olá! Sou a Helena') &&
        m.mensagem.includes('Para começarmos, qual seu nome?')
    );

    // Se já tem mensagem (por qualquer via), não adicionar novamente
    if (messages.length > 0 && jaTemWelcome) {
      console.log('[useSyncHistorico] ✅ Boas-vindas já existem no histórico (skip)');
      syncedRef.current = true;
      return;
    }

    // Tentar carregar histórico do backend
    const loadHistory = async () => {
      // ✅ Ativar lock global
      globalSyncLock = true;

      try {
        console.log('[useSyncHistorico] 🔓 Lock ativado - iniciando sincronização:', sessionId);

        const response = await buscarMensagensV2(sessionId);

        if (response.session_exists && response.mensagens.length > 0) {
          console.log('[useSyncHistorico] Histórico encontrado:', response.mensagens.length, 'mensagens');

          // ✅ Filtro de defesa: Remover boas-vindas duplicadas do backend
          const mensagensFiltradas = response.mensagens.filter(msg => {
            const isBoasVindas = msg.role === 'assistant' &&
                                 typeof msg.content === 'string' &&
                                 msg.content.includes('Olá! Sou a Helena') &&
                                 msg.content.includes('Para começarmos, qual seu nome?');
            return !isBoasVindas;  // ← Descarta boas-vindas do backend
          });

          // Carregar histórico filtrado
          if (mensagensFiltradas.length > 0) {
            carregarHistorico(mensagensFiltradas);
          }

          // ✅ Injetar boas-vindas hardcoded SOMENTE se:
          // 1. Não foi injetada anteriormente (sessionStorage)
          // 2. Não existe no histórico atual
          if (!welcomeAlreadyInjected && !jaTemWelcome) {
            console.log('[useSyncHistorico] ✅ Adicionando boas-vindas hardcoded (histórico restaurado)');
            adicionarMensagemRapida('helena', MENSAGEM_BOAS_VINDAS);
            sessionStorage.setItem(storageKey, '1');  // ← Marca como injetada
          }
        } else {
          // ✅ Nova sessão - adicionar boas-vindas SOMENTE se não foi injetada antes
          if (!welcomeAlreadyInjected && !jaTemWelcome) {
            console.log('[useSyncHistorico] ✅ Nova sessão - adicionando boas-vindas hardcoded');
            adicionarMensagemRapida('helena', MENSAGEM_BOAS_VINDAS);
            sessionStorage.setItem(storageKey, '1');  // ← Marca como injetada
          } else {
            console.log('[useSyncHistorico] ⚠️ Boas-vindas já foram injetadas nesta sessão (skip)');
          }
        }

        syncedRef.current = true;
      } catch (error: any) {
        console.log('[useSyncHistorico] Erro ao carregar histórico:', error.message);

        // ✅ Se sessão não existe (404) E não foi injetada antes
        if (error.response?.status === 404 && !welcomeAlreadyInjected && !jaTemWelcome) {
          console.log('[useSyncHistorico] ✅ Sessão 404 - adicionando boas-vindas hardcoded');
          adicionarMensagemRapida('helena', MENSAGEM_BOAS_VINDAS);
          sessionStorage.setItem(storageKey, '1');  // ← Marca como injetada
        }

        syncedRef.current = true;
      } finally {
        // ✅ SEMPRE liberar lock no final
        console.log('[useSyncHistorico] 🔓 Lock liberado');
        // Pequeno delay para garantir que segunda execução veja o lock
        setTimeout(() => {
          globalSyncLock = false;
        }, 100);
      }
    };

    loadHistory();
  }, [sessionId, messages.length, carregarHistorico, adicionarMensagemRapida, messages]);
};
