import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { hasRole } from '../services/authApi';
import { loginSchema } from '../schemas/authSchemas';

function getSafeRedirect(next: string | null): string {
  if (!next || !next.startsWith('/') || next.startsWith('//')) return '';
  return next;
}

export default function LoginPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const nextUrl = getSafeRedirect(searchParams.get('next'));
  const { login, isLoading, error, clearError } = useAuthStore();
  const [form, setForm] = useState({ email: '', password: '' });
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setValidationErrors({});

    const result = loginSchema.safeParse(form);
    if (!result.success) {
      const errs: Record<string, string> = {};
      result.error.issues.forEach(issue => {
        errs[String(issue.path[0])] = issue.message;
      });
      setValidationErrors(errs);
      return;
    }

    const success = await login(form.email, form.password);
    if (success) {
      if (nextUrl) {
        navigate(nextUrl);
      } else {
        // Admin vai para home, demais para portal
        const user = useAuthStore.getState().user;
        navigate(hasRole(user, 'admin') || user?.is_superuser ? '/' : '/portal');
      }
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' as const, background: '#f4f6f9' }}>
      {/* Header institucional */}
      <header style={{
        background: '#fff', borderBottom: '3px solid #1351B4', padding: '12px 24px',
        display: 'flex', alignItems: 'center', gap: 12,
      }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 12, textDecoration: 'none' }}>
          <div style={{
            width: 32, height: 32, background: '#1351B4', borderRadius: 4,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: '#fff', fontWeight: 700, fontSize: 14,
          }}>MG</div>
          <div>
            <p style={{ margin: 0, fontWeight: 600, fontSize: 14, color: '#1B4F72' }}>MapaGov</p>
            <p style={{ margin: 0, fontSize: 11, color: '#666' }}>Ministério da Gestão e da Inovação em Serviços Públicos</p>
          </div>
        </Link>
        <Link to="/" style={{ marginLeft: 'auto', fontSize: 13, color: '#1351B4', textDecoration: 'none', fontWeight: 500 }}>
          &#8592; Voltar
        </Link>
      </header>

      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20, gap: 40 }}>
      <img
        src="/helena_login.png"
        alt="Helena"
        style={{ height: 340, objectFit: 'contain', flexShrink: 0 }}
      />
      <div style={{ width: '100%', maxWidth: 420, padding: 32, background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <h1 style={{ color: '#1B4F72', fontSize: 24, marginBottom: 8, textAlign: 'center' }}>MapaGov</h1>
        <p style={{ color: '#666', textAlign: 'center', marginBottom: 24 }}>Acesse sua conta</p>

        {error && (
          <div style={{ background: '#fdecea', color: '#b71c1c', padding: '10px 14px', borderRadius: 4, marginBottom: 16, fontSize: 14 }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>Email</label>
            <input
              type="email"
              value={form.email}
              onChange={e => setForm({ ...form, email: e.target.value })}
              style={{ width: '100%', padding: '10px 12px', border: '1px solid #ccc', borderRadius: 4, fontSize: 14, boxSizing: 'border-box' }}
              placeholder="seu.email@gestao.gov.br"
            />
            {validationErrors.email && <span style={{ color: '#b71c1c', fontSize: 12 }}>{validationErrors.email}</span>}
          </div>

          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>Senha</label>
            <input
              type="password"
              value={form.password}
              onChange={e => setForm({ ...form, password: e.target.value })}
              style={{ width: '100%', padding: '10px 12px', border: '1px solid #ccc', borderRadius: 4, fontSize: 14, boxSizing: 'border-box' }}
            />
            {validationErrors.password && <span style={{ color: '#b71c1c', fontSize: 12 }}>{validationErrors.password}</span>}
          </div>

          <button
            type="submit"
            disabled={isLoading}
            style={{
              width: '100%', padding: '12px', background: '#1351B4', color: '#fff',
              border: 'none', borderRadius: 4, fontSize: 16, fontWeight: 600, cursor: 'pointer',
              opacity: isLoading ? 0.7 : 1,
            }}
          >
            {isLoading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>

        <div style={{ marginTop: 20, textAlign: 'center', fontSize: 14 }}>
          <Link to="/recuperar-senha" style={{ color: '#1351B4', textDecoration: 'none' }}>Esqueci minha senha</Link>
        </div>
        <div style={{ marginTop: 12, textAlign: 'center', fontSize: 14, color: '#666' }}>
          Nao tem conta?{' '}
          <Link to="/registrar" style={{ color: '#1351B4', textDecoration: 'none', fontWeight: 500 }}>Cadastre-se</Link>
        </div>
      </div>
      </div>
    </div>
  );
}
