import { INTERFACE_SCHEMAS } from './interfaces';

export interface ValidationResult {
  valid: boolean;
  data: Record<string, unknown>;
  errors?: string[];
}

export function validateInterfaceData(
  tipo: string,
  dados: Record<string, unknown> | null | undefined,
): ValidationResult {
  const schema = (INTERFACE_SCHEMAS as any)[tipo];
  if (!schema) {
    // Sem schema definido: passthrough (graceful degradation)
    return { valid: true, data: dados || {} };
  }

  const result = schema.safeParse(dados);
  if (result.success) {
    return { valid: true, data: result.data as Record<string, unknown> };
  }

  // Log de falha (mantido para dev — sem stringify pesado em prod)
  console.warn(`[validate] ${tipo} falhou:`,
    result.error.issues.map((i: any) => `${i.path?.join('.') || '?'}: ${i.message}`));
  const errors = result.error.issues.map(
    (i: any) => `${i.path?.join('.') || '?'}: ${i.message}`,
  );
  return { valid: false, data: dados || {}, errors };
}
