import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { UserInfo } from '../services/authApi';
import { fetchCsrf, loginApi, logoutApi, getMeApi, registerApi } from '../services/authApi';
import type { RegisterData } from '../services/authApi';

interface AuthState {
  user: UserInfo | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  register: (data: RegisterData) => Promise<{ success: boolean; profile_type?: string; access_status?: string; error?: string }>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          // Garante CSRF token antes do POST
          await fetchCsrf();
          const data = await loginApi(email, password);
          set({
            user: data.user,
            isAuthenticated: true,
            isLoading: false,
          });
          return true;
        } catch (err: any) {
          const msg = err.response?.data?.erro || err.response?.data?.error || 'Erro ao fazer login.';
          const code = err.response?.data?.code;
          set({ isLoading: false, error: msg });

          // Retornar info extra para redirect (email_not_verified, access_pending)
          if (code === 'email_not_verified' || code === 'access_pending') {
            set({ error: msg });
          }
          return false;
        }
      },

      logout: async () => {
        try {
          await logoutApi();
        } catch {
          // Ignora erros de logout (sessao ja expirou)
        }
        set({ user: null, isAuthenticated: false, error: null });
      },

      register: async (data: RegisterData) => {
        set({ isLoading: true, error: null });
        try {
          await fetchCsrf();
          const res = await registerApi(data);
          set({ isLoading: false });
          return {
            success: true,
            profile_type: res.profile_type,
            access_status: res.access_status,
          };
        } catch (err: any) {
          const errors = err.response?.data?.errors;
          let msg = 'Erro ao registrar.';
          if (errors) {
            // Pega primeira mensagem de erro
            const firstKey = Object.keys(errors)[0];
            const firstError = errors[firstKey];
            msg = Array.isArray(firstError) ? firstError[0] : String(firstError);
          }
          set({ isLoading: false, error: msg });
          return { success: false, error: msg };
        }
      },

      checkAuth: async () => {
        // Se nao tem user no cache, nao tenta
        if (!get().isAuthenticated && !get().user) {
          set({ isLoading: false });
          return;
        }

        set({ isLoading: true });
        try {
          const user = await getMeApi();
          set({ user, isAuthenticated: true, isLoading: false });
        } catch {
          // Sessao expirou
          set({ user: null, isAuthenticated: false, isLoading: false });
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'mapagov-auth',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
