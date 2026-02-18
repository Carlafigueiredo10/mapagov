import { useEffect, useState, useCallback } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import {
  listAllUsers, listPendingUsers, castVote, changeUserRole,
  createUser, editUser, deleteUser,
} from '../services/adminApi';
import type { AdminUser, PendingUser, VoteResult, CreateUserPayload, EditUserPayload } from '../services/adminApi';
import { useAuthStore } from '../store/authStore';
import { hasRole } from '../services/authApi';
import type { UserRole } from '../services/authApi';
import api from '../services/api';

const ROLE_LABELS: Record<string, string> = {
  operator: 'Operador',
  area_manager: 'Gestor de Area',
  general_manager: 'Gestor Geral',
  admin: 'Administrador',
};

const STATUS_LABELS: Record<string, string> = {
  pending: 'Pendente',
  approved: 'Aprovado',
  rejected: 'Rejeitado',
};

const STATUS_BADGE: Record<string, { bg: string; color: string }> = {
  pending: { bg: '#fff3e0', color: '#e65100' },
  approved: { bg: '#e8f5e9', color: '#2e7d32' },
  rejected: { bg: '#ffebee', color: '#b71c1c' },
};

const ROLE_BADGE: Record<string, { bg: string; color: string }> = {
  operator: { bg: '#e3f2fd', color: '#1565c0' },
  area_manager: { bg: '#f3e5f5', color: '#7b1fa2' },
  general_manager: { bg: '#e0f2f1', color: '#00695c' },
  admin: { bg: '#fce4ec', color: '#c62828' },
};

interface AreaOption { id: number; codigo: string; nome: string; }

