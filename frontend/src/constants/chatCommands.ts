/**
 * Constantes de comando para comunicação frontend-backend
 *
 * Tokens determinísticos que não conflitam com texto do usuário.
 * O backend reconhece esses tokens e trata como comandos especiais.
 */
export const CHAT_CMD = {
  CONFIRMAR_DUPLA: "__CONFIRMAR_DUPLA__",
  EDITAR_DUPLA: "__EDITAR_DUPLA__",
  CONFIRMAR: "__CONFIRMAR__",
  CANCELAR: "__CANCELAR__",
  SEGUIR: "__SEGUIR__",
  PULAR: "__PULAR__",
  ENTRAR_DUVIDAS: "__entrar_duvidas__",
  SAIR_DUVIDAS: "__sair_duvidas__",
} as const;

export type ChatCommand = typeof CHAT_CMD[keyof typeof CHAT_CMD];
