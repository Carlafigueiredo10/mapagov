import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { confirmPasswordResetApi, fetchCsrf } from '../services/authApi';
import { newPasswordSchema } from '../schemas/authSchemas';

export default function PasswordResetConfirmPage() {
  const { uid, token } = useParams<{ uid: string; token: string }>();
  const [form, setForm] = useState({ password: '', password_confirm: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const result = newPasswordSchema.safeParse(form);
    if (!result.success) {
      setError(result.error.issues[0].message);
      return;
    }

    if (!uid || !token) {
      setError('Link invalido.');
      return;
    }

    setLoading(true);
    try {
      await fetchCsrf();
      await confirmPasswordResetApi(uid, token, form.password);
      setSuccess(true);
    } catch (err: any) {
      setError(err.response?.data?.erro || 'Erro ao alterar senha.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f4f6f9' }}>
        <div style={{ width: '100%', maxWidth: 420, padding: 32, background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.1)', textAlign: 'center' }}>
          <h2 style={{ color: '#1B4F72', marginBottom: 16 }}>Senha alterada</h2>
          <p style={{ color: '#333', marginBottom: 16 }}>Sua senha foi redefinida com sucesso.</p>
          <Link to="/login" style={{ color: '#1351B4', textDecoration: 'none', fontWeight: 500 }}>Fazer login</Link>
        </div>
      </div>
    );
  }

  const inputStyle = { width: '100%', padding: '10px 12px', border: '1px solid #ccc', borderRadius: 4, fontSize: 14, boxSizing: 'border-box' as const };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f4f6f9' }}>
      <div style={{ width: '100%', maxWidth: 420, padding: 32, background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <h1 style={{ color: '#1B4F72', fontSize: 24, marginBottom: 8, textAlign: 'center' }}>Nova senha</h1>

        {error && (
          <div style={{ background: '#fdecea', color: '#b71c1c', padding: '10px 14px', borderRadius: 4, marginBottom: 16, fontSize: 14 }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 14 }}>
            <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>Nova senha</label>
            <input type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} style={inputStyle} />
            <p style={{ margin: '4px 0 0', fontSize: 12, color: '#888' }}>No mínimo 6 caracteres, com letra maiúscula, minúscula, número e símbolo.</p>
          </div>
          <div style={{ marginBottom: 20 }}>
            <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>Confirmar nova senha</label>
            <input type="password" value={form.password_confirm} onChange={e => setForm({ ...form, password_confirm: e.target.value })} style={inputStyle} />
          </div>
          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%', padding: '12px', background: '#1351B4', color: '#fff',
              border: 'none', borderRadius: 4, fontSize: 16, fontWeight: 600, cursor: 'pointer',
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading ? 'Salvando...' : 'Salvar nova senha'}
          </button>
        </form>
      </div>
    </div>
  );
}
