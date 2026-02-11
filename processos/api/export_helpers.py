"""
Export Helpers - Analise de Riscos

Funcoes auxiliares para export de PDF/DOCX baseado em snapshot.

Contrato: schema_version = "1.0"

Funcoes principais:
- get_snapshot_para_export(analise, user) -> AnaliseSnapshot
- criar_snapshot(analise, user, motivo) -> AnaliseSnapshot
- build_snapshot_payload(analise) -> dict
- should_render_question(qid, bloco, respostas) -> bool
- labelize(value, enum_map) -> str
- format_value(value, required) -> str | None
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from django.contrib.auth import get_user_model
from django.conf import settings

from processos.models_analise_riscos import (
    AnaliseRiscos,
    AnaliseSnapshot,
    MotivoSnapshot,
)
from processos.domain.helena_analise_riscos.blocos_schema import BLOCOS_SCHEMA


# =============================================================================
# CONSTANTES
# =============================================================================

SCHEMA_VERSION = "1.0"
VERSAO_SISTEMA = "Helena v2.1"

# Nota institucional para documentos exportados
NOTA_CONDICIONAIS = (
    "Campos condicionais podem nao aparecer quando nao se aplicam "
    "ao contexto da analise."
)


# =============================================================================
# DEPENDENCIAS CONDICIONAIS DOS 6 BLOCOS
# =============================================================================
# Mapeamento: {bloco: {pergunta: {pergunta_pai: [valores_que_ativam]}}}
# Se a pergunta_pai NAO tiver um dos valores listados, a pergunta filha NAO renderiza.

DEPENDENCIAS = {
    "BLOCO_1": {
        "Q2": {"Q1": ["BAIXA", "MEDIA", "ALTA"]},
        "Q3": {"Q1": ["BAIXA", "MEDIA", "ALTA"]},
        "Q4": {"Q1": ["BAIXA", "MEDIA", "ALTA"]},
    },
    "BLOCO_2": {
        "Q2": {"Q1": ["BAIXA", "MEDIA", "ALTA"]},
    },
    "BLOCO_3": {
        "Q2": {"Q1": ["DEPENDE_PARCIALMENTE", "DEPENDE_CRITICAMENTE"]},
        "Q3": {"Q1": ["DEPENDE_PARCIALMENTE", "DEPENDE_CRITICAMENTE"]},
        "Q4": {"Q1": ["DEPENDE_PARCIALMENTE", "DEPENDE_CRITICAMENTE"]},
        "Q5": {"Q1": ["DEPENDE_PARCIALMENTE", "DEPENDE_CRITICAMENTE"]},
    },
    "BLOCO_4": {
        "Q2": {"Q1": ["EXISTEM_COM_MARGEM", "EXISTEM_CRITICOS"]},
        "Q3": {"Q1": ["EXISTEM_COM_MARGEM", "EXISTEM_CRITICOS"]},
        "Q4": {"Q1": ["EXISTEM_COM_MARGEM", "EXISTEM_CRITICOS"]},
        "Q5": {"Q1": ["EXISTEM_COM_MARGEM", "EXISTEM_CRITICOS"]},
    },
    "BLOCO_5": {
        # Todas obrigatorias, sem condicionais
    },
    "BLOCO_6": {
        "Q2": {"Q1": ["POSSIVEL", "PROVAVEL"]},
        "Q3": {"Q1": ["POSSIVEL", "PROVAVEL"]},
        "Q4": {"Q1": ["POSSIVEL", "PROVAVEL"]},
        "Q5": {"Q1": ["POSSIVEL", "PROVAVEL"]},
    },
    "BLOCO_7": {
        "Q2": {"Q1": ["SIM"]},
        "Q3": {"Q1": ["SIM"]},
        "Q4": {"Q1": ["SIM"]},
        "Q5": {"Q1": ["SIM"]},
    },
}


# =============================================================================
# LABELS PARA ENUMS (conversao para texto legivel)
# =============================================================================

LABELS = {
    # --- Bloco 1: Dependencia de Terceiros ---
    "NAO_EXISTE": "Nao existe",
    "BAIXA": "Baixa",
    "MEDIA": "Media",
    "ALTA": "Alta",
    "FORMAL": "Formal (contrato, ACT, convenio vigente)",
    "PARCIAL": "Parcial (minuta, termo em negociacao)",
    "INFORMAL": "Informal (sem instrumento valido)",
    "CONTRATO_VIGENTE": "Contrato vigente",
    "CONTRATACAO_FUTURA": "Contratacao futura",
    "LICITACAO_NAO_REALIZADA": "Licitacao nao realizada",
    "CONTRATO_TEMPORARIO_SAZONAL": "Contrato temporario/sazonal",
    "NAO_SE_APLICA": "Nao se aplica",
    "NAO_CRITICA": "Nao critica",
    "IMPORTANTE": "Importante",
    "CRITICA_PARA_RESULTADO_FINAL": "Critica para o resultado final",

    # --- Bloco 2: Recursos Humanos ---
    "CURTO": "Curto (ate 30 dias, baixo custo)",
    "MEDIO": "Medio (30 a 90 dias, custo moderado)",
    "LONGO": "Longo (mais de 90 dias, alto custo)",
    "NAO": "Nao",
    "MODERADO": "Moderado",
    "ELEVADO": "Elevado",
    "ADEQUADO": "Adequado",
    "INSUFICIENTE": "Insuficiente",

    # --- Bloco 3: Tecnologia e Sistemas ---
    "NAO_DEPENDE": "Nao depende",
    "DEPENDE_PARCIALMENTE": "Depende parcialmente",
    "DEPENDE_CRITICAMENTE": "Depende criticamente",
    "INTERNO": "Interno",
    "EXTERNO": "Externo",
    "MISTO": "Misto",
    "ESTAVEL_CONSOLIDADO": "Estavel e consolidado",
    "EM_IMPLANTACAO_OU_EVOLUCAO": "Em implantacao ou evolucao",
    "INSTAVEL_OU_CRITICO": "Instavel ou critico",
    "SIM_PLENA": "Sim, plenamente",
    "NAO_EXISTE": "Nao existe",
    "OCASIONAL": "Ocasional",
    "RECORRENTE": "Recorrente",

    # --- Bloco 4: Prazos, SLAs e Pressoes Legais ---
    "NAO_EXISTEM": "Nao existem",
    "EXISTEM_COM_MARGEM": "Existem, com margem",
    "EXISTEM_CRITICOS": "Existem, criticos",
    "LEGAL": "Legal (lei, decreto, MP)",
    "REGULAMENTAR": "Regulamentar (portaria, instrucao)",
    "CONTRATUAL": "Contratual (ACT, contrato, convenio)",
    "ADMINISTRATIVA": "Administrativa (meta interna, acordo informal)",
    "FINANCEIRA": "Financeira",
    "RESPONSABILIZACAO_AGENTES": "Responsabilizacao de agentes",
    "JUDICIALIZACAO": "Judicializacao",
    "MULTIPLA": "Multipla",
    "SIM_CLARA": "Sim, clara",
    "LIMITADA": "Limitada",
    "INEXISTENTE": "Inexistente",
    "ORGAOS_CONTROLE": "Orgaos de controle",
    "MIDIA_SOCIEDADE": "Midia/sociedade",
    "PODER_JUDICIARIO": "Poder Judiciario",

    # --- Bloco 5: Governanca e Tomada de Decisao ---
    "CLARA_E_FORMAL": "Clara e formal",
    "CLARA_MAS_INFORMAL": "Clara, mas informal",
    "DIFUSA": "Difusa",
    "EXISTE": "Existe",
    "UMA_INSTANCIA": "Uma instancia",
    "MULTIPLAS_INSTANCIAS": "Multiplas instancias",
    "PREVISIVEL": "Previsivel",
    "PARCIALMENTE_PREVISIVEL": "Parcialmente previsivel",
    "IMPREVISIVEL": "Imprevisivel",
    "POSSIVEL": "Possivel",
    "PROVAVEL": "Provavel",

    # --- Bloco 6: Impacto Desigual ---
    "MULHERES": "Mulheres",
    "PESSOAS_NEGRAS": "Pessoas negras",
    "PESSOAS_COM_DEFICIENCIA": "Pessoas com deficiencia",
    "POPULACOES_VULNERAVEIS": "Populacoes vulneraveis",
    "TERRITORIOS_ESPECIFICOS": "Territorios especificos",
    "OUTROS": "Outros",
    "ACESSO": "Acesso",
    "QUALIDADE_DO_SERVICO": "Qualidade do servico",
    "TRATAMENTO_DESIGUAL": "Tratamento desigual",
    "BARREIRA_TECNOLOGICA": "Barreira tecnologica",
    "EXPOSICAO_A_RISCO": "Exposicao a risco",
    "PONTUAL": "Pontual",
    "SISTEMICO": "Sistemico",
    "NAO_PREVISTAS": "Nao previstas",
    "PREVISTAS_PARCIALMENTE": "Previstas parcialmente",
    "PREVISTAS_E_FORMALIZADAS": "Previstas e formalizadas",

    # --- Frequencia (Bloco B) ---
    "CONTINUO": "Continuo (diario/semanal)",
    "PERIODICO": "Periodico (mensal/trimestral)",
    "PONTUAL": "Pontual (evento unico)",
    "SOB_DEMANDA": "Sob demanda",

    # --- Bloco B Estruturado (v2) ---
    # Recursos
    "PESSOAS": "Pessoas/Equipe",
    "TI": "Sistemas/TI",
    "ORCAMENTO": "Orcamento/Verba",
    "EQUIPAMENTOS": "Equipamentos",
    "INFRAESTRUTURA": "Infraestrutura",
    "MATERIAIS": "Materiais",
    # SLA
    "SIM": "Sim",
    # NAO ja esta definido acima
    "NAO_SEI": "Nao sei/Nao tenho certeza",
    # Dependencia
    "SISTEMAS": "Sistemas externos",
    "TERCEIROS": "Terceiros/Fornecedores",
    "AMBOS": "Sistemas e terceiros",

    # --- Categorias de Risco ---
    "OPERACIONAL": "Operacional",
    "FINANCEIRO": "Financeiro",
    "LEGAL": "Legal",
    "REPUTACIONAL": "Reputacional",
    "TECNOLOGICO": "Tecnologico",
    "IMPACTO_DESIGUAL": "Impacto Desigual",

    # --- Niveis de Risco ---
    "CRITICO": "Critico",
    "ALTO": "Alto",
    "BAIXO": "Baixo",

    # --- Fonte Sugestao ---
    "USUARIO": "Usuario",
    "HELENA_INFERENCIA": "Helena (Inferencia)",

    # --- Grau Confianca ---

    # --- Estrategia Resposta (4 oficiais do Guia MGI) ---
    "EVITAR": "Evitar",
    "MITIGAR": "Mitigar",
    "COMPARTILHAR": "Compartilhar",
    "ACEITAR": "Aceitar",
}


# =============================================================================
# FUNCAO CANONICA DE STATUS
# =============================================================================

def is_respondido(risco: Dict[str, Any]) -> bool:
    """
    Funcao canonica para determinar se um risco tem resposta definida.

    REGRA UNICA (fonte da verdade para Secoes 5 e 6):
    - Risco respondido = tem pelo menos uma RespostaRisco com estrategia E acao

    IMPORTANTE: Esta funcao DEVE ser usada em:
    - build_tratamento() para classificar tratados x pendentes
    - build_leitura_mgi() para identificar riscos sem deliberacao

    NAO usar logica local em nenhum lugar do export.
    """
    respostas = risco.get("respostas", [])
    if not respostas:
        return False

    # Verifica se tem pelo menos uma resposta valida (estrategia + acao)
    for resp in respostas:
        estrategia = (resp.get("estrategia") or "").strip()
        acao = (resp.get("descricao_acao") or resp.get("acao") or "").strip()
        if estrategia and acao:
            return True

    return False


def dedup_acoes(acoes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove acoes duplicadas por chave (estrategia, texto).

    Preserva ordem de insercao. Ignora acoes vazias ou incompletas.

    Args:
        acoes: Lista de dicts com 'estrategia' e 'descricao_acao'/'acao'/'texto'

    Returns:
        Lista sem duplicatas
    """
    vistos = set()
    saida = []

    for a in (acoes or []):
        if not isinstance(a, dict):
            continue

        estrategia = (a.get("estrategia") or "").strip()
        # Suporta varios nomes de campo para texto da acao
        texto = (
            a.get("descricao_acao") or
            a.get("acao") or
            a.get("texto") or
            ""
        ).strip()

        # Ignora acoes incompletas
        if not estrategia or not texto:
            continue

        chave = (estrategia.upper(), texto.lower())
        if chave in vistos:
            continue

        vistos.add(chave)
        saida.append(a)

    return saida


