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
  integrity_hash?: string;
  snapshot_created?: boolean;
  error?: string;
}

export const useAutoSave = (options: AutoSaveOptions = {}) => {
  const { interval = 30000, enabled = true } = options;

  const { dadosPOP, sessionId, popId, popUuid, integrityHash, setPopIdentifiers } = useChatStore();
  const lastSaveRef = useRef<string>('');
  const saveTimeoutRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  // Salvar manualmente
  const saveNow = useCallback(async () => {
    if (!enabled) return { success: false, error: 'Auto-save desabilitado' };

    try {
      const dadosSerializados = JSON.stringify(dadosPOP);

      // Verificar se houve mudanças desde último save
      if (dadosSerializados === lastSaveRef.current) {
        return { success: true, skipped: true };
      }

      const payload = {
        id: popId,
        uuid: popUuid,
        session_id: sessionId,
        integrity_hash: integrityHash,
        ...dadosPOP,
        raw_payload: dadosSerializados,
      };

      const response = await api.post<AutoSaveResponse>('/pop-autosave/', payload);

      if (response.data.success) {
        if (response.data.pop && response.data.integrity_hash) {
          setPopIdentifiers(
            response.data.pop.id,
            response.data.pop.uuid,
            response.data.integrity_hash,
          );
        }

        lastSaveRef.current = dadosSerializados;

        return {
          success: true,
          popId: response.data.pop?.id,
          snapshot: response.data.snapshot_created,
        };
      } else {
        console.error('[Auto-save] Falhou:', response.data.error);
        return { success: false, error: response.data.error };
      }
    } catch (error: unknown) {
      // Detectar conflito 409 (outra aba modificou o POP)
      const axiosErr = error as { response?: { status?: number; data?: { conflict?: Record<string, unknown> } } };
      if (axiosErr?.response?.status === 409) {
        console.warn('[Auto-save] Conflito detectado (409)');
        return {
          success: false,
          conflict: true,
          serverData: axiosErr.response.data?.conflict,
        };
      }

      console.error('[Auto-save] Erro:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Erro desconhecido',
      };
    }
  }, [enabled, dadosPOP, sessionId, popId, popUuid, integrityHash, setPopIdentifiers]);

  // Auto-save periódico
  useEffect(() => {
    if (!enabled) return;

    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    saveTimeoutRef.current = setTimeout(() => {
      saveNow();
    }, interval);

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
      saveNow();
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [enabled, saveNow]);

  return {
    saveNow,
    popId,
    popUuid,
  };
};
