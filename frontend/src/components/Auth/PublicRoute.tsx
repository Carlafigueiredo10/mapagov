import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

const PUBLIC_MVP = import.meta.env.VITE_PUBLIC_MVP_MODE === '1';

/** Redireciona usuarios ja autenticados+aprovados para /portal */
export default function PublicRoute({ children }: { children: React.ReactNode }) {
  if (PUBLIC_MVP) return <>{children}</>;

  const { isAuthenticated, user } = useAuthStore();

  if (isAuthenticated && user?.can_access) {
    return <Navigate to="/portal" replace />;
  }

  return <>{children}</>;
}
