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
