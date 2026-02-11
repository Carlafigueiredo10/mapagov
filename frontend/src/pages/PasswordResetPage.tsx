import { useState } from 'react';
import { Link } from 'react-router-dom';
import { requestPasswordResetApi, fetchCsrf } from '../services/authApi';
import { passwordResetSchema } from '../schemas/authSchemas';

export default function PasswordResetPage() {
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const result = passwordResetSchema.safeParse({ email });
    if (!result.success) {
      setError(result.error.issues[0].message);
      return;
    }

    setLoading(true);
    try {
      await fetchCsrf();
      await requestPasswordResetApi(email);
      setSent(true);
    } catch {
      setSent(true); // Nao revelar se email existe
    } finally {
      setLoading(false);
    }
  };

  if (sent) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f4f6f9' }}>
        <div style={{ width: '100%', maxWidth: 420, padding: 32, background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.1)', textAlign: 'center' }}>
          <h2 style={{ color: '#1B4F72', marginBottom: 16 }}>Email enviado</h2>
          <p style={{ color: '#333' }}>Se o email estiver cadastrado, voce recebera um link de recuperacao.</p>
          <Link to="/login" style={{ color: '#1351B4', textDecoration: 'none', fontWeight: 500 }}>Voltar ao login</Link>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f4f6f9' }}>
      <div style={{ width: '100%', maxWidth: 420, padding: 32, background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <h1 style={{ color: '#1B4F72', fontSize: 24, marginBottom: 8, textAlign: 'center' }}>Recuperar senha</h1>
        <p style={{ color: '#666', textAlign: 'center', marginBottom: 24 }}>Informe seu email para receber o link de recuperacao</p>

        {error && (
          <div style={{ background: '#fdecea', color: '#b71c1c', padding: '10px 14px', borderRadius: 4, marginBottom: 16, fontSize: 14 }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 16 }}>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', border: '1px solid #ccc', borderRadius: 4, fontSize: 14, boxSizing: 'border-box' }}
              placeholder="seu.email@gestao.gov.br"
            />
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
            {loading ? 'Enviando...' : 'Enviar link'}
          </button>
        </form>

        <div style={{ marginTop: 16, textAlign: 'center', fontSize: 14 }}>
          <Link to="/login" style={{ color: '#1351B4', textDecoration: 'none' }}>Voltar ao login</Link>
        </div>
      </div>
    </div>
  );
}
