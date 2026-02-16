// Em vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
// @ts-ignore
import vitePluginEslint from 'vite-plugin-eslint'

export default defineConfig(({ mode }) => ({
  plugins: [react()],

  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.ts',
    include: ['src/**/*.test.{ts,tsx}'],
  },

  // Base URL para assets em produção (Django WhiteNoise)
  // Em dev: '/' (raiz - Vite serve assets de /public)
  // Em prod: '/static/' (Django collectstatic)
  // IMPORTANTE: Componentes devem usar caminhos SEM /static/ - o build adiciona automaticamente
  base: mode === 'production' ? '/static/' : '/',

  server: {
    port: 5173,
    strictPort: true, // Não tenta outras portas se 5173 estiver ocupada
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
}))