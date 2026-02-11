import api from './api';

export interface UserInfo {
  email: string;
  username: string;
  is_superuser: boolean;
  profile_type: 'mgi' | 'externo';
  email_verified: boolean;
  access_status: 'pending' | 'approved' | 'rejected';
  nome_completo: string;
  cargo: string;
  orgao: number | null;
  area: number | null;
  created_at: string;
  can_access: boolean;
  is_approver: boolean;
}

export interface RegisterData {
  email: string;
  password: string;
  password_confirm: string;
  nome_completo: string;
  cargo?: string;
  area_codigo?: string;
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
