"""
Constantes para Analise de Riscos

IDs estaveis, textos podem evoluir.
"""

# Questionario de contexto - IDs estaveis
QUESTIONARIO_CONTEXTO = {
    "Q_CONTEXTO_01": {
        "id": "Q_CONTEXTO_01",
        "texto": "[PLACEHOLDER] Qual area DECIPEX responsavel?",
        "tipo": "selecao",
        "obrigatorio": True,
    },
    "Q_CONTEXTO_02": {
        "id": "Q_CONTEXTO_02",
        "texto": "[PLACEHOLDER] Qual macroprocesso sera analisado?",
        "tipo": "selecao",
        "obrigatorio": True,
    },
    "Q_CONTEXTO_03": {
        "id": "Q_CONTEXTO_03",
        "texto": "[PLACEHOLDER] Existe historico de incidentes nesse processo?",
        "tipo": "sim_nao",
        "obrigatorio": True,
    },
    "Q_CONTEXTO_04": {
        "id": "Q_CONTEXTO_04",
        "texto": "[PLACEHOLDER] Qual o nivel de criticidade esperado?",
        "tipo": "selecao",
        "obrigatorio": False,
    },
    "Q_CONTEXTO_05": {
        "id": "Q_CONTEXTO_05",
        "texto": "[PLACEHOLDER] Ha grupos vulneraveis impactados pelo processo?",
        "tipo": "sim_nao",
        "obrigatorio": True,
    },
}

# Areas DECIPEX - IDs estaveis
AREAS_DECIPEX = {
    "CGBEN": "Coordenacao-Geral de Beneficios",
    "CGRIS": "Coordenacao-Geral de Riscos",
    "CGPAG": "Coordenacao-Geral de Pagamentos",
    "CGPES": "Coordenacao-Geral de Pessoal",
    "CGLOG": "Coordenacao-Geral de Logistica",
}

# Descricoes das categorias de risco
DESCRICOES_CATEGORIA = {
    "OPERACIONAL": "Falhas em processos ou recursos",
    "FINANCEIRO": "Perdas orcamentarias",
    "LEGAL": "Descumprimento normativo",
    "REPUTACIONAL": "Dano a imagem institucional",
    "TECNOLOGICO": "Falhas em sistemas/TI",
    "IMPACTO_DESIGUAL": "Impacto desigual/excludente por ausencia ou insuficiencia de analise distributiva",
}

# Descricoes das estrategias
DESCRICOES_ESTRATEGIA = {
    "MITIGAR": "Reduzir probabilidade ou impacto",
    "EVITAR": "Eliminar a causa do risco",
    "COMPARTILHAR": "Compartilhar/transferir parte do risco (ex.: contrato, cooperacao, seguro)",
    "ACEITAR": "Reconhecer sem acao",
    "RESGUARDAR": "Documentar para compliance",
}