# =============================================================================
# FUNCOES AUXILIARES
# =============================================================================

# =============================================================================
# RENDERIZACAO DEFENSIVA (evitar None, vazios no relatorio)
# =============================================================================

def fmt_text(value: Any, pendente: str = "Pendente") -> str:
    """
    Formata texto para exibicao, substituindo None/vazio por texto padrao.

    Args:
        value: Valor a formatar
        pendente: Texto a exibir se valor for None/vazio

    Returns:
        Texto formatado (nunca None)
    """
    if value is None:
        return pendente
    if isinstance(value, str) and not value.strip():
        return pendente
    return str(value)


def fmt_dash(value: Any) -> str:
    """
    Formata valor numerico/metrica para exibicao, substituindo None por dash.

    Uso: Score, Probabilidade, Impacto, etc.

    Args:
        value: Valor a formatar

    Returns:
        Valor formatado ou "—" se None/vazio
    """
    if value is None:
        return "—"
    if isinstance(value, str) and not value.strip():
        return "—"
    return str(value)


def labelize(value: Any, enum_map: Optional[Dict[str, str]] = None) -> str:
    """
    Converte valor de enum para label legivel.

    Args:
        value: Valor do enum (ex: "NAO_EXISTE")
        enum_map: Mapa customizado (opcional, usa LABELS por padrao)

    Returns:
        Label legivel (ex: "Nao existe")
    """
    if value is None:
        return ""

    # Lista (multipla escolha)
    if isinstance(value, list):
        labels = [labelize(v, enum_map) for v in value]
        return ", ".join(filter(None, labels))

    # String
    value_str = str(value)
    labels_map = enum_map or LABELS
    return labels_map.get(value_str, value_str.replace("_", " ").title())


