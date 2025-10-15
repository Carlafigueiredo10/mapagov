import { useEffect, useRef, useCallback } from 'react';
import { useChatStore } from '../store/chatStore';
import api from '../services/api';

interface AutoSaveOptions {
  interval?: number; // Intervalo em ms (padrão: 30 segundos)
  enabled?: boolean; // Se auto-save está habilitado
}

interface AutoSaveResponse {
  success: boolean;
  pop?: {
    id: number;
    uuid: string;
    autosave_sequence: number;
  };
  snapshot_created?: boolean;
  error?: string;
}

export const useAutoSave = (options: AutoSaveOptions = {}) => {
  const { interval = 30000, enabled = true } = options;

  const { dadosPOP, sessionId } = useChatStore();
  const lastSaveRef = useRef<string>('');
  const saveTimeoutRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const popIdRef = useRef<number | null>(null);
  const popUuidRef = useRef<string | null>(null);

  // Salvar manualmente
  const saveNow = useCallback(async () => {
    if (!enabled) return { success: false, error: 'Auto-save desabilitado' };

    try {
      const dadosSerializados = JSON.stringify(dadosPOP);

      // Verificar se houve mudanças desde último save
      if (dadosSerializados === lastSaveRef.current) {
        console.log('⏭️ Auto-save: Sem mudanças desde último save');
        return { success: true, skipped: true };
      }

      console.log('💾 Auto-save: Salvando dados...', {
        sessionId,
        popId: popIdRef.current,
        dadosSize: Object.keys(dadosPOP).length
      });

      const payload = {
        id: popIdRef.current,
        uuid: popUuidRef.current,
        session_id: sessionId,
        ...dadosPOP,
        raw_payload: dadosSerializados,
      };

      const response = await api.post<AutoSaveResponse>('/pop-autosave/', payload);

      if (response.data.success) {
        // Armazenar referências para próximos saves
        if (response.data.pop) {
          popIdRef.current = response.data.pop.id;
          popUuidRef.current = response.data.pop.uuid;
        }

        lastSaveRef.current = dadosSerializados;

        console.log('✅ Auto-save concluído:', {
          id: popIdRef.current,
          sequence: response.data.pop?.autosave_sequence,
          snapshot: response.data.snapshot_created
        });

        return {
          success: true,
          popId: popIdRef.current,
          snapshot: response.data.snapshot_created
        };
      } else {
        console.error('❌ Auto-save falhou:', response.data.error);
        return { success: false, error: response.data.error };
      }
    } catch (error) {
      console.error('❌ Erro no auto-save:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Erro desconhecido'
      };
    }
  }, [enabled, dadosPOP, sessionId]);

  // Auto-save periódico
  useEffect(() => {
    if (!enabled) return;

    // Limpar timeout anterior
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    // Agendar próximo save
    saveTimeoutRef.current = setTimeout(() => {
      saveNow();
    }, interval);

    // Cleanup
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, [enabled, interval, saveNow]);

  // Salvar ao sair da página
  useEffect(() => {
    if (!enabled) return;

    const handleBeforeUnload = () => {
      // Tentar salvar sincronamente antes de sair
      // Note: nem sempre funciona devido a restrições do navegador
      saveNow();
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [enabled, saveNow]);

  return {
    saveNow,
    popId: popIdRef.current,
    popUuid: popUuidRef.current,
  };
};
