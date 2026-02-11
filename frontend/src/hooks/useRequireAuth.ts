import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

const PUBLIC_MVP = import.meta.env.VITE_PUBLIC_MVP_MODE === '1';
const DEV_BYPASS = import.meta.env.DEV;

/**
 * Hook para gate interno de paginas com landing publica.
 *
 * Em modo publico (MVP=1): sempre retorna true (sem auth).
 * Em modo auth (MVP=0): checa isAuthenticated.
 *   - Se autenticado, retorna true.
 *   - Se nao, redireciona para /login?next=<path_atual> e retorna false.
 *
 * Uso:
 *   const requireAuth = useRequireAuth();
 *   const handleIniciar = () => {
 *     if (requireAuth()) { setViewMode('tool'); }
 *   };
 */
export function useRequireAuth() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated } = useAuthStore();

  return (): boolean => {
    if (PUBLIC_MVP || DEV_BYPASS) return true;
    if (isAuthenticated) return true;
    navigate(`/login?next=${encodeURIComponent(location.pathname)}`, { replace: true });
    return false;
  };
}