def format_value(value: Any, required: bool = False) -> Optional[str]:
    """
    Formata valor para exibicao no documento.

    Args:
        value: Valor a formatar
        required: Se True e valor vazio, retorna "Nao informado"

    Returns:
        Valor formatado ou None (se opcional e vazio)
    """
    if value is None or value == "" or value == []:
        return "Nao informado" if required else None

    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else ("Nao informado" if required else None)

    return str(value)


def should_render_question(bloco: str, qid: str, respostas: Dict[str, Any]) -> bool:
    """
    Verifica se uma pergunta deve ser renderizada baseado nas condicionais.

    Args:
        bloco: ID do bloco (ex: "BLOCO_1")
        qid: ID da pergunta (ex: "Q2")
        respostas: Respostas do bloco

    Returns:
        True se deve renderizar, False se condicional nao atendida
    """
    deps = DEPENDENCIAS.get(bloco, {})

    # Sem dependencia = sempre renderiza
    if qid not in deps:
        return True

    # Verifica cada dependencia
    for pergunta_pai, valores_ativos in deps[qid].items():
        valor_pai = respostas.get(pergunta_pai)
        if valor_pai not in valores_ativos:
            return False

    return True


# =============================================================================
# BUILDER DO SNAPSHOT
# =============================================================================

