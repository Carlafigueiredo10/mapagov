// Em vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
// @ts-ignore
import vitePluginEslint from 'vite-plugin-eslint'

export default defineConfig(({ mode }) => ({
  // Adicione o plugin aqui
  plugins: [react()], // ESLint temporariamente desabilitado

  // Base URL para assets em produção (Django WhiteNoise)
  // Em dev: '/' (raiz - Vite serve assets de /public)
  // Em prod: '/static/' (Django collectstatic)
  // IMPORTANTE: Componentes devem usar caminhos SEM /static/ - o build adiciona automaticamente
  base: mode === 'production' ? '/static/' : '/',

  server: {
    port: 5173,
    strictPort: true, // Não tenta outras portas se 5173 estiver ocupada
    // Proxy desabilitado - frontend usa VITE_API_URL diretamente
    // Em desenvolvimento: http://localhost:8000
    // Em produção: https://mapagov-api.onrender.com
  },
}))