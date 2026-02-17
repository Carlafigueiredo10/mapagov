import { useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { hasRole } from '../../services/authApi';

const PUBLIC_MVP = import.meta.env.VITE_PUBLIC_MVP_MODE === '1';

export default function AdminRoute({ children }: { children: React.ReactNode }) {
  if (PUBLIC_MVP) return <>{children}</>;

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

  // AdminRoute: somente role=admin ou is_superuser
  if (!hasRole(user, 'admin') && !user?.is_superuser) {
    return <Navigate to="/portal" replace />;
  }

  return <>{children}</>;
}