def build_snapshot_payload(analise: AnaliseRiscos) -> Dict[str, Any]:
    """
    Monta o payload completo do snapshot (schema 1.0).

    Args:
        analise: Instancia de AnaliseRiscos

    Returns:
        Dict com estrutura padronizada para export
    """
    # Contexto estruturado (Bloco A + B)
    contexto = analise.contexto_estruturado or {}

    # Respostas dos 7 blocos
    respostas_blocos = analise.respostas_blocos or {}

    # Riscos com respostas
    riscos_payload = []
    riscos = analise.riscos.filter(ativo=True).prefetch_related("respostas")

    for risco in riscos:
        risco_data = {
            "id": str(risco.id),
            "titulo": risco.titulo,
            "descricao": risco.descricao or "",
            "categoria": risco.categoria,
            "probabilidade": risco.probabilidade,
            "impacto": risco.impacto,
            "score_risco": risco.score_risco,
            "nivel_risco": risco.nivel_risco,
            "fonte_sugestao": risco.fonte_sugestao,
            "bloco_origem": risco.bloco_origem or "",
            "justificativa": risco.justificativa or "",
            "grau_confianca": risco.grau_confianca or "",
            "perguntas_acionadoras": risco.perguntas_acionadoras or [],
            "regra_aplicada": risco.regra_aplicada or "",
            # Respostas ao risco (plano de tratamento)
            "respostas": [],
        }

        # Inclui RespostaRisco se existir
        for resposta in risco.respostas.all():
            risco_data["respostas"].append({
                "id": str(resposta.id),
                "estrategia": resposta.estrategia,
                "descricao_acao": resposta.descricao_acao,
                "responsavel_nome": resposta.responsavel_nome,
                "responsavel_area": resposta.responsavel_area,
                "prazo": resposta.prazo.isoformat() if resposta.prazo else None,
            })

        riscos_payload.append(risco_data)

    # Resumo estatistico
    total = len(riscos_payload)
    resumo = {
        "total": total,
        "criticos": sum(1 for r in riscos_payload if r["nivel_risco"] == "CRITICO"),
        "altos": sum(1 for r in riscos_payload if r["nivel_risco"] == "ALTO"),
        "medios": sum(1 for r in riscos_payload if r["nivel_risco"] == "MEDIO"),
        "baixos": sum(1 for r in riscos_payload if r["nivel_risco"] == "BAIXO"),
    }

    # Payload final (schema 1.0)
    return {
        "versao_sistema": VERSAO_SISTEMA,
        "schema_version": SCHEMA_VERSION,
        "fonte_estado_em": analise.atualizado_em.isoformat() if analise.atualizado_em else datetime.now().isoformat(),
        "analise_id": str(analise.id),
        "tipo_origem": analise.tipo_origem,
        "modo_entrada": analise.modo_entrada,
        "status": analise.status,
        "etapa_atual": analise.etapa_atual,
        "contexto_estruturado": contexto,
        "respostas_blocos": respostas_blocos,
        "riscos": riscos_payload,
        "resumo": resumo,
    }


