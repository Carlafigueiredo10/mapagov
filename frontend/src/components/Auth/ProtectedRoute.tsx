import { useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

const PUBLIC_MVP = import.meta.env.VITE_PUBLIC_MVP_MODE === '1';
const DEV_BYPASS = import.meta.env.DEV;

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  if (PUBLIC_MVP || DEV_BYPASS) return <>{children}</>;

  const { isAuthenticated, user, isLoading, checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
        <p style={{ color: '#666' }}>Verificando acesso...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (user && !user.email_verified) {
    return <Navigate to="/acesso-pendente" replace />;
  }

  if (user && user.access_status !== 'approved') {
    return <Navigate to="/acesso-pendente" replace />;
  }

  return <>{children}</>;
}
