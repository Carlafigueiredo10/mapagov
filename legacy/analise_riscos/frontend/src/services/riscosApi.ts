// riscosApi.ts - API Service para Análise de Riscos
import axios from 'axios';
import type {
  UploadPDFResponse,
  AnalyzeRisksRequest,
  AnalyzeRisksResponse,
  GeneratePDFResponse,
  POPInfo,
  AnswersMap,
} from '../components/AnaliseRiscos/types';

// URL da API - usa variável de ambiente ou URL relativa em produção
const API_BASE_URL = import.meta.env.VITE_API_URL ||
  (import.meta.env.PROD ? '' : 'http://localhost:8000');

// Instância do axios configurada
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Para cookies CSRF
});

// Interceptor para CSRF token
apiClient.interceptors.request.use((config) => {
  const csrfToken = getCsrfToken();
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  return config;
});

// Helper para obter CSRF token
function getCsrfToken(): string | null {
  const cookies = document.cookie.split(';');
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken') {
      return value;
    }
  }
  return null;
}

/**
 * Upload de PDF e extração de texto + metadados do POP
 */
export async function uploadPDFPOP(file: File): Promise<UploadPDFResponse> {
  try {
    const formData = new FormData();
    formData.append('pdf_file', file);

    const response = await apiClient.post<UploadPDFResponse>(
      '/api/extract-pdf/',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  } catch (error) {
    console.error('[uploadPDFPOP] Erro:', error);
    if (axios.isAxiosError(error)) {
      return {
        success: false,
        text: '',
        pop_info: {} as POPInfo,
        error: error.response?.data?.error || error.message,
      };
    }
    throw error;
  }
}

/**
 * Buscar POPs já mapeados (para selecionar ao invés de fazer upload)
 */
export async function fetchPOPsExistentes(): Promise<POPInfo[]> {
  try {
    // Endpoint fictício - ajustar conforme sua API
    const response = await apiClient.get<{ pops: POPInfo[] }>('/api/pops/');
    return response.data.pops || [];
  } catch (error) {
    console.error('[fetchPOPsExistentes] Erro:', error);
    return [];
  }
}

/**
 * Obter detalhes de um POP específico
 */
export async function fetchPOPById(popId: string): Promise<POPInfo | null> {
  try {
    const response = await apiClient.get<{ pop: POPInfo }>(`/api/pops/${popId}/`);
    return response.data.pop;
  } catch (error) {
    console.error('[fetchPOPById] Erro:', error);
    return null;
  }
}

/**
 * Analisar riscos com IA (Helena GRC)
 */
export async function analisarRiscos(
  request: AnalyzeRisksRequest
): Promise<AnalyzeRisksResponse> {
  try {
    console.log('[analisarRiscos] Enviando requisição:', {
      pop_titulo: request.pop_info.titulo,
      texto_length: request.pop_text.length,
      respostas_count: Object.keys(request.answers).length,
    });

    const response = await apiClient.post<AnalyzeRisksResponse>(
      '/api/analyze-risks/',
      request,
      {
        timeout: 120000, // 2 minutos - análise pode demorar
      }
    );

    console.log('[analisarRiscos] Resposta recebida:', {
      success: response.data.success,
      riscos_count: response.data.data?.riscos?.length,
    });

    return response.data;
  } catch (error) {
    console.error('[analisarRiscos] Erro:', error);
    if (axios.isAxiosError(error)) {
      return {
        success: false,
        error:
          error.response?.data?.error ||
          error.message ||
          'Erro ao analisar riscos',
      };
    }
    throw error;
  }
}

/**
 * Gerar PDF do relatório de riscos
 */
export async function gerarPDFRiscos(
  relatorioId: string
): Promise<GeneratePDFResponse> {
  try {
    const response = await apiClient.post<GeneratePDFResponse>(
      '/api/riscos/gerar-pdf/',
      { relatorio_id: relatorioId },
      {
        timeout: 60000, // 1 minuto
      }
    );

    return response.data;
  } catch (error) {
    console.error('[gerarPDFRiscos] Erro:', error);
    if (axios.isAxiosError(error)) {
      return {
        success: false,
        error:
          error.response?.data?.error ||
          error.message ||
          'Erro ao gerar PDF',
      };
    }
    throw error;
  }
}

/**
 * Helper: Download direto do PDF
 */
export function downloadPDF(url: string, filename: string = 'relatorio_riscos.pdf') {
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
}

/**
 * Auto-save de respostas (opcional - para persistência durante o chat)
 */
export async function autosaveRespostas(
  popId: string,
  answers: AnswersMap
): Promise<{ success: boolean }> {
  try {
    await apiClient.post('/api/riscos/autosave/', {
      pop_id: popId,
      answers,
    });
    return { success: true };
  } catch (error) {
    console.error('[autosaveRespostas] Erro:', error);
    return { success: false };
  }
}
