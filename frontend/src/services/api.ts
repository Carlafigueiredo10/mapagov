import axios from 'axios';

// URL da API - usa variável de ambiente ou localhost em dev
const API_BASE_URL = import.meta.env.VITE_API_URL ||
  (import.meta.env.PROD ? '' : 'http://127.0.0.1:8000');

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2 minutos - aumentado para processar condicionais complexas
  withCredentials: true, // CRITICO: Permite envio de cookies para sessao Django
});

// Helper para ler cookie por nome
function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? match[2] : null;
}

// Adiciona headers CSRF e X-Requested-With
api.interceptors.request.use((config) => {
  config.headers['X-Requested-With'] = 'XMLHttpRequest';
  const csrfToken = getCookie('csrftoken');
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  return config;
});

// Interceptor de resposta: retry em timeout + redirect em 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;

    // Session expirada — redirect para login (exceto se ja esta em rota de auth)
    if (
      error.response?.status === 401 &&
      !config.url?.includes('/auth/')
    ) {
      window.location.href = '/login';
      return Promise.reject(error);
    }

    // CSRF token ausente ou expirado — busca e retenta uma vez
    if (
      error.response?.status === 403 &&
      !config._csrfRetry &&
      !getCookie('csrftoken')
    ) {
      config._csrfRetry = true;
      await api.get('/auth/csrf/');
      const newToken = getCookie('csrftoken');
      if (newToken) {
        config.headers['X-CSRFToken'] = newToken;
      }
      return api(config);
    }

    // Se foi timeout e ainda nao tentou retry
    if (error.code === 'ECONNABORTED' && !config._retry) {
      config._retry = true;
      return api(config);
    }

    return Promise.reject(error);
  }
);


export default api;