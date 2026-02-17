import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().email('E-mail invalido'),
  password: z.string().min(1, 'Senha obrigatoria'),
});

const passwordSchema = z.string()
  .min(6, 'Senha deve ter no mínimo 6 caracteres')
  .regex(/[A-Z]/, 'Deve conter ao menos uma letra maiuscula')
  .regex(/[a-z]/, 'Deve conter ao menos uma letra minuscula')
  .regex(/[0-9]/, 'Deve conter ao menos um numero')
  .regex(/[^A-Za-z0-9]/, 'Deve conter ao menos um simbolo (!@#$%...)');

export const registerSchema = z.object({
  email: z.string().email('E-mail inválido'),
  password: passwordSchema,
  password_confirm: z.string(),
  nome_completo: z.string().min(3, 'Nome deve ter no mínimo 3 caracteres'),
  cargo: z.string().optional(),
  is_decipex: z.boolean().optional(),
  area_codigo: z.string().optional(),
  setor_trabalho: z.string().optional(),
}).refine(data => data.password === data.password_confirm, {
  message: 'As senhas não conferem',
  path: ['password_confirm'],
}).refine(data => {
  if (data.is_decipex && !data.area_codigo) return false;
  return true;
}, {
  message: 'Selecione a área da Decipex',
  path: ['area_codigo'],
}).refine(data => {
  if (data.is_decipex === false && !data.setor_trabalho?.trim()) return false;
  return true;
}, {
  message: 'Informe o setor de trabalho',
  path: ['setor_trabalho'],
});

export const passwordResetSchema = z.object({
  email: z.string().email('E-mail invalido'),
});

export const newPasswordSchema = z.object({
  password: passwordSchema,
  password_confirm: z.string(),
}).refine(data => data.password === data.password_confirm, {
  message: 'As senhas nao conferem',
  path: ['password_confirm'],
});

export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type PasswordResetFormData = z.infer<typeof passwordResetSchema>;
export type NewPasswordFormData = z.infer<typeof newPasswordSchema>;