# =============================================================================
# GESTAO DE SNAPSHOTS
# =============================================================================

_SYSTEM_USER_CACHE = None


def get_system_user():
    """
    Retorna usuario do sistema para operacoes automaticas (ex: export sem auth).

    Cria o usuario se nao existir. Usado como fallback quando request.user
    e AnonymousUser mas precisamos criar snapshot.

    Usa cache em memoria para evitar hit no banco a cada export.
    """
    global _SYSTEM_USER_CACHE
    if _SYSTEM_USER_CACHE is not None:
        return _SYSTEM_USER_CACHE

    User = get_user_model()
    username = getattr(settings, "EXPORT_SYSTEM_USERNAME", "system_export")

    user = User.objects.filter(username=username).first()
    if not user:
        user = User.objects.create(
            username=username,
            is_active=True,  # Ativo para evitar filtros de "limpar inativos"
            first_name="Sistema",
            last_name="Export",
        )

    _SYSTEM_USER_CACHE = user
    return user


def criar_snapshot(
    analise: AnaliseRiscos,
    user,
    motivo: str = MotivoSnapshot.MANUAL,
    correlation_id: str = "",
) -> AnaliseSnapshot:
    """
    Cria um novo snapshot da analise.

    Args:
        analise: Instancia de AnaliseRiscos
        user: Usuario que esta criando (pode ser None ou AnonymousUser)
        motivo: MotivoSnapshot (MANUAL, FINALIZACAO, etc)
        correlation_id: ID de correlacao opcional

    Returns:
        AnaliseSnapshot criado
    """
    # Guard-rail: se user nao autenticado, usa system user
    criado_por_tipo = "USER"
    if not getattr(user, "is_authenticated", False):
        user = get_system_user()
        criado_por_tipo = "SYSTEM"

    # Calcula proxima versao
    ultimo = analise.snapshots.order_by("-versao", "-criado_em").first()
    proxima_versao = (ultimo.versao + 1) if ultimo else 1

    # Monta payload
    dados = build_snapshot_payload(analise)

    # Marca no payload se foi criado por sistema (auditoria)
    dados["criado_por_tipo"] = criado_por_tipo

    # Cria snapshot
    snapshot = AnaliseSnapshot.objects.create(
        analise=analise,
        versao=proxima_versao,
        dados_completos=dados,
        motivo_snapshot=motivo,
        correlation_id=correlation_id,
        criado_por=user,
    )

    return snapshot


