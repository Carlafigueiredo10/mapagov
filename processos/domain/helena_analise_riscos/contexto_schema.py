"""
Schema do Contexto Estruturado (Etapa 1)

Define a estrutura obrigatoria para contextualizar o objeto antes da analise.

Bloco A - Identificacao do Objeto
Bloco B - Contexto Operacional (7 perguntas)

REGRA: Sem contexto minimo completo, o sistema NAO avanca para Etapa 2.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


# =============================================================================
# BLOCO A - IDENTIFICACAO DO OBJETO
# =============================================================================

BLOCO_A_SCHEMA = {
    "nome_objeto": {
        "label": "Nome do objeto analisado",
        "tipo": "texto",
        "obrigatorio": True,
        "max_length": 255,
        "placeholder": "Ex: Processo de contratacao de TI",
    },
    "objetivo_finalidade": {
        "label": "Objetivo/Finalidade",
        "tipo": "texto_longo",
        "obrigatorio": True,
        "max_length": 1000,
        "placeholder": "Para que serve este projeto/processo?",
    },
    "area_responsavel": {
        "label": "Area responsavel",
        "tipo": "texto",
        "obrigatorio": True,
        "max_length": 100,
        "placeholder": "Ex: CGTI, DECIPEX, etc.",
    },
    "descricao_escopo": {
        "label": "Descricao do escopo",
        "tipo": "texto_longo",
        "obrigatorio": False,  # Obrigatorio se modo_entrada != PDF
        "max_length": 2000,
        "placeholder": "Descreva brevemente o que faz este processo/projeto",
        "help_text": "Obrigatorio quando nao houver PDF anexado",
    },
}


# =============================================================================
# BLOCO B - CONTEXTO OPERACIONAL (7 perguntas)
# =============================================================================

BLOCO_B_SCHEMA = {
    "recursos_necessarios": {
        "label": "Quais recursos sao necessarios para executar este processo/projeto?",
        "tipo": "texto_longo",
        "obrigatorio": True,
        "max_length": 1000,
        "placeholder": "Pessoas, sistemas, orcamento, equipamentos...",
        "help_text": "Revela dependencias criticas e riscos operacionais/tecnologicos",
    },
    "areas_atores_envolvidos": {
        "label": "Quais areas, unidades ou atores estao diretamente envolvidos?",
        "tipo": "texto_longo",
        "obrigatorio": True,
        "max_length": 1000,
        "placeholder": "Liste as areas e papeis envolvidos",
        "help_text": "Identifica responsabilidades difusas e riscos de governanca",
    },
    "frequencia_execucao": {
        "label": "Com que frequencia isso ocorre ou sera executado?",
        "tipo": "selecao",
        "obrigatorio": True,
        "opcoes": [
            {"valor": "CONTINUO", "label": "Continuo (diario/semanal)"},
            {"valor": "PERIODICO", "label": "Periodico (mensal/trimestral)"},
            {"valor": "PONTUAL", "label": "Pontual (evento unico)"},
            {"valor": "SOB_DEMANDA", "label": "Sob demanda"},
        ],
        "help_text": "Risco = impacto x exposicao. Frequencia aumenta exposicao.",
    },
    "prazos_slas": {
        "label": "Existem prazos legais, normativos ou SLAs associados?",
        "tipo": "texto_longo",
        "obrigatorio": True,
        "max_length": 500,
        "placeholder": "Descreva prazos e obrigacoes, ou 'Nao ha'",
        "help_text": "Risco de descumprimento normativo e reputacional",
    },
    "dependencias_externas": {
        "label": "Ha dependencia de sistemas externos, terceiros ou outros orgaos?",
        "tipo": "texto_longo",
        "obrigatorio": True,
        "max_length": 1000,
        "placeholder": "Liste dependencias ou 'Nao ha'",
        "help_text": "Risco fora do controle direto da gestao",
    },
    "historico_problemas": {
        "label": "Ja houve problemas, incidentes, retrabalho ou questionamentos anteriores?",
        "tipo": "texto_longo",
        "obrigatorio": True,
        "max_length": 1000,
        "placeholder": "Descreva historico ou 'Nao ha registro'",
        "help_text": "Historico e evidencia empirica, nao opiniao",
    },
    "impacto_se_falhar": {
        "label": "O que acontece se isso nao funcionar como esperado?",
        "tipo": "texto_longo",
        "obrigatorio": True,
        "max_length": 1000,
        "placeholder": "Descreva as consequencias de falha",
        "help_text": "ANCORA: calibra impacto e justifica decisoes futuras",
        "ancora": True,  # Marcador especial - usado como impacto_base
    },
}


# =============================================================================
# SCHEMA COMPLETO DO CONTEXTO
# =============================================================================

CONTEXTO_ESTRUTURADO_SCHEMA = {
    "bloco_a": BLOCO_A_SCHEMA,
    "bloco_b": BLOCO_B_SCHEMA,
}


def validar_contexto_minimo(contexto: Dict[str, Any], modo_entrada: str) -> Dict[str, List[str]]:
    """
    Valida se o contexto estruturado tem os campos minimos obrigatorios.

    Args:
        contexto: Dict com bloco_a e bloco_b
        modo_entrada: QUESTIONARIO, PDF ou ID

    Returns:
        Dict com erros por campo. Vazio = valido.
    """
    erros: Dict[str, List[str]] = {}

    bloco_a = contexto.get("bloco_a", {})
    bloco_b = contexto.get("bloco_b", {})

    # Validar Bloco A
    for campo, config in BLOCO_A_SCHEMA.items():
        valor = bloco_a.get(campo, "").strip() if isinstance(bloco_a.get(campo), str) else bloco_a.get(campo)

        # Descricao escopo e obrigatoria se nao for PDF
        obrigatorio = config["obrigatorio"]
        if campo == "descricao_escopo" and modo_entrada != "PDF":
            obrigatorio = True

        if obrigatorio and not valor:
            erros[f"bloco_a.{campo}"] = [f"{config['label']} e obrigatorio"]

        if valor and config.get("max_length") and len(str(valor)) > config["max_length"]:
            erros[f"bloco_a.{campo}"] = [f"Maximo de {config['max_length']} caracteres"]

    # Validar Bloco B
    for campo, config in BLOCO_B_SCHEMA.items():
        valor = bloco_b.get(campo, "")

        if config["tipo"] == "selecao":
            valores_validos = [o["valor"] for o in config["opcoes"]]
            if config["obrigatorio"] and valor not in valores_validos:
                erros[f"bloco_b.{campo}"] = [f"Selecione uma opcao valida"]
        else:
            valor_str = valor.strip() if isinstance(valor, str) else valor
            if config["obrigatorio"] and not valor_str:
                erros[f"bloco_b.{campo}"] = [f"{config['label']} e obrigatorio"]

            if valor_str and config.get("max_length") and len(str(valor_str)) > config["max_length"]:
                erros[f"bloco_b.{campo}"] = [f"Maximo de {config['max_length']} caracteres"]

    return erros


def extrair_impacto_base(contexto: Dict[str, Any]) -> Optional[str]:
    """
    Extrai o impacto_base (Q7 - ancora) do contexto.

    Usado para:
    - Calibrar impacto na Etapa 3
    - Justificar decisoes de ACEITAR ou RESGUARDAR
    - Responder questionamentos de auditoria
    """
    bloco_b = contexto.get("bloco_b", {})
    return bloco_b.get("impacto_se_falhar", "")
