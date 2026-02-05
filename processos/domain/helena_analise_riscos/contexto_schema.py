"""
Schema do Contexto Estruturado (Etapa 1)

Define a estrutura obrigatoria para contextualizar o objeto antes da analise.

Bloco A - Identificacao do Objeto
Bloco B - Contexto Operacional (7 perguntas + campos estruturados aditivos)

REGRA: Sem contexto minimo completo, o sistema NAO avanca para Etapa 2.

NOTA: Bloco B suporta campos estruturados ADITIVOS (v2):
- Campos de texto antigos continuam funcionando (retrocompat)
- Novos campos estruturados sao opcionais
- Chave ausente = nao respondeu (diferente de [] ou NAO_SEI)
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from processos.analise_riscos_enums import (
    BlocoBRecurso,
    BlocoBFrequencia,
    BlocoBSLA,
    BlocoBDependencia,
    BlocoBIncidentes,
)


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
# BLOCO B - CAMPOS ESTRUTURADOS ADITIVOS (v2)
# =============================================================================
# Estes campos sao OPCIONAIS e coexistem com os campos de texto acima.
# Chave ausente = nao respondeu
# Lista vazia [] = respondeu "nenhum/nao se aplica"
# NAO_SEI = usuario indicou incerteza (NUNCA deve virar NAO)

BLOCO_B_ESTRUTURADO_SCHEMA = {
    "recursos": {
        "label": "Tipos de recursos necessarios",
        "tipo": "checklist",
        "obrigatorio": False,
        "enum": "BlocoBRecurso",
        "opcoes": [e.value for e in BlocoBRecurso],
        "help_text": "Selecione os tipos de recursos. Lista vazia = nenhum/nao se aplica.",
    },
    "recursos_outros": {
        "label": "Outros recursos (especificar)",
        "tipo": "texto",
        "obrigatorio": False,
        "max_length": 500,
        "condicional": True,  # Mostrar se selecionou recursos
    },
    "atores_envolvidos_texto": {
        "label": "Areas e atores envolvidos",
        "tipo": "texto_longo",
        "obrigatorio": False,
        "max_length": 1000,
        "placeholder": "Area X, fornecedor Y...",
    },
    "frequencia": {
        "label": "Frequencia de execucao",
        "tipo": "selecao",
        "obrigatorio": False,
        "enum": "BlocoBFrequencia",
        "opcoes": [e.value for e in BlocoBFrequencia],
    },
    "sla": {
        "label": "Existem prazos legais ou SLAs?",
        "tipo": "radio",
        "obrigatorio": False,
        "enum": "BlocoBSLA",
        "opcoes": [e.value for e in BlocoBSLA],
        "help_text": "NAO_SEI e uma opcao valida - indica incerteza.",
    },
    "sla_detalhe": {
        "label": "Detalhes dos prazos/SLAs",
        "tipo": "texto",
        "obrigatorio": False,
        "max_length": 500,
        "condicional": {"sla": ["SIM"]},
    },
    "dependencia": {
        "label": "Tipo de dependencia externa",
        "tipo": "radio",
        "obrigatorio": False,
        "enum": "BlocoBDependencia",
        "opcoes": [e.value for e in BlocoBDependencia],
        "help_text": "NAO_SEI e uma opcao valida - indica incerteza.",
    },
    "dependencia_detalhe": {
        "label": "Detalhes das dependencias",
        "tipo": "texto",
        "obrigatorio": False,
        "max_length": 1000,
        "condicional": {"dependencia": ["SISTEMAS", "TERCEIROS", "AMBOS"]},
    },
    "incidentes": {
        "label": "Historico de incidentes/problemas",
        "tipo": "radio",
        "obrigatorio": False,
        "enum": "BlocoBIncidentes",
        "opcoes": [e.value for e in BlocoBIncidentes],
        "help_text": "NAO_SEI e uma opcao valida - indica incerteza.",
    },
    "incidentes_detalhe": {
        "label": "Detalhes dos incidentes",
        "tipo": "texto_longo",
        "obrigatorio": False,
        "max_length": 1000,
        "condicional": {"incidentes": ["SIM"]},
    },
    "consequencia_texto": {
        "label": "Consequencias se falhar",
        "tipo": "texto_longo",
        "obrigatorio": False,
        "max_length": 1000,
        "placeholder": "Se falhar, ...",
    },
}


# =============================================================================
# SCHEMA COMPLETO DO CONTEXTO
# =============================================================================

CONTEXTO_ESTRUTURADO_SCHEMA = {
    "bloco_a": BLOCO_A_SCHEMA,
    "bloco_b": BLOCO_B_SCHEMA,
    "bloco_b_estruturado": BLOCO_B_ESTRUTURADO_SCHEMA,  # Campos aditivos v2
}


def validar_contexto_minimo(contexto: Dict[str, Any], modo_entrada: str) -> Dict[str, List[str]]:
    """
    Valida se o contexto estruturado tem os campos minimos obrigatorios.

    REGRA v2: Aceita campo antigo OU campo novo para cada conceito.
    - recursos_necessarios (antigo) OU recursos (novo, aceita [])
    - frequencia_execucao (antigo) OU frequencia (novo)
    - prazos_slas (antigo) OU sla (novo, aceita NAO_SEI)
    - dependencias_externas (antigo) OU dependencia (novo, aceita NAO_SEI)
    - historico_problemas (antigo) OU incidentes (novo, aceita NAO_SEI)
    - impacto_se_falhar (antigo) OU consequencia_texto (novo)

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

    # ===========================================================================
    # Validar Bloco B com retrocompatibilidade (antigo OU novo)
    # ===========================================================================

    # Mapeamento: campo_antigo -> campo_novo_equivalente
    # Para cada par, aceita UM OU OUTRO preenchido
    campos_com_alternativa = {
        "recursos_necessarios": "recursos",        # texto antigo OU checklist novo
        "frequencia_execucao": "frequencia",       # selecao antiga OU selecao nova
        "prazos_slas": "sla",                      # texto antigo OU radio novo (SIM/NAO/NAO_SEI)
        "dependencias_externas": "dependencia",   # texto antigo OU radio novo
        "historico_problemas": "incidentes",      # texto antigo OU radio novo
        "impacto_se_falhar": "consequencia_texto", # texto antigo OU texto novo (mas vamos manter antigo obrigatorio)
    }

    for campo, config in BLOCO_B_SCHEMA.items():
        valor_antigo = bloco_b.get(campo, "")
        campo_novo = campos_com_alternativa.get(campo)
        valor_novo = bloco_b.get(campo_novo) if campo_novo else None

        # Verificar se tem valor antigo (texto ou selecao)
        tem_antigo = False
        if config["tipo"] == "selecao":
            valores_validos = [o["valor"] for o in config["opcoes"]]
            tem_antigo = valor_antigo in valores_validos
        else:
            tem_antigo = bool(valor_antigo.strip() if isinstance(valor_antigo, str) else valor_antigo)

        # Verificar se tem valor novo (checklist, radio, ou texto)
        tem_novo = False
        if campo_novo:
            if campo_novo == "recursos":
                # recursos: lista presente = respondeu (mesmo se [])
                tem_novo = "recursos" in bloco_b  # chave existe
            elif campo_novo in ("sla", "dependencia", "incidentes"):
                # radio: qualquer valor (SIM, NAO, NAO_SEI) = respondeu
                tem_novo = valor_novo is not None and valor_novo != ""
            elif campo_novo == "frequencia":
                # selecao: valor valido
                tem_novo = valor_novo is not None and valor_novo != ""
            elif campo_novo == "consequencia_texto":
                # texto: nao vazio
                tem_novo = bool(valor_novo.strip() if isinstance(valor_novo, str) else valor_novo)

        # Campo obrigatorio: exige antigo OU novo
        if config["obrigatorio"]:
            # Excecao: impacto_se_falhar e a "ancora" - SEMPRE exigido (campo principal)
            if campo == "impacto_se_falhar":
                if not tem_antigo:
                    erros[f"bloco_b.{campo}"] = [f"{config['label']} e obrigatorio"]
            elif not tem_antigo and not tem_novo:
                erros[f"bloco_b.{campo}"] = [f"{config['label']} e obrigatorio (ou preencha o campo estruturado equivalente)"]

        # Validar max_length do campo antigo (se preenchido)
        if tem_antigo and config.get("max_length"):
            if len(str(valor_antigo)) > config["max_length"]:
                erros[f"bloco_b.{campo}"] = [f"Maximo de {config['max_length']} caracteres"]

    return erros