def _snapshot_invalido(snapshot: AnaliseSnapshot, analise: AnaliseRiscos) -> bool:
    """
    Verifica se snapshot esta invalido/incompleto para export.

    Criterios:
    - dados_completos nao existe ou nao e dict
    - nao tem schema_version (snapshot antigo/ruim)
    - nao tem riscos
    - riscos vazio mas analise tem riscos no model

    Args:
        snapshot: Snapshot a verificar
        analise: Analise para comparar estado atual

    Returns:
        True se snapshot invalido, False se OK
    """
    data = snapshot.dados_completos or {}

    if not isinstance(data, dict) or not data:
        return True

    # Sem schema_version = snapshot antigo/ruim
    if not data.get("schema_version"):
        return True

    riscos = data.get("riscos")
    if riscos is None:
        return True

    # Snapshot diz 0 riscos, mas model tem riscos = incompleto
    try:
        if isinstance(riscos, list) and len(riscos) == 0 and analise.riscos.filter(ativo=True).exists():
            return True
    except Exception:
        # Se der erro no exists, nao bloqueia export
        pass

    return False


def get_snapshot_para_export(analise: AnaliseRiscos, user) -> AnaliseSnapshot:
    """
    Obtem snapshot para export.

    Regra:
    - Se existe snapshot valido, retorna o mais recente
    - Se snapshot invalido/vazio, cria novo MANUAL
    - Se nao existe snapshot, cria um snapshot MANUAL

    Args:
        analise: Instancia de AnaliseRiscos
        user: Usuario solicitando o export

    Returns:
        AnaliseSnapshot para usar no export
    """
    ultimo = analise.snapshots.order_by("-versao", "-criado_em").first()

    if not ultimo:
        return criar_snapshot(analise, user, motivo=MotivoSnapshot.MANUAL)

    # Fallback: snapshot invalido -> cria novo MANUAL
    if _snapshot_invalido(ultimo, analise):
        return criar_snapshot(analise, user, motivo=MotivoSnapshot.MANUAL)

    return ultimo


def verificar_desatualizacao(analise: AnaliseRiscos, snapshot: AnaliseSnapshot) -> bool:
    """
    Verifica se o snapshot esta potencialmente desatualizado.

    Args:
        analise: Instancia de AnaliseRiscos
        snapshot: Snapshot a verificar

    Returns:
        True se houver alteracoes apos o snapshot
    """
    fonte_estado_em = snapshot.dados_completos.get("fonte_estado_em")

    if not fonte_estado_em:
        return True  # Sem data = considera desatualizado

    try:
        snapshot_timestamp = datetime.fromisoformat(fonte_estado_em)
        return analise.atualizado_em > snapshot_timestamp
    except (ValueError, TypeError):
        return True


# =============================================================================
# HELPERS PARA RENDERIZACAO
# =============================================================================

