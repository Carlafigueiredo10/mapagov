import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().email('E-mail invalido'),
  password: z.string().min(1, 'Senha obrigatoria'),
});

export const registerSchema = z.object({
  email: z.string().email('E-mail invalido'),
  password: z.string().min(8, 'Senha deve ter no minimo 8 caracteres'),
  password_confirm: z.string(),
  nome_completo: z.string().min(3, 'Nome deve ter no minimo 3 caracteres'),
  cargo: z.string().optional(),
  area_codigo: z.string().optional(),
}).refine(data => data.password === data.password_confirm, {
  message: 'As senhas nao conferem',
  path: ['password_confirm'],
});

export const passwordResetSchema = z.object({
  email: z.string().email('E-mail invalido'),
});

export const newPasswordSchema = z.object({
  password: z.string().min(8, 'Senha deve ter no minimo 8 caracteres'),
  password_confirm: z.string(),
}).refine(data => data.password === data.password_confirm, {
  message: 'As senhas nao conferem',
  path: ['password_confirm'],
});

export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type PasswordResetFormData = z.infer<typeof passwordResetSchema>;
export type NewPasswordFormData = z.infer<typeof newPasswordSchema>;
