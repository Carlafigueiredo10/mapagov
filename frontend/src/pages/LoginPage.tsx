import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { loginSchema } from '../schemas/authSchemas';

function getSafeRedirect(next: string | null): string {
  if (!next || !next.startsWith('/') || next.startsWith('//')) return '/portal';
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
      navigate(nextUrl);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f4f6f9' }}>
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
  );
}
