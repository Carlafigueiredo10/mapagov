import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getAdminStats } from '../services/adminApi';
import type { AdminStats } from '../services/adminApi';

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getAdminStats()
      .then(setStats)
      .catch(() => setError('Erro ao carregar estatisticas.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div style={{ maxWidth: 900, margin: '0 auto', padding: '32px 20px' }}>
        <p style={{ color: '#666' }}>Carregando...</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '32px 20px' }}>
      <Link to="/" style={{ color: '#1351B4', textDecoration: 'none', fontSize: 13, fontWeight: 500 }}>
        &#8592; Pagina principal
      </Link>
      <h1 style={{ color: '#1B4F72', marginBottom: 8, marginTop: 12 }}>Painel Administrativo</h1>
      <p style={{ color: '#666', marginBottom: 32 }}>Visao geral do sistema.</p>

      {error && (
        <div style={{ background: '#ffebee', color: '#b71c1c', padding: '10px 14px', borderRadius: 4, marginBottom: 16 }}>
          {error}
        </div>
      )}

      {stats && (
        <>
          {/* Stat Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 32 }}>
            <StatCard
              label="Total de usuarios"
              value={stats.total_users}
              color="#1B4F72"
              linkTo="/admin/usuarios"
            />
            <StatCard
              label="Pendentes"
              value={stats.pending_users}
              color="#e65100"
              accent="#f9a825"
              linkTo="/admin/usuarios?status=pending"
            />
            <StatCard
              label="Aprovados"
              value={stats.approved_users}
              color="#2e7d32"
              linkTo="/admin/usuarios?status=approved"
            />
            <StatCard
              label="Rejeitados"
              value={stats.rejected_users}
              color="#b71c1c"
              linkTo="/admin/usuarios?status=rejected"
            />
          </div>

          {/* Detalhes por tipo e role */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 32 }}>
            <div style={{ border: '1px solid #ddd', borderRadius: 8, padding: 20, background: '#fff' }}>
              <h3 style={{ color: '#1B4F72', margin: '0 0 12px 0', fontSize: 16 }}>Por tipo</h3>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 14, color: '#333' }}>
                <span>MGI (gestao.gov.br)</span>
                <span style={{ fontWeight: 600 }}>{stats.by_profile_type.mgi || 0}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 14, color: '#333', marginTop: 8 }}>
                <span>Externo</span>
                <span style={{ fontWeight: 600 }}>{stats.by_profile_type.externo || 0}</span>
              </div>
            </div>

            <div style={{ border: '1px solid #ddd', borderRadius: 8, padding: 20, background: '#fff' }}>
              <h3 style={{ color: '#1B4F72', margin: '0 0 12px 0', fontSize: 16 }}>Por role</h3>
              {[
                { key: 'operator', label: 'Operador' },
                { key: 'area_manager', label: 'Gestor de Area' },
                { key: 'general_manager', label: 'Gestor Geral' },
                { key: 'admin', label: 'Administrador' },
              ].map(({ key, label }) => (
                <div key={key} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 14, color: '#333', marginTop: key === 'operator' ? 0 : 8 }}>
                  <span>{label}</span>
                  <span style={{ fontWeight: 600 }}>{stats.by_role[key] || 0}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Acoes rapidas */}
          <div style={{ display: 'flex', gap: 12 }}>
            <Link
              to="/admin/usuarios"
              style={{
                padding: '10px 24px', background: '#1351B4', color: '#fff',
                borderRadius: 4, textDecoration: 'none', fontWeight: 500, fontSize: 14,
              }}
            >
              Gerenciar usuarios
            </Link>
            <Link
              to="/admin/usuarios?action=create"
              style={{
                padding: '10px 24px', background: '#fff', color: '#1351B4',
                border: '1px solid #1351B4', borderRadius: 4, textDecoration: 'none',
                fontWeight: 500, fontSize: 14,
              }}
            >
              Novo usuario
            </Link>
          </div>
        </>
      )}
    </div>
  );
}

function StatCard({
  label, value, color, accent, linkTo,
}: {
  label: string;
  value: number;
  color: string;
  accent?: string;
  linkTo: string;
}) {
  return (
    <Link
      to={linkTo}
      style={{
        border: '1px solid #ddd',
        borderLeft: accent ? `4px solid ${accent}` : '1px solid #ddd',
        borderRadius: 8,
        padding: 20,
        background: '#fff',
        textDecoration: 'none',
        display: 'block',
      }}
    >
      <div style={{ fontSize: 32, fontWeight: 700, color }}>{value}</div>
      <div style={{ fontSize: 14, color: '#666', marginTop: 4 }}>{label}</div>
    </Link>
  );
}
