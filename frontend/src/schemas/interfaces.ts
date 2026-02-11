import { z } from 'zod';

// Schemas Zod para as interfaces dinâmicas mais frequentes.
// Interfaces sem schema definido passam sem validação (graceful degradation).

// Zod 4 — schema mínimo, sem transforms/union/passthrough
export const AreasSchema = z.object({
  opcoes_areas: z.record(z.string(), z.object({
    codigo: z.string(),
    nome: z.string(),
  })),
});

export const SubareasSchema = z.object({
  area_pai: z.object({ codigo: z.string(), nome: z.string() }),
  subareas: z.array(z.object({
    codigo: z.string(),
    nome: z.string(),
    nome_completo: z.string().optional(),
    prefixo: z.string().optional(),
  })),
});

export const ConfirmacaoDuplaSchema = z.object({
  botao_confirmar: z.string().optional(),
  botao_editar: z.string().optional(),
});

export const FinalSchema = z.object({
  pdfUrl: z.string().optional(),
  arquivo: z.string().optional(),
});

export const SistemasSchema = z.object({
  sistemas: z.array(z.string()).optional(),
  sistemas_disponiveis: z.array(z.string()).optional(),
});

export const TextoLivreSchema = z.object({
  campo: z.string().optional(),
  placeholder: z.string().optional(),
  label: z.string().optional(),
});

export const DropdownSchema = z.object({
  opcoes: z.array(z.object({
    codigo: z.string().optional(),
    nome: z.string(),
    valor: z.string().optional(),
  }).passthrough()).optional(),
  opcoes_disponiveis: z.record(z.unknown()).optional(),
}).passthrough();

export const BadgeCompromissoSchema = z.object({
  titulo: z.string().optional(),
  mensagem: z.string().optional(),
});

export const EtapaFormSchema = z.object({
  etapa_numero: z.number().optional(),
  etapa_atual: z.number().optional(),
}).passthrough();

export const RevisaoSchema = z.object({
  campos: z.record(z.unknown()).optional(),
  dados_pop: z.record(z.unknown()).optional(),
}).passthrough();

// Registry: tipo_interface → schema
export const INTERFACE_SCHEMAS = {
  areas: AreasSchema,
  subareas: SubareasSchema,
  confirmacao_dupla: ConfirmacaoDuplaSchema,
  confirmacao_explicacao: ConfirmacaoDuplaSchema,
  final: FinalSchema,
  sistemas: SistemasSchema,
  texto_livre: TextoLivreSchema,
  dropdown_macro: DropdownSchema,
  dropdown_processo: DropdownSchema,
  dropdown_subprocesso: DropdownSchema,
  dropdown_atividade: DropdownSchema,
  dropdown_processo_com_texto_livre: DropdownSchema,
  dropdown_subprocesso_com_texto_livre: DropdownSchema,
  dropdown_atividade_com_texto_livre: DropdownSchema,
  badge_compromisso: BadgeCompromissoSchema,
  etapa_form: EtapaFormSchema,
  revisao: RevisaoSchema,
} as const;