def extrair_impacto_base(contexto: Dict[str, Any]) -> Optional[str]:
    """
    Extrai o impacto_base (Q7 - ancora) do contexto.

    Usado para:
    - Calibrar impacto na Etapa 3
    - Justificar decisoes de ACEITAR (especialmente em riscos ALTO/CRITICO)
    - Responder questionamentos de auditoria
    """
    bloco_b = contexto.get("bloco_b", {})
    # Prioriza campo estruturado novo, fallback para antigo
    return bloco_b.get("consequencia_texto") or bloco_b.get("impacto_se_falhar", "")


def validar_bloco_b_estruturado(bloco_b: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Valida campos estruturados do Bloco B (aditivos).

    IMPORTANTE:
    - Campos ausentes NAO sao erro (chave ausente = nao respondeu)
    - Lista vazia [] e valida (significa "nenhum/nao se aplica")
    - NAO_SEI e valor valido para sla, dependencia, incidentes

    Args:
        bloco_b: Dict com campos do Bloco B

    Returns:
        Dict com erros por campo. Vazio = valido.
    """
    erros: Dict[str, List[str]] = {}

    # Validar recursos (checklist)
    if "recursos" in bloco_b:
        recursos = bloco_b.get("recursos")
        if not isinstance(recursos, list):
            erros["recursos"] = ["Deve ser uma lista"]
        else:
            valores_validos = {e.value for e in BlocoBRecurso}
            invalidos = [r for r in recursos if r not in valores_validos]
            if invalidos:
                erros["recursos"] = [f"Valores invalidos: {invalidos}. Validos: {list(valores_validos)}"]

    # Validar frequencia (enum)
    if "frequencia" in bloco_b:
        freq = bloco_b.get("frequencia")
        valores_validos = {e.value for e in BlocoBFrequencia}
        if freq and freq not in valores_validos:
            erros["frequencia"] = [f"Valor invalido: {freq}. Validos: {list(valores_validos)}"]

    # Validar sla (enum com NAO_SEI)
    if "sla" in bloco_b:
        sla = bloco_b.get("sla")
        valores_validos = {e.value for e in BlocoBSLA}
        if sla and sla not in valores_validos:
            erros["sla"] = [f"Valor invalido: {sla}. Validos: {list(valores_validos)}"]

    # Validar dependencia (enum com NAO_SEI)
    if "dependencia" in bloco_b:
        dep = bloco_b.get("dependencia")
        valores_validos = {e.value for e in BlocoBDependencia}
        if dep and dep not in valores_validos:
            erros["dependencia"] = [f"Valor invalido: {dep}. Validos: {list(valores_validos)}"]

    # Validar incidentes (enum com NAO_SEI)
    if "incidentes" in bloco_b:
        inc = bloco_b.get("incidentes")
        valores_validos = {e.value for e in BlocoBIncidentes}
        if inc and inc not in valores_validos:
            erros["incidentes"] = [f"Valor invalido: {inc}. Validos: {list(valores_validos)}"]

    # Validar campos de texto (max_length)
    campos_texto = {
        "recursos_outros": 500,
        "atores_envolvidos_texto": 1000,
        "sla_detalhe": 500,
        "dependencia_detalhe": 1000,
        "incidentes_detalhe": 1000,
        "consequencia_texto": 1000,
    }
    for campo, max_len in campos_texto.items():
        if campo in bloco_b:
            valor = bloco_b.get(campo, "")
            if isinstance(valor, str) and len(valor) > max_len:
                erros[campo] = [f"Maximo de {max_len} caracteres"]

    return erros


def tem_campos_estruturados(bloco_b: Dict[str, Any]) -> bool:
    """
    Verifica se o Bloco B tem campos estruturados (v2).

    Usado para determinar se deve usar adapter ou campos antigos no export.
    """
    campos_v2 = {"recursos", "frequencia", "sla", "dependencia", "incidentes"}
    return any(campo in bloco_b for campo in campos_v2)