def get_texto_pergunta(bloco: str, qid: str) -> str:
    """
    Retorna o texto da pergunta a partir do schema.

    Args:
        bloco: ID do bloco (ex: "BLOCO_1")
        qid: ID da pergunta (ex: "Q1")

    Returns:
        Texto da pergunta ou string vazia
    """
    bloco_schema = BLOCOS_SCHEMA.get(bloco, {})
    perguntas = bloco_schema.get("perguntas", {})
    pergunta = perguntas.get(qid, {})
    return pergunta.get("texto", "")


def get_titulo_bloco(bloco: str) -> str:
    """
    Retorna o titulo do bloco a partir do schema.

    Args:
        bloco: ID do bloco (ex: "BLOCO_1")

    Returns:
        Titulo do bloco
    """
    bloco_schema = BLOCOS_SCHEMA.get(bloco, {})
    return bloco_schema.get("titulo", bloco)


def build_bloco_renderizado(bloco: str, respostas: Dict[str, Any]) -> Dict[str, Any]:
    """
    Monta estrutura renderizada de um bloco para o documento.

    Args:
        bloco: ID do bloco
        respostas: Respostas do bloco

    Returns:
        Dict com titulo e lista de perguntas/respostas renderizadas
    """
    bloco_schema = BLOCOS_SCHEMA.get(bloco, {})
    perguntas_schema = bloco_schema.get("perguntas", {})

    resultado = {
        "id": bloco,
        "titulo": bloco_schema.get("titulo", bloco),
        "objetivo": bloco_schema.get("objetivo", ""),
        "perguntas": [],
    }

    for qid in sorted(perguntas_schema.keys()):
        # Verifica condicional
        if not should_render_question(bloco, qid, respostas):
            continue

        pergunta_info = perguntas_schema[qid]
        valor_raw = respostas.get(qid)

        # Determina se e obrigatoria
        is_required = pergunta_info.get("obrigatoria", True)

        # Formata valor
        valor_formatado = format_value(valor_raw, required=is_required)

        # Pula se None (opcional vazio)
        if valor_formatado is None:
            continue

        # Labelize se for enum
        valor_label = labelize(valor_raw) if valor_raw else valor_formatado

        resultado["perguntas"].append({
            "id": qid,
            "texto": pergunta_info.get("texto", ""),
            "valor_raw": valor_raw,
            "valor_label": valor_label,
            "tipo": pergunta_info.get("tipo", ""),
            "multipla_escolha": pergunta_info.get("multipla_escolha", False),
        })

    return resultado


# =============================================================================
# BLOCO B - RENDERIZACAO COM FALLBACK (v2)
# =============================================================================

