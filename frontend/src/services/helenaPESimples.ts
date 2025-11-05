/**
 * Helena PE API Simplificada
 *
 * Service para comunicação com backend do Planejamento Estratégico
 * Versão simplificada focada apenas no essencial
 */

// URL da API - usa variável de ambiente ou URL relativa em produção
const API_BASE_URL = import.meta.env.VITE_API_URL ||
  (import.meta.env.PROD ? '' : 'http://localhost:8000');

const API_BASE = `${API_BASE_URL}/api/planejamento-estrategico`;

export interface SessionData {
  session_id: string;
  estado_atual: string;
  modelo_selecionado?: string;
  percentual_conclusao: number;
  estrutura_planejamento?: any;
  diagnostico?: any;
}

export interface ApiResponse {
  resposta: string;
  session_data: SessionData;
  opcoes?: string[];
  progresso?: string;
}

export interface ConfirmacaoModeloResponse {
  session_data: SessionData;
  mensagem_confirmacao: string;
  modelo_selecionado: string;
  info_modelo: {
    nome: string;
    nome_completo: string;
    descricao: string;
    icone: string;
  };
}

class HelenaPEService {
  private sessionData: SessionData | null = null;

  /**
   * Inicia nova sessão
   */
  async iniciarSessao(): Promise<ApiResponse> {
    try {
      console.log('[Helena PE] Iniciando sessão...', API_BASE);
      const response = await fetch(`${API_BASE}/iniciar/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      console.log('[Helena PE] Response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      console.log('[Helena PE] Dados recebidos:', data);

      // Salva session_data completo
      this.sessionData = data.session_data;
      console.log('[Helena PE] Session data salvo:', this.sessionData);

      return {
        resposta: data.mensagem_inicial,
        session_data: data.session_data
      };
    } catch (error) {
      console.error('[Helena PE] Erro ao iniciar sessão:', error);
      throw error;
    }
  }

  /**
   * Envia mensagem do usuário
   */
  async enviarMensagem(mensagem: string, sessionData?: SessionData): Promise<ApiResponse> {
    // Usa sessionData fornecido ou o armazenado internamente
    const currentSessionData = sessionData || this.sessionData;

    console.log('[Helena PE] Tentando enviar mensagem. Session data:', currentSessionData);

    if (!currentSessionData) {
      throw new Error('Sessão não iniciada');
    }

    try {
      console.log('[Helena PE] Enviando mensagem:', mensagem);
      const response = await fetch(`${API_BASE}/processar/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mensagem,
          session_data: currentSessionData
        })
      });

      console.log('[Helena PE] Response status (processar):', response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      console.log('[Helena PE] Resposta recebida:', data);

      // Atualiza session_data local
      this.sessionData = data.session_data;

      return data;
    } catch (error) {
      console.error('[Helena PE] Erro ao enviar mensagem:', error);
      throw error;
    }
  }

  /**
   * Inicia modelo diretamente (sem seleção manual)
   */
  async iniciarModeloDireto(modeloId: string): Promise<ConfirmacaoModeloResponse> {
    try {
      console.log('[Helena PE] Iniciando modelo direto:', modeloId);
      const response = await fetch(`${API_BASE}/iniciar-modelo/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ modelo: modeloId })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      console.log('[Helena PE] Confirmação recebida:', data);

      // Salva session_data
      this.sessionData = data.session_data;

      return data;
    } catch (error) {
      console.error('[Helena PE] Erro ao iniciar modelo direto:', error);
      throw error;
    }
  }

  /**
   * Confirma modelo e inicia agente
   */
  async confirmarModelo(sessionData: SessionData): Promise<ApiResponse> {
    try {
      console.log('[Helena PE] Confirmando modelo...');
      const response = await fetch(`${API_BASE}/confirmar-modelo/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_data: sessionData })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      console.log('[Helena PE] Agente iniciado:', data);

      // Atualiza session_data
      this.sessionData = data.session_data;

      return data;
    } catch (error) {
      console.error('[Helena PE] Erro ao confirmar modelo:', error);
      throw error;
    }
  }

  /**
   * Reseta sessão
   */
  resetar() {
    this.sessionData = null;
  }

  /**
   * Retorna session_data atual
   */
  getSessionData(): SessionData | null {
    return this.sessionData;
  }
}

export const helenaPEService = new HelenaPEService();
export default helenaPEService;
