// Em vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
// @ts-ignore
import vitePluginEslint from 'vite-plugin-eslint'

export default defineConfig({
  // Adicione o plugin aqui
  plugins: [react()], // ESLint temporariamente desabilitado

  server: {
    port: 5173,
    strictPort: true, // Não tenta outras portas se 5173 estiver ocupada
    // Proxy desabilitado - frontend usa VITE_API_URL diretamente
    // Em desenvolvimento: http://localhost:8000
    // Em produção: https://mapagov-api.onrender.com
  },
})