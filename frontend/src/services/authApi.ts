import api from './api';

export type UserRole = 'operator' | 'area_manager' | 'general_manager' | 'admin';

export interface UserInfo {
  email: string;
  username: string;
  is_superuser: boolean;
  profile_type: 'mgi' | 'externo';
  email_verified: boolean;
  access_status: 'pending' | 'approved' | 'rejected';
  role: UserRole;
  nome_completo: string;
  cargo: string;
  orgao: number | null;
  area: number | null;
  created_at: string;
  can_access: boolean;
  is_approver: boolean;
}

const ROLE_HIERARCHY: UserRole[] = ['operator', 'area_manager', 'general_manager', 'admin'];

/** Verifica se o usuario tem role >= minRole. */
export function hasRole(user: UserInfo | null, minRole: UserRole): boolean {
  if (!user) return false;
  return ROLE_HIERARCHY.indexOf(user.role) >= ROLE_HIERARCHY.indexOf(minRole);
}

export interface RegisterData {
  email: string;
  password: string;
  password_confirm: string;
  nome_completo: string;
  cargo?: string;
  is_decipex?: boolean;
  area_codigo?: string;
  setor_trabalho?: string;
}

export interface PublicArea {
  codigo: string;
  nome_curto: string;
}

/** Busca CSRF token (deve ser chamado antes do primeiro POST) */
export async function fetchCsrf() {
  return api.get('/auth/csrf/');
}

export async function loginApi(email: string, password: string) {
  const res = await api.post('/auth/login/', { email, password });
  return res.data;
}

export async function registerApi(data: RegisterData) {
  const res = await api.post('/auth/register/', data);
  return res.data;
}

export async function logoutApi() {
  const res = await api.post('/auth/logout/');
  return res.data;
}

export async function getMeApi(): Promise<UserInfo> {
  const res = await api.get('/auth/me/');
  return res.data;
}

export async function verifyEmailApi(uid: string, token: string) {
  const res = await api.get(`/auth/verify-email/${uid}/${token}/`);
  return res.data;
}

export async function requestPasswordResetApi(email: string) {
  const res = await api.post('/auth/password-reset/', { email });
  return res.data;
}

export async function confirmPasswordResetApi(uid: string, token: string, password: string) {
  const res = await api.post('/auth/password-reset-confirm/', { uid, token, password });
  return res.data;
}

export async function fetchPublicAreas(): Promise<PublicArea[]> {
  const res = await api.get('/auth/areas/');
  return res.data;
}
