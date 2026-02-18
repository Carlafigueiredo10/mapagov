import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { registerSchema } from '../schemas/authSchemas';
import { fetchPublicAreas } from '../services/authApi';
import type { PublicArea } from '../services/authApi';

// Checklist de requisitos da senha
const PASSWORD_RULES = [
  { key: 'length', label: 'Mínimo 6 caracteres', test: (v: string) => v.length >= 6 },
  { key: 'upper', label: 'Letra maiúscula', test: (v: string) => /[A-Z]/.test(v) },
  { key: 'lower', label: 'Letra minúscula', test: (v: string) => /[a-z]/.test(v) },
  { key: 'number', label: 'Número', test: (v: string) => /[0-9]/.test(v) },
  { key: 'symbol', label: 'Símbolo (!@#$%...)', test: (v: string) => /[^A-Za-z0-9]/.test(v) },
];

export default function RegisterPage() {
  const { register, isLoading, error, clearError } = useAuthStore();
  const [form, setForm] = useState({
    email: '@gestao.gov.br', password: '', password_confirm: '',
    nome_completo: '', cargo: '', area_codigo: '',
    setor_trabalho: '',
  });
  const [isDecipex, setIsDecipex] = useState<boolean | null>(null);
  const [areas, setAreas] = useState<PublicArea[]>([]);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [success, setSuccess] = useState(false);
  const [profileType, setProfileType] = useState<string>('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  useEffect(() => {
    fetchPublicAreas().then(setAreas).catch(() => {});
  }, []);

  const isGestaoEmail = form.email.trim().toLowerCase().endsWith('@gestao.gov.br');
  const isExternalEmail = form.email.includes('@') && !isGestaoEmail;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setValidationErrors({});

    if (isDecipex === null) {
      setValidationErrors({ is_decipex: 'Selecione sua vinculação' });
      return;
    }

    const payload = {
      ...form,
      is_decipex: isDecipex,
    };

    const result = registerSchema.safeParse(payload);
    if (!result.success) {
      const errs: Record<string, string> = {};
      result.error.issues.forEach(issue => {
        errs[String(issue.path[0])] = issue.message;
      });
      setValidationErrors(errs);
      return;
    }

    const res = await register(payload);
    if (res.success) {
      setSuccess(true);
      setProfileType(res.profile_type || '');
    }
  };

  const update = (field: string, value: string) => setForm({ ...form, [field]: value });

  // --- Tela de sucesso ---
  if (success) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f4f6f9' }}>
        <div style={{ width: '100%', maxWidth: 480, padding: 32, background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.1)', textAlign: 'center' }}>
          <img src="/helena_cadastro.png" alt="Helena" style={{ width: 56, height: 56, borderRadius: '50%', marginBottom: 12 }} />
          <h2 style={{ color: '#1B4F72', marginBottom: 16 }}>Cadastro realizado</h2>
          <p style={{ color: '#333', marginBottom: 8 }}>
            Verifique seu e-mail para liberar o acesso.
          </p>
          <p style={{ color: '#888', fontSize: 13, marginBottom: 8 }}>
            Caso nao encontre, verifique a pasta de spam.
          </p>
          {profileType === 'externo' && (
            <p style={{ color: '#666', fontSize: 14 }}>
              Como seu e-mail não pertence ao MGI, seu cadastro ficará pendente de autorização.
              Você será avisado por e-mail.
            </p>
          )}
          <Link to="/login" style={{ color: '#1351B4', textDecoration: 'none', fontWeight: 500 }}>Ir para login</Link>
        </div>
      </div>
    );
  }

  // --- Estilos ---
  const inputStyle = { width: '100%', padding: '10px 12px', border: '1px solid #ccc', borderRadius: 4, fontSize: 14, boxSizing: 'border-box' as const };
  const selectStyle = { ...inputStyle, background: '#fff', cursor: 'pointer' as const };
  const labelStyle = { display: 'block' as const, marginBottom: 4, fontWeight: 500, fontSize: 14, color: '#333' };
  const errorStyle = { color: '#b71c1c', fontSize: 12, marginTop: 4, display: 'block' as const };
  const fieldStyle = { marginBottom: 16 };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' as const, background: '#f4f6f9' }}>
      {/* Header institucional */}
      <header style={{
        background: '#fff', borderBottom: '3px solid #1351B4', padding: '12px 24px',
        display: 'flex', alignItems: 'center', gap: 12,
      }}>
        <Link to="/sobre" style={{ display: 'flex', alignItems: 'center', gap: 12, textDecoration: 'none' }}>
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
        <Link to="/sobre" style={{ marginLeft: 'auto', fontSize: 13, color: '#1351B4', textDecoration: 'none', fontWeight: 500 }}>
          &#8592; Voltar
        </Link>
      </header>

      {/* Conteúdo principal */}
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
        <div style={{
          display: 'flex', width: '100%', maxWidth: 920,
          background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
          overflow: 'hidden',
        }}>

          {/* Coluna esquerda — Helena + contexto */}
          <div style={{
            width: 300, flexShrink: 0, padding: '32px 24px',
            display: 'flex', flexDirection: 'column', alignItems: 'center',
            borderRight: '1px solid #e8e8e8',
          }}>
            <img src="/helena_cadastro.png" alt="Helena — Assistente MapaGov" style={{ width: 180, height: 180, objectFit: 'contain', marginBottom: 16 }} />
            <p style={{ margin: 0, fontWeight: 600, fontSize: 16, color: '#1B4F72' }}>Helena</p>
            <p style={{ margin: '2px 0 16px', fontSize: 13, color: '#666' }}>Assistente MapaGov</p>

            <p style={{ fontSize: 13, lineHeight: 1.6, color: '#444', textAlign: 'center', marginBottom: 20 }}>
              Ao criar sua conta, você terá acesso às ferramentas de apoio à governança institucional.
            </p>

            <div style={{ width: '100%', fontSize: 13, color: '#555' }}>
              <p style={{ margin: '0 0 8px', fontWeight: 600, color: '#1B4F72', fontSize: 12, textTransform: 'uppercase' as const, letterSpacing: 0.5 }}>Produtos disponíveis</p>
              <ul style={{ margin: 0, paddingLeft: 18, display: 'flex', flexDirection: 'column', gap: 6 }}>
                <li>Mapeamento de Processos</li>
                <li>Análise de Riscos</li>
                <li>Planejamento Estratégico</li>
                <li>Catálogo de Processos</li>
              </ul>
            </div>

            <div style={{ marginTop: 'auto', paddingTop: 24, textAlign: 'center', fontSize: 11, color: '#999', lineHeight: 1.5 }}>
              <p style={{ margin: '0 0 8px' }}>Decipex — MGI</p>
              <p style={{ margin: 0 }}>Seus dados são tratados conforme a Lei Geral de Proteção de Dados (LGPD). Em caso de dúvidas, entre em contato com a administração do sistema.</p>
            </div>
          </div>

          {/* Coluna direita — Formulário */}
          <div style={{ flex: 1, padding: '32px 32px', overflowY: 'auto', maxHeight: '90vh' }}>
            <h1 style={{ color: '#1B4F72', fontSize: 22, marginBottom: 4 }}>Criar conta</h1>
            <p style={{ color: '#666', marginBottom: 20, fontSize: 14 }}>Preencha os dados para acessar o MapaGov</p>

            {error && (
              <div role="alert" style={{ background: '#fdecea', color: '#b71c1c', padding: '10px 14px', borderRadius: 4, marginBottom: 16, fontSize: 14 }}>
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} noValidate>
              {/* Nome */}
              <div style={fieldStyle}>
                <label htmlFor="reg-nome" style={labelStyle}>Nome completo *</label>
                <input id="reg-nome" type="text" value={form.nome_completo} onChange={e => update('nome_completo', e.target.value)} style={inputStyle} autoComplete="name" />
                {validationErrors.nome_completo && <span style={errorStyle} role="alert">{validationErrors.nome_completo}</span>}
              </div>

              {/* Email */}
              <div style={fieldStyle}>
                <label htmlFor="reg-email" style={labelStyle}>E-mail institucional *</label>
                <input id="reg-email" type="email" value={form.email} onChange={e => update('email', e.target.value)} style={inputStyle} placeholder="nome@gestao.gov.br" autoComplete="email" />
                {validationErrors.email && <span style={errorStyle} role="alert">{validationErrors.email}</span>}
                {isExternalEmail && (
                  <p role="status" style={{ margin: '6px 0 0', fontSize: 12, color: '#92400e', background: '#fef3c7', padding: '8px 10px', borderRadius: 4 }}>
                    E-mail fora do domínio @gestao.gov.br. O cadastro ficará pendente de autorização.
                  </p>
                )}
              </div>

              {/* Cargo */}
              <div style={fieldStyle}>
                <label htmlFor="reg-cargo" style={labelStyle}>Cargo</label>
                <input id="reg-cargo" type="text" value={form.cargo} onChange={e => update('cargo', e.target.value)} style={inputStyle} autoComplete="organization-title" />
              </div>

              {/* Vinculação — radio buttons */}
              <fieldset style={{ border: 'none', padding: 0, margin: 0, marginBottom: 16 }}>
                <legend style={{ ...labelStyle, marginBottom: 4 }}>Vinculação institucional *</legend>
                <p style={{ margin: '0 0 10px', fontSize: 12, color: '#666' }}>
                  Decipex: Departamento de Centralização de Inativos, Pensionistas e Órgãos Extintos.
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', fontSize: 14, color: '#333' }}>
                    <input
                      type="radio"
                      name="vinculacao"
                      checked={isDecipex === true}
                      onChange={() => { setIsDecipex(true); setForm(f => ({ ...f, setor_trabalho: '' })); }}
                      style={{ accentColor: '#1351B4', width: 18, height: 18 }}
                    />
                    Trabalho na Decipex
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', fontSize: 14, color: '#333' }}>
                    <input
                      type="radio"
                      name="vinculacao"
                      checked={isDecipex === false}
                      onChange={() => { setIsDecipex(false); setForm(f => ({ ...f, area_codigo: '' })); }}
                      style={{ accentColor: '#1351B4', width: 18, height: 18 }}
                    />
                    Não trabalho na Decipex
                  </label>
                </div>
                {validationErrors.is_decipex && <span style={errorStyle} role="alert">{validationErrors.is_decipex}</span>}
              </fieldset>

              {/* Área (Decipex = sim) */}
              {isDecipex === true && (
                <div style={fieldStyle}>
                  <label htmlFor="reg-area" style={labelStyle}>Área da Decipex *</label>
                  <select id="reg-area" value={form.area_codigo} onChange={e => update('area_codigo', e.target.value)} style={selectStyle}>
                    <option value="">Selecione a área</option>
                    {areas.map(a => (
                      <option key={a.codigo} value={a.codigo}>{a.nome_curto}</option>
                    ))}
                  </select>
                  {validationErrors.area_codigo && <span style={errorStyle} role="alert">{validationErrors.area_codigo}</span>}
                </div>
              )}

              {/* Setor (Decipex = não) */}
              {isDecipex === false && (
                <div style={fieldStyle}>
                  <label htmlFor="reg-setor" style={labelStyle}>Setor de trabalho *</label>
                  <input id="reg-setor" type="text" value={form.setor_trabalho} onChange={e => update('setor_trabalho', e.target.value)} style={inputStyle} placeholder="Ex.: Coordenação de Logística" />
                  {validationErrors.setor_trabalho && <span style={errorStyle} role="alert">{validationErrors.setor_trabalho}</span>}
                </div>
              )}

              {/* Senha com toggle e checklist */}
              <div style={fieldStyle}>
                <label htmlFor="reg-password" style={labelStyle}>Senha *</label>
                <div style={{ position: 'relative' as const }}>
                  <input
                    id="reg-password"
                    type={showPassword ? 'text' : 'password'}
                    value={form.password}
                    onChange={e => update('password', e.target.value)}
                    style={{ ...inputStyle, paddingRight: 44 }}
                    autoComplete="new-password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(v => !v)}
                    aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
                    style={{
                      position: 'absolute', right: 8, top: '50%', transform: 'translateY(-50%)',
                      background: 'none', border: 'none', cursor: 'pointer', fontSize: 13,
                      color: '#666', padding: '4px',
                    }}
                  >
                    {showPassword ? 'Ocultar' : 'Mostrar'}
                  </button>
                </div>
                {/* Checklist de critérios — 2 colunas */}
                <ul style={{ listStyle: 'none', padding: 0, margin: '6px 0 0', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2px 12px' }}>
                  {PASSWORD_RULES.map(rule => {
                    const ok = form.password.length > 0 && rule.test(form.password);
                    return (
                      <li key={rule.key} style={{ fontSize: 12, color: ok ? '#2e7d32' : '#888', display: 'flex', alignItems: 'center', gap: 4 }}>
                        <span style={{ fontSize: 13 }}>{ok ? '\u2713' : '\u2022'}</span>
                        {rule.label}
                      </li>
                    );
                  })}
                </ul>
                {validationErrors.password && <span style={errorStyle} role="alert">{validationErrors.password}</span>}
              </div>

              {/* Confirmar senha */}
              <div style={{ marginBottom: 20 }}>
                <label htmlFor="reg-confirm" style={labelStyle}>Confirmar senha *</label>
                <div style={{ position: 'relative' as const }}>
                  <input
                    id="reg-confirm"
                    type={showConfirm ? 'text' : 'password'}
                    value={form.password_confirm}
                    onChange={e => update('password_confirm', e.target.value)}
                    style={{ ...inputStyle, paddingRight: 44 }}
                    autoComplete="new-password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirm(v => !v)}
                    aria-label={showConfirm ? 'Ocultar confirmação' : 'Mostrar confirmação'}
                    style={{
                      position: 'absolute', right: 8, top: '50%', transform: 'translateY(-50%)',
                      background: 'none', border: 'none', cursor: 'pointer', fontSize: 13,
                      color: '#666', padding: '4px',
                    }}
                  >
                    {showConfirm ? 'Ocultar' : 'Mostrar'}
                  </button>
                </div>
                {form.password_confirm.length > 0 && form.password !== form.password_confirm && (
                  <span style={{ ...errorStyle, color: '#b45309' }}>As senhas não conferem</span>
                )}
                {validationErrors.password_confirm && <span style={errorStyle} role="alert">{validationErrors.password_confirm}</span>}
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
              Já tem conta?{' '}
              <Link to="/login" style={{ color: '#1351B4', textDecoration: 'none', fontWeight: 500 }}>Fazer login</Link>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
