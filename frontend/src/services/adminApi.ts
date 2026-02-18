import api from './api';

export interface PendingUser {
  id: number;
  email: string;
  username: string;
  profile_type: string;
  access_status: string;
  email_verified: boolean;
  nome_completo: string;
  cargo: string;
  created_at: string;
  approvals_count: number;
  rejections_count: number;
  votes: Array<{
    admin_email: string | null;
    vote: string;
    justificativa: string;
    voted_at: string;
  }>;
}

export interface VoteResult {
  mensagem: string;
  access_status: string;
  result: 'approved' | 'rejected' | null;
}

export async function listPendingUsers(filters?: { domain?: string; area?: string }) {
  const params = new URLSearchParams();
  if (filters?.domain) params.set('domain', filters.domain);
  if (filters?.area) params.set('area', filters.area);
  const res = await api.get(`/admin/pending-users/?${params.toString()}`);
  return res.data as PendingUser[];
}

export async function castVote(userId: number, vote: 'approve' | 'reject', justificativa?: string) {
  const res = await api.post(`/admin/users/${userId}/vote/`, { vote, justificativa: justificativa || '' });
  return res.data as VoteResult;
}

export async function getUserDetail(userId: number) {
  const res = await api.get(`/admin/users/${userId}/`);
  return res.data;
}

export async function getAuditLog() {
  const res = await api.get('/admin/audit-log/');
  return res.data;
}

export async function changeUserRole(userId: number, role: string, areaId?: number) {
  const payload: { role: string; area_id?: number } = { role };
  if (areaId !== undefined) payload.area_id = areaId;
  const res = await api.patch(`/admin/users/${userId}/role/`, payload);
  return res.data as { success: boolean; role: string; role_display: string; area: string | null };
}

// ============================================================================
// ADMIN CRUD — Lista completa, criar, editar, desativar, stats
// ============================================================================

export interface AdminUser {
  profile_id: number;
  user_id: number;
  email: string;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
  profile_type: 'mgi' | 'externo';
  access_status: 'pending' | 'approved' | 'rejected';
  email_verified: boolean;
  role: string;
  nome_completo: string;
  cargo: string;
  setor_trabalho: string;
  is_decipex: boolean;
  orgao: number | null;
  orgao_nome: string | null;
  area: number | null;
  area_codigo: string | null;
  area_nome: string | null;
  created_at: string;
  updated_at: string;
}

export interface AdminUserListResponse {
  count: number;
  limit: number;
  offset: number;
  results: AdminUser[];
}

export interface AdminStats {
  total_users: number;
  pending_users: number;
  approved_users: number;
  rejected_users: number;
  by_role: Record<string, number>;
  by_profile_type: Record<string, number>;
}

export interface CreateUserPayload {
  email: string;
  nome_completo: string;
  cargo?: string;
  role?: string;
  profile_type?: string;
  access_status?: string;
  password?: string;
  area_id?: number | null;
  setor_trabalho?: string;
  is_decipex?: boolean;
}

export interface EditUserPayload {
  nome_completo?: string;
  cargo?: string;
  role?: string;
  access_status?: string;
  email_verified?: boolean;
  area_id?: number | null;
  is_active?: boolean;
  setor_trabalho?: string;
  is_decipex?: boolean;
}

export async function listAllUsers(filters?: {
  search?: string;
  status?: string;
  role?: string;
  profile_type?: string;
  limit?: number;
  offset?: number;
}): Promise<AdminUserListResponse> {
  const params = new URLSearchParams();
  if (filters?.search) params.set('search', filters.search);
  if (filters?.status) params.set('status', filters.status);
  if (filters?.role) params.set('role', filters.role);
  if (filters?.profile_type) params.set('profile_type', filters.profile_type);
  if (filters?.limit) params.set('limit', String(filters.limit));
  if (filters?.offset) params.set('offset', String(filters.offset));
  const res = await api.get(`/admin/users/?${params.toString()}`);
  return res.data;
}

export async function getAdminStats(): Promise<AdminStats> {
  const res = await api.get('/admin/stats/');
  return res.data;
}

export async function createUser(payload: CreateUserPayload) {
  const res = await api.post('/admin/users/create/', payload);
  return res.data as { profile_id: number; email: string; mensagem: string; temp_password?: string };
}

export async function editUser(profileId: number, payload: EditUserPayload) {
  const res = await api.patch(`/admin/users/${profileId}/edit/`, payload);
  return res.data as { success: boolean; mensagem: string };
}

export async function deleteUser(profileId: number) {
  const res = await api.delete(`/admin/users/${profileId}/delete/`);
  return res.data as { success: boolean; mensagem: string };
}
