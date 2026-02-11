import { Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export default function PendingAccessPage() {
  const { user, logout } = useAuthStore();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f4f6f9' }}>
      <div style={{ width: '100%', maxWidth: 480, padding: 32, background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.1)', textAlign: 'center' }}>
        <h2 style={{ color: '#1B4F72', marginBottom: 16 }}>Acesso pendente</h2>

        {user && !user.email_verified ? (
          <>
            <p style={{ color: '#333', marginBottom: 8 }}>
              Verifique seu email para liberar o acesso.
            </p>
            <p style={{ color: '#666', fontSize: 14 }}>
              Enviamos um link de verificacao para <strong>{user.email}</strong>.
              Confira sua caixa de entrada e spam.
            </p>
          </>
        ) : user?.access_status === 'pending' ? (
          <>
            <p style={{ color: '#333', marginBottom: 8 }}>
              Seu cadastro esta em analise pela equipe responsavel.
            </p>
            <p style={{ color: '#666', fontSize: 14 }}>
              Voce sera avisado por email quando o acesso for liberado.
            </p>
          </>
        ) : user?.access_status === 'rejected' ? (
          <>
            <p style={{ color: '#b71c1c', marginBottom: 8 }}>
              Seu cadastro nao foi aprovado.
            </p>
            <p style={{ color: '#666', fontSize: 14 }}>
              Em caso de duvidas, entre em contato com a equipe de administracao.
            </p>
          </>
        ) : (
          <p style={{ color: '#666' }}>Verificando status do acesso...</p>
        )}

        <div style={{ marginTop: 24, display: 'flex', gap: 16, justifyContent: 'center' }}>
          <Link to="/" style={{ color: '#1351B4', textDecoration: 'none', fontSize: 14 }}>Pagina inicial</Link>
          <button onClick={handleLogout} style={{ background: 'none', border: 'none', color: '#b71c1c', cursor: 'pointer', fontSize: 14 }}>
            Sair
          </button>
        </div>
      </div>
    </div>
  );
}
