import axios from 'axios';

// URL da API - usa variável de ambiente ou URL relativa em produção
// Em produção (build), se VITE_API_URL não estiver definido, usa URL relativa
// Em dev, usa localhost:8000
const API_BASE_URL = import.meta.env.VITE_API_URL ||
  (import.meta.env.MODE === 'production' ? '' : 'http://localhost:8000');

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2 minutos - aumentado para processar condicionais complexas
});

// Adiciona header X-Requested-With para evitar bloqueio CORS
api.interceptors.request.use((config) => {
  config.headers['X-Requested-With'] = 'XMLHttpRequest';
  // Se precisar CSRF, descomente abaixo:
  // const csrfToken = getCookie('csrftoken');
  // if (csrfToken) {
  //   config.headers['X-CSRFToken'] = csrfToken;
  // }
  return config;
});

// Interceptor de resposta para retry automático em caso de timeout
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;

    // Se foi timeout e ainda não tentou retry
    if (error.code === 'ECONNABORTED' && !config._retry) {
      config._retry = true;
      console.warn('⚠️ Timeout na requisição. Tentando novamente...');
      return api(config);
    }

    // Se foi erro de rede
    if (error.message === 'Network Error') {
      console.error('❌ Erro de rede. Verifique se o backend está rodando.');
    }

    return Promise.reject(error);
  }
);


export default api;