/**
 * Gerenciador de Sessão - Helena PE
 * Persistência leve com sessionStorage
 */

import { SessionData } from '../types/planejamento';

const SESSION_KEY = 'helenaPE_session';
const MESSAGES_KEY = 'helenaPE_messages';

export const sessionManager = {
  /**
   * Salva sessão no sessionStorage
   */
  saveSession(sessionData: SessionData) {
    try {
      sessionStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
    } catch (error) {
      console.warn('[SessionManager] Erro ao salvar sessão:', error);
    }
  },

  /**
   * Recupera sessão do sessionStorage
   */
  loadSession(): SessionData | null {
    try {
      const saved = sessionStorage.getItem(SESSION_KEY);
      return saved ? JSON.parse(saved) : null;
    } catch (error) {
      console.warn('[SessionManager] Erro ao carregar sessão:', error);
      return null;
    }
  },

  /**
   * Limpa sessão
   */
  clearSession() {
    try {
      sessionStorage.removeItem(SESSION_KEY);
      sessionStorage.removeItem(MESSAGES_KEY);
    } catch (error) {
      console.warn('[SessionManager] Erro ao limpar sessão:', error);
    }
  },

  /**
   * Salva histórico de mensagens
   */
  saveMessages(messages: any[]) {
    try {
      sessionStorage.setItem(MESSAGES_KEY, JSON.stringify(messages));
    } catch (error) {
      console.warn('[SessionManager] Erro ao salvar mensagens:', error);
    }
  },

  /**
   * Recupera histórico de mensagens
   */
  loadMessages(): any[] {
    try {
      const saved = sessionStorage.getItem(MESSAGES_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch (error) {
      console.warn('[SessionManager] Erro ao carregar mensagens:', error);
      return [];
    }
  },

  /**
   * Verifica se há sessão ativa
   */
  hasActiveSession(): boolean {
    const session = this.loadSession();
    return session !== null && session.session_id !== undefined;
  }
};

export default sessionManager;