export default function AdminUsersPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const currentUser = useAuthStore((s) => s.user);
  const isAdmin = hasRole(currentUser, 'admin') || currentUser?.is_superuser;

  // Filtros
  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [statusFilter, setStatusFilter] = useState(searchParams.get('status') || '');
  const [roleFilter, setRoleFilter] = useState(searchParams.get('role') || '');
  const [profileTypeFilter, setProfileTypeFilter] = useState('');

  // Dados
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error'>('success');

  // Votacao (pendentes)
  const [pendingUsers, setPendingUsers] = useState<PendingUser[]>([]);
  const [votingId, setVotingId] = useState<number | null>(null);

  // Role change
  const [areas, setAreas] = useState<AreaOption[]>([]);
  const [pendingRole, setPendingRole] = useState<{ profileId: number; role: UserRole } | null>(null);

  // Modais
  const [showCreateModal, setShowCreateModal] = useState(searchParams.get('action') === 'create');
  const [editingUser, setEditingUser] = useState<AdminUser | null>(null);
  const [deletingUser, setDeletingUser] = useState<AdminUser | null>(null);
  const [tempPassword, setTempPassword] = useState('');

  // Debounce search
  const [debouncedSearch, setDebouncedSearch] = useState(search);
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(timer);
  }, [search]);

  // Carregar areas
  useEffect(() => {
    if (!isAdmin) return;
    api.get('/areas/?all=1').then(res => {
      setAreas(res.data.map((a: any) => ({ id: a.id, codigo: a.codigo, nome: a.nome })));
    }).catch(() => {});
  }, [isAdmin]);

  // Carregar usuarios
  const loadUsers = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listAllUsers({
        search: debouncedSearch || undefined,
        status: statusFilter || undefined,
        role: roleFilter || undefined,
        profile_type: profileTypeFilter || undefined,
      });
      setUsers(data.results);
      setCount(data.count);

      // Carregar dados de votacao para pendentes
      if (!statusFilter || statusFilter === 'pending') {
        const pending = await listPendingUsers();
        setPendingUsers(pending);
      } else {
        setPendingUsers([]);
      }
    } catch {
      showMsg('Erro ao carregar usuarios.', 'error');
    } finally {
      setLoading(false);
    }
  }, [debouncedSearch, statusFilter, roleFilter, profileTypeFilter]);

  useEffect(() => { loadUsers(); }, [loadUsers]);

  const showMsg = (text: string, type: 'success' | 'error' = 'success') => {
    setMessage(text);
    setMessageType(type);
    setTimeout(() => setMessage(''), 5000);
  };

  // Votacao
  const handleVote = async (userId: number, vote: 'approve' | 'reject') => {
    setVotingId(userId);
    try {
      const result: VoteResult = await castVote(userId, vote);
      showMsg(result.result ? `${result.mensagem} Status: ${result.access_status}` : result.mensagem);
      loadUsers();
    } catch (err: any) {
      showMsg(err.response?.data?.erro || 'Erro ao registrar voto.', 'error');
    } finally {
      setVotingId(null);
    }
  };

  // Role change
  const handleRoleSelect = (profileId: number, newRole: UserRole) => {
    if (newRole === 'area_manager') {
      setPendingRole({ profileId, role: newRole });
    } else {
      handleRoleChange(profileId, newRole);
    }
  };

  const handleRoleChange = async (profileId: number, newRole: UserRole, areaId?: number) => {
    setPendingRole(null);
    const user = users.find(u => u.profile_id === profileId);
    if (!user) return;
    try {
      const result = await changeUserRole(user.user_id, newRole, areaId);
      showMsg(`Role alterado para ${result.role_display}${result.area ? ` (${result.area})` : ''}.`);
      loadUsers();
    } catch (err: any) {
      showMsg(err.response?.data?.erro || 'Erro ao alterar role.', 'error');
    }
  };

  // Quick status toggle
  const handleStatusToggle = async (user: AdminUser) => {
    const newStatus = user.access_status === 'approved' ? 'rejected' : 'approved';
    try {
      await editUser(user.profile_id, { access_status: newStatus });
      showMsg(`Status alterado para ${STATUS_LABELS[newStatus]}.`);
      loadUsers();
    } catch (err: any) {
      showMsg(err.response?.data?.erro || 'Erro ao alterar status.', 'error');
    }
  };

  // Delete
  const handleDelete = async (user: AdminUser) => {
    try {
      await deleteUser(user.profile_id);
      showMsg('Usuario desativado.');
      setDeletingUser(null);
      loadUsers();
    } catch (err: any) {
      showMsg(err.response?.data?.erro || 'Erro ao desativar usuario.', 'error');
    }
  };

  // Create
  const handleCreate = async (payload: CreateUserPayload) => {
    try {
      const result = await createUser(payload);
      if (result.temp_password) {
        setTempPassword(result.temp_password);
      }
      showMsg(`Usuario ${result.email} criado.`);
      if (!result.temp_password) setShowCreateModal(false);
      loadUsers();
    } catch (err: any) {
      const errors = err.response?.data?.errors;
      if (errors) {
        const msgs = Object.values(errors).flat().join(' ');
        showMsg(msgs, 'error');
      } else {
        showMsg('Erro ao criar usuario.', 'error');
      }
    }
  };

  // Edit
  const handleEdit = async (profileId: number, payload: EditUserPayload) => {
    try {
      await editUser(profileId, payload);
      showMsg('Usuario atualizado.');
      setEditingUser(null);
      loadUsers();
    } catch (err: any) {
      showMsg(err.response?.data?.erro || 'Erro ao atualizar.', 'error');
    }
  };

  // Dados de votacao para um usuario
  const getPendingData = (userId: number) => pendingUsers.find(p => p.id === userId);

  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: '32px 20px' }}>
      <Link to="/admin" style={{ color: '#1351B4', textDecoration: 'none', fontSize: 13, fontWeight: 500 }}>
        &#8592; Painel Administrativo
      </Link>
      <h1 style={{ color: '#1B4F72', marginBottom: 8, marginTop: 12 }}>Gerenciamento de Usuarios</h1>
      <p style={{ color: '#666', marginBottom: 24 }}>
        {count} usuario{count !== 1 ? 's' : ''} encontrado{count !== 1 ? 's' : ''}.
      </p>

      {/* Mensagem */}
      {message && (
        <div style={{
          background: messageType === 'error' ? '#ffebee' : '#e8f5e9',
          color: messageType === 'error' ? '#b71c1c' : '#2e7d32',
          padding: '10px 14px', borderRadius: 4, marginBottom: 16,
        }}>
          {message}
        </div>
      )}

      {/* Filtros */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 20, flexWrap: 'wrap', alignItems: 'center' }}>
        <input
          type="text"
          placeholder="Buscar por nome ou email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ padding: '8px 12px', border: '1px solid #ccc', borderRadius: 4, fontSize: 14, flex: '1 1 200px', minWidth: 180 }}
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{ padding: '8px 12px', border: '1px solid #ccc', borderRadius: 4, fontSize: 14 }}
        >
          <option value="">Todos os status</option>
          <option value="pending">Pendente</option>
          <option value="approved">Aprovado</option>
          <option value="rejected">Rejeitado</option>
        </select>
        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          style={{ padding: '8px 12px', border: '1px solid #ccc', borderRadius: 4, fontSize: 14 }}
        >
          <option value="">Todos os roles</option>
          <option value="operator">Operador</option>
          <option value="area_manager">Gestor de Area</option>
          <option value="general_manager">Gestor Geral</option>
          <option value="admin">Administrador</option>
        </select>
        <select
          value={profileTypeFilter}
          onChange={(e) => setProfileTypeFilter(e.target.value)}
          style={{ padding: '8px 12px', border: '1px solid #ccc', borderRadius: 4, fontSize: 14 }}
        >
          <option value="">Todos os tipos</option>
          <option value="mgi">MGI</option>
          <option value="externo">Externo</option>
        </select>
        <button
          onClick={() => setShowCreateModal(true)}
          style={{
            padding: '8px 20px', background: '#1351B4', color: '#fff',
            border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 500, fontSize: 14,
          }}
        >
          + Criar usuario
        </button>
      </div>

      {/* Lista */}
      {loading ? (
        <p style={{ color: '#666' }}>Carregando...</p>
      ) : users.length === 0 ? (
        <p style={{ color: '#666' }}>Nenhum usuario encontrado.</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {users.map(user => {
            const sb = STATUS_BADGE[user.access_status] || STATUS_BADGE.pending;
            const rb = ROLE_BADGE[user.role] || ROLE_BADGE.operator;
            const pending = getPendingData(user.profile_id);

            return (
              <div key={user.profile_id} style={{
                border: '1px solid #ddd', borderRadius: 8, padding: 16, background: '#fff',
                opacity: user.is_active ? 1 : 0.6,
              }}>
                {/* Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                      <h3 style={{ margin: 0, color: '#1B4F72', fontSize: 16 }}>
                        {user.nome_completo || user.username}
                      </h3>
                      <span style={{
                        fontSize: 11, padding: '2px 8px', borderRadius: 12,
                        background: sb.bg, color: sb.color, fontWeight: 600,
                      }}>
                        {STATUS_LABELS[user.access_status] || user.access_status}
                      </span>
                      <span style={{
                        fontSize: 11, padding: '2px 8px', borderRadius: 12,
                        background: rb.bg, color: rb.color, fontWeight: 600,
                      }}>
                        {ROLE_LABELS[user.role] || user.role}
                      </span>
                      {!user.is_active && (
                        <span style={{ fontSize: 11, padding: '2px 8px', borderRadius: 12, background: '#eee', color: '#666', fontWeight: 600 }}>
                          Inativo
                        </span>
                      )}
                    </div>
                    <p style={{ margin: '4px 0 0', color: '#666', fontSize: 13 }}>{user.email}</p>
                    {user.cargo && <p style={{ margin: '2px 0 0', color: '#888', fontSize: 12 }}>{user.cargo}</p>}
                    {user.area_nome && <p style={{ margin: '2px 0 0', color: '#888', fontSize: 12 }}>Area: {user.area_codigo} - {user.area_nome}</p>}
                  </div>
                  <div style={{ textAlign: 'right', fontSize: 12, color: '#999', whiteSpace: 'nowrap' }}>
                    <div>{new Date(user.created_at).toLocaleDateString('pt-BR')}</div>
                    <div>{user.email_verified ? 'Email verificado' : 'Email nao verificado'}</div>
                    <div>{user.profile_type === 'mgi' ? 'MGI' : 'Externo'}</div>
                  </div>
                </div>

                {/* Votos (so para pendentes) */}
                {pending && pending.votes.length > 0 && (
                  <div style={{ marginTop: 10, padding: '6px 10px', background: '#f5f5f5', borderRadius: 4 }}>
                    <p style={{ fontSize: 11, fontWeight: 600, color: '#666', margin: '0 0 4px' }}>Votos:</p>
                    {pending.votes.map((v, i) => (
                      <p key={i} style={{ fontSize: 11, color: v.vote === 'approve' ? '#2e7d32' : '#b71c1c', margin: '1px 0' }}>
                        {v.admin_email} — {v.vote === 'approve' ? 'Aprovado' : 'Rejeitado'}
                        {v.justificativa && ` (${v.justificativa})`}
                      </p>
                    ))}
                  </div>
                )}

                {/* Acoes */}
                <div style={{ marginTop: 12, display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                  {/* Votacao para pendentes */}
                  {user.access_status === 'pending' && (
                    <>
                      <button
                        onClick={() => handleVote(user.profile_id, 'approve')}
                        disabled={votingId === user.profile_id}
                        style={btnStyle('#2e7d32')}
                      >
                        Aprovar
                      </button>
                      <button
                        onClick={() => handleVote(user.profile_id, 'reject')}
                        disabled={votingId === user.profile_id}
                        style={btnStyle('#b71c1c')}
                      >
                        Rejeitar
                      </button>
                    </>
                  )}

                  {/* Toggle status (nao-pendentes) */}
                  {user.access_status !== 'pending' && (
                    <button onClick={() => handleStatusToggle(user)} style={btnOutlineStyle}>
                      {user.access_status === 'approved' ? 'Bloquear' : 'Aprovar'}
                    </button>
                  )}

                  {/* Editar */}
                  <button onClick={() => setEditingUser(user)} style={btnOutlineStyle}>
                    Editar
                  </button>

                  {/* Role dropdown */}
                  {isAdmin && (
                    <select
                      defaultValue=""
                      onChange={(e) => {
                        if (e.target.value) handleRoleSelect(user.profile_id, e.target.value as UserRole);
                        e.target.value = '';
                      }}
                      style={{ padding: '4px 8px', border: '1px solid #ccc', borderRadius: 4, fontSize: 12, cursor: 'pointer' }}
                    >
                      <option value="" disabled>Role...</option>
                      {Object.entries(ROLE_LABELS).map(([value, label]) => (
                        <option key={value} value={value}>{label}</option>
                      ))}
                    </select>
                  )}

                  {/* Seletor de area para area_manager */}
                  {pendingRole?.profileId === user.profile_id && (
                    <>
                      <select
                        defaultValue=""
                        onChange={(e) => {
                          if (e.target.value) handleRoleChange(user.profile_id, pendingRole.role, Number(e.target.value));
                        }}
                        style={{ padding: '4px 8px', border: '1px solid #1351B4', borderRadius: 4, fontSize: 12, cursor: 'pointer' }}
                      >
                        <option value="" disabled>Area...</option>
                        {areas.map(a => <option key={a.id} value={a.id}>{a.codigo}</option>)}
                      </select>
                      <button onClick={() => setPendingRole(null)} style={{ ...btnOutlineStyle, fontSize: 11, padding: '3px 6px' }}>
                        Cancelar
                      </button>
                    </>
                  )}

                  {/* Desativar */}
                  <button
                    onClick={() => setDeletingUser(user)}
                    style={{ ...btnOutlineStyle, color: '#b71c1c', borderColor: '#b71c1c', marginLeft: 'auto' }}
                  >
                    Desativar
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal Criar */}
      {showCreateModal && (
        <UserFormModal
          title="Criar usuario"
          areas={areas}
          onSubmit={(data) => handleCreate(data as CreateUserPayload)}
          onClose={() => { setShowCreateModal(false); setTempPassword(''); }}
          tempPassword={tempPassword}
        />
      )}

      {/* Modal Editar */}
      {editingUser && (
        <UserFormModal
          title="Editar usuario"
          areas={areas}
          initial={editingUser}
          onSubmit={(data) => handleEdit(editingUser.profile_id, data as EditUserPayload)}
          onClose={() => setEditingUser(null)}
        />
      )}

      {/* Confirmacao Desativar */}
      {deletingUser && (
        <div style={overlayStyle}>
          <div style={{ ...modalStyle, maxWidth: 420 }}>
            <h3 style={{ color: '#b71c1c', margin: '0 0 12px' }}>Desativar usuario</h3>
            <p style={{ color: '#333', fontSize: 14, marginBottom: 20 }}>
              Desativar <strong>{deletingUser.email}</strong>?<br />
              O usuario nao podera logar. Esta acao pode ser revertida.
            </p>
            <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
              <button onClick={() => setDeletingUser(null)} style={btnOutlineStyle}>Cancelar</button>
              <button onClick={() => handleDelete(deletingUser)} style={btnStyle('#b71c1c')}>Confirmar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Modal de formulario (criar / editar)
// ============================================================================

function UserFormModal({
  title, areas, initial, onSubmit, onClose, tempPassword,
}: {
  title: string;
  areas: AreaOption[];
  initial?: AdminUser;
  onSubmit: (data: Record<string, any>) => void;
  onClose: () => void;
  tempPassword?: string;
}) {
  const isEdit = !!initial;
  const [form, setForm] = useState({
    email: initial?.email || '',
    nome_completo: initial?.nome_completo || '',
    cargo: initial?.cargo || '',
    role: initial?.role || 'operator',
    profile_type: initial?.profile_type || 'externo',
    access_status: initial?.access_status || 'approved',
    area_id: initial?.area || '',
    setor_trabalho: initial?.setor_trabalho || '',
    is_decipex: initial?.is_decipex || false,
    password: '',
  });

  const handleChange = (field: string, value: any) => setForm(prev => ({ ...prev, [field]: value }));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload: Record<string, any> = {};

    if (!isEdit) {
      payload.email = form.email;
      payload.profile_type = form.profile_type;
      if (form.password) payload.password = form.password;
    }

    payload.nome_completo = form.nome_completo;
    payload.cargo = form.cargo;
    payload.role = form.role;
    payload.access_status = form.access_status;
    payload.setor_trabalho = form.setor_trabalho;
    payload.is_decipex = form.is_decipex;
    payload.area_id = form.area_id ? Number(form.area_id) : null;

    onSubmit(payload);
  };

  // Se tem temp_password, mostra tela de confirmacao
  if (tempPassword) {
    return (
      <div style={overlayStyle}>
        <div style={modalStyle}>
          <h3 style={{ color: '#1B4F72', margin: '0 0 12px' }}>Usuario criado</h3>
          <p style={{ fontSize: 14, color: '#333', marginBottom: 8 }}>
            Senha temporaria gerada (copie e envie ao usuario):
          </p>
          <div style={{
            background: '#f5f5f5', padding: '12px 16px', borderRadius: 4,
            fontFamily: 'monospace', fontSize: 16, fontWeight: 700, color: '#1B4F72',
            userSelect: 'all', marginBottom: 20,
          }}>
            {tempPassword}
          </div>
          <button onClick={onClose} style={btnStyle('#1351B4')}>Fechar</button>
        </div>
      </div>
    );
  }

  return (
    <div style={overlayStyle}>
      <div style={modalStyle}>
        <h3 style={{ color: '#1B4F72', margin: '0 0 16px' }}>{title}</h3>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {/* Email (so criar) */}
          {!isEdit && (
            <label style={labelStyle}>
              Email *
              <input
                type="email"
                required
                value={form.email}
                onChange={(e) => handleChange('email', e.target.value)}
                style={inputStyle}
              />
            </label>
          )}
          {isEdit && (
            <div style={{ fontSize: 13, color: '#666', marginBottom: 4 }}>
              Email: <strong>{initial?.email}</strong> (nao editavel)
            </div>
          )}

          <label style={labelStyle}>
            Nome completo *
            <input
              type="text"
              required
              value={form.nome_completo}
              onChange={(e) => handleChange('nome_completo', e.target.value)}
              style={inputStyle}
            />
          </label>

          <label style={labelStyle}>
            Cargo
            <input
              type="text"
              value={form.cargo}
              onChange={(e) => handleChange('cargo', e.target.value)}
              style={inputStyle}
            />
          </label>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <label style={labelStyle}>
              Role
              <select value={form.role} onChange={(e) => handleChange('role', e.target.value)} style={inputStyle}>
                {Object.entries(ROLE_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
              </select>
            </label>

            <label style={labelStyle}>
              Status
              <select value={form.access_status} onChange={(e) => handleChange('access_status', e.target.value)} style={inputStyle}>
                {Object.entries(STATUS_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
              </select>
            </label>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            {!isEdit && (
              <label style={labelStyle}>
                Tipo
                <select value={form.profile_type} onChange={(e) => handleChange('profile_type', e.target.value)} style={inputStyle}>
                  <option value="externo">Externo</option>
                  <option value="mgi">MGI</option>
                </select>
              </label>
            )}

            <label style={labelStyle}>
              Area
              <select value={form.area_id} onChange={(e) => handleChange('area_id', e.target.value)} style={inputStyle}>
                <option value="">Nenhuma</option>
                {areas.map(a => <option key={a.id} value={a.id}>{a.codigo} - {a.nome}</option>)}
              </select>
            </label>
          </div>

          <label style={labelStyle}>
            Setor de trabalho
            <input
              type="text"
              value={form.setor_trabalho}
              onChange={(e) => handleChange('setor_trabalho', e.target.value)}
              style={inputStyle}
            />
          </label>

          <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: '#333' }}>
            <input
              type="checkbox"
              checked={form.is_decipex}
              onChange={(e) => handleChange('is_decipex', e.target.checked)}
            />
            Vinculado a Decipex
          </label>

          {/* Senha (so criar) */}
          {!isEdit && (
            <label style={labelStyle}>
              Senha (deixe vazio para gerar automaticamente)
              <input
                type="text"
                value={form.password}
                onChange={(e) => handleChange('password', e.target.value)}
                style={inputStyle}
                placeholder="Gerada automaticamente se vazio"
              />
            </label>
          )}

          <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end', marginTop: 8 }}>
            <button type="button" onClick={onClose} style={btnOutlineStyle}>Cancelar</button>
            <button type="submit" style={btnStyle('#1351B4')}>
              {isEdit ? 'Salvar' : 'Criar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ============================================================================
// Estilos compartilhados (inline)
// ============================================================================

const overlayStyle: React.CSSProperties = {
  position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)',
  display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000,
};

const modalStyle: React.CSSProperties = {
  background: '#fff', borderRadius: 8, padding: 32, width: 520,
  maxHeight: '85vh', overflowY: 'auto', boxShadow: '0 4px 24px rgba(0,0,0,0.2)',
};

const labelStyle: React.CSSProperties = {
  display: 'flex', flexDirection: 'column', gap: 4, fontSize: 13, color: '#333', fontWeight: 500,
};

const inputStyle: React.CSSProperties = {
  padding: '8px 12px', border: '1px solid #ccc', borderRadius: 4, fontSize: 14, fontWeight: 400,
};

const btnStyle = (bg: string): React.CSSProperties => ({
  padding: '6px 16px', background: bg, color: '#fff',
  border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 500, fontSize: 13,
});

const btnOutlineStyle: React.CSSProperties = {
  padding: '6px 16px', background: 'transparent', color: '#1351B4',
  border: '1px solid #ccc', borderRadius: 4, cursor: 'pointer', fontWeight: 500, fontSize: 13,
};