def build_bloco_b_renderizado(bloco_b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Monta estrutura renderizada do Bloco B com fallback entre campos novos e antigos.

    Regra:
    - Se campo estruturado novo existe -> usa ele
    - Se nao existe -> fallback para campo antigo (texto)
    - Layout nao quebra em analises antigas

    Args:
        bloco_b: Dict com campos do Bloco B (estruturados e/ou texto)

    Returns:
        Dict com campos renderizados para exibicao no documento
    """
    resultado = {
        "titulo": "Contexto Operacional",
        "tem_campos_estruturados": _tem_campos_estruturados(bloco_b),
        "campos": [],
    }

    # 1. RECURSOS
    if "recursos" in bloco_b:
        recursos = bloco_b.get("recursos", [])
        recursos_outros = bloco_b.get("recursos_outros", "")
        valor = labelize(recursos) if recursos else "Nenhum selecionado"
        if recursos_outros:
            valor += f" (Outros: {recursos_outros})"
        resultado["campos"].append({
            "id": "recursos",
            "label": "Recursos necessarios",
            "valor": valor,
            "tipo": "estruturado",
        })
    else:
        # Fallback para texto antigo
        texto = bloco_b.get("recursos_necessarios", "")
        if texto:
            resultado["campos"].append({
                "id": "recursos_necessarios",
                "label": "Recursos necessarios",
                "valor": texto,
                "tipo": "texto",
            })

    # 2. ATORES ENVOLVIDOS
    texto_atores = bloco_b.get("atores_envolvidos_texto") or bloco_b.get("areas_atores_envolvidos", "")
    if texto_atores:
        resultado["campos"].append({
            "id": "atores",
            "label": "Areas e atores envolvidos",
            "valor": texto_atores,
            "tipo": "texto",
        })

    # 3. FREQUENCIA
    if "frequencia" in bloco_b:
        freq = bloco_b.get("frequencia", "")
        resultado["campos"].append({
            "id": "frequencia",
            "label": "Frequencia de execucao",
            "valor": labelize(freq),
            "tipo": "estruturado",
        })
    else:
        # Fallback para campo antigo
        freq = bloco_b.get("frequencia_execucao", "")
        if freq:
            resultado["campos"].append({
                "id": "frequencia_execucao",
                "label": "Frequencia de execucao",
                "valor": labelize(freq),
                "tipo": "selecao",
            })

    # 4. SLA / PRAZOS
    if "sla" in bloco_b:
        sla = bloco_b.get("sla", "")
        sla_detalhe = bloco_b.get("sla_detalhe", "")
        valor = labelize(sla)
        if sla_detalhe:
            valor += f" - {sla_detalhe}"
        resultado["campos"].append({
            "id": "sla",
            "label": "Prazos legais ou SLAs",
            "valor": valor,
            "tipo": "estruturado",
        })
    else:
        # Fallback para texto antigo
        texto = bloco_b.get("prazos_slas", "")
        if texto:
            resultado["campos"].append({
                "id": "prazos_slas",
                "label": "Prazos legais ou SLAs",
                "valor": texto,
                "tipo": "texto",
            })

    # 5. DEPENDENCIA EXTERNA
    if "dependencia" in bloco_b:
        dep = bloco_b.get("dependencia", "")
        dep_detalhe = bloco_b.get("dependencia_detalhe", "")
        valor = labelize(dep)
        if dep_detalhe:
            valor += f" - {dep_detalhe}"
        resultado["campos"].append({
            "id": "dependencia",
            "label": "Dependencias externas",
            "valor": valor,
            "tipo": "estruturado",
        })
    else:
        # Fallback para texto antigo
        texto = bloco_b.get("dependencias_externas", "")
        if texto:
            resultado["campos"].append({
                "id": "dependencias_externas",
                "label": "Dependencias externas",
                "valor": texto,
                "tipo": "texto",
            })

    # 6. INCIDENTES / HISTORICO
    if "incidentes" in bloco_b:
        inc = bloco_b.get("incidentes", "")
        inc_detalhe = bloco_b.get("incidentes_detalhe", "")
        valor = labelize(inc)
        if inc_detalhe:
            valor += f" - {inc_detalhe}"
        resultado["campos"].append({
            "id": "incidentes",
            "label": "Historico de problemas/incidentes",
            "valor": valor,
            "tipo": "estruturado",
        })
    else:
        # Fallback para texto antigo
        texto = bloco_b.get("historico_problemas", "")
        if texto:
            resultado["campos"].append({
                "id": "historico_problemas",
                "label": "Historico de problemas/incidentes",
                "valor": texto,
                "tipo": "texto",
            })

    # 7. IMPACTO / CONSEQUENCIA
    texto_impacto = bloco_b.get("consequencia_texto") or bloco_b.get("impacto_se_falhar", "")
    if texto_impacto:
        resultado["campos"].append({
            "id": "impacto",
            "label": "Consequencias se falhar",
            "valor": texto_impacto,
            "tipo": "texto",
            "ancora": True,  # Marcador especial
        })

    return resultado


def _tem_campos_estruturados(bloco_b: Dict[str, Any]) -> bool:
    """
    Verifica se o Bloco B tem campos estruturados (v2).

    Usado para determinar se deve mostrar indicador no documento.
    """
    campos_v2 = {"recursos", "frequencia", "sla", "dependencia", "incidentes"}
    return any(campo in bloco_b for campo in campos_v2)
