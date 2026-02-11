import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { registerSchema } from '../schemas/authSchemas';

export default function RegisterPage() {
  const navigate = useNavigate();
  const { register, isLoading, error, clearError } = useAuthStore();
  const [form, setForm] = useState({
    email: '', password: '', password_confirm: '',
    nome_completo: '', cargo: '', area_codigo: '',
  });
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [success, setSuccess] = useState(false);
  const [profileType, setProfileType] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setValidationErrors({});

    const result = registerSchema.safeParse(form);
    if (!result.success) {
      const errs: Record<string, string> = {};
      result.error.issues.forEach(issue => {
        errs[String(issue.path[0])] = issue.message;
      });
      setValidationErrors(errs);
      return;
    }

    const res = await register(form);
    if (res.success) {
      setSuccess(true);
      setProfileType(res.profile_type || '');
    }
  };

  const update = (field: string, value: string) => setForm({ ...form, [field]: value });

  if (success) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f4f6f9' }}>
        <div style={{ width: '100%', maxWidth: 480, padding: 32, background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.1)', textAlign: 'center' }}>
          <h2 style={{ color: '#1B4F72', marginBottom: 16 }}>Cadastro realizado</h2>
          <p style={{ color: '#333', marginBottom: 8 }}>
            Verifique seu email para liberar o acesso.
          </p>
          {profileType === 'externo' && (
            <p style={{ color: '#666', fontSize: 14 }}>
              Como seu email nao pertence ao MGI, seu cadastro sera analisado pela equipe responsavel.
              Voce sera avisado por email.
            </p>
          )}
          <Link to="/login" style={{ color: '#1351B4', textDecoration: 'none', fontWeight: 500 }}>Ir para login</Link>
        </div>
      </div>
    );
  }

  const inputStyle = { width: '100%', padding: '10px 12px', border: '1px solid #ccc', borderRadius: 4, fontSize: 14, boxSizing: 'border-box' as const };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f4f6f9' }}>
      <div style={{ width: '100%', maxWidth: 480, padding: 32, background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <h1 style={{ color: '#1B4F72', fontSize: 24, marginBottom: 8, textAlign: 'center' }}>Cadastro</h1>
        <p style={{ color: '#666', textAlign: 'center', marginBottom: 24 }}>Crie sua conta no MapaGov</p>

        {error && (
          <div style={{ background: '#fdecea', color: '#b71c1c', padding: '10px 14px', borderRadius: 4, marginBottom: 16, fontSize: 14 }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 14 }}>
            <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>Nome completo *</label>
            <input type="text" value={form.nome_completo} onChange={e => update('nome_completo', e.target.value)} style={inputStyle} />
            {validationErrors.nome_completo && <span style={{ color: '#b71c1c', fontSize: 12 }}>{validationErrors.nome_completo}</span>}
          </div>

          <div style={{ marginBottom: 14 }}>
            <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>Email institucional *</label>
            <input type="email" value={form.email} onChange={e => update('email', e.target.value)} style={inputStyle} placeholder="seu.email@gestao.gov.br" />
            {validationErrors.email && <span style={{ color: '#b71c1c', fontSize: 12 }}>{validationErrors.email}</span>}
          </div>

          <div style={{ marginBottom: 14 }}>
            <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>Cargo</label>
            <input type="text" value={form.cargo} onChange={e => update('cargo', e.target.value)} style={inputStyle} />
          </div>

          <div style={{ marginBottom: 14 }}>
            <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>Senha *</label>
            <input type="password" value={form.password} onChange={e => update('password', e.target.value)} style={inputStyle} />
            {validationErrors.password && <span style={{ color: '#b71c1c', fontSize: 12 }}>{validationErrors.password}</span>}
          </div>

          <div style={{ marginBottom: 20 }}>
            <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>Confirmar senha *</label>
            <input type="password" value={form.password_confirm} onChange={e => update('password_confirm', e.target.value)} style={inputStyle} />
            {validationErrors.password_confirm && <span style={{ color: '#b71c1c', fontSize: 12 }}>{validationErrors.password_confirm}</span>}
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
            {isLoading ? 'Cadastrando...' : 'Cadastrar'}
          </button>
        </form>

        <div style={{ marginTop: 16, textAlign: 'center', fontSize: 14, color: '#666' }}>
          Ja tem conta?{' '}
          <Link to="/login" style={{ color: '#1351B4', textDecoration: 'none', fontWeight: 500 }}>Fazer login</Link>
        </div>
      </div>
    </div>
  );
}
