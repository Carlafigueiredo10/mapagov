"""
API REST para Analise de Riscos

Endpoints Legados (v1):
- POST /api/analise-riscos/criar/
- GET  /api/analise-riscos/listar/
- GET  /api/analise-riscos/<id>/
- PATCH /api/analise-riscos/<id>/questionario/
- PATCH /api/analise-riscos/<id>/etapa/
- POST /api/analise-riscos/<id>/riscos/
- PATCH /api/analise-riscos/<id>/riscos/<risco_id>/analise/
- DELETE /api/analise-riscos/<id>/riscos/<risco_id>/
- POST /api/analise-riscos/<id>/riscos/<risco_id>/respostas/
- PATCH /api/analise-riscos/<id>/finalizar/

Endpoints v2 (novo fluxo):
- POST /api/analise-riscos/v2/criar/
- PATCH /api/analise-riscos/<id>/contexto/
- PATCH /api/analise-riscos/<id>/blocos/
- POST /api/analise-riscos/<id>/inferir/
"""
import logging
import uuid
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from processos.infra.rate_limiting import rate_limit_user
from processos.models_analise_riscos import (
    AnaliseRiscos,
    RiscoIdentificado,
    RespostaRisco,
    AnaliseSnapshot,
    MotivoSnapshot,
    FonteSugestao,
)
from processos.analise_riscos_enums import StatusAnalise, ModoEntrada, TipoOrigem, StatusTratamento
from processos.domain.helena_analise_riscos.contexto_schema import validar_contexto_minimo
from processos.domain.helena_analise_riscos.regras_inferencia import inferir_todos_riscos
from processos.domain.helena_analise_riscos.leitura_mgi import (
    gerar_leitura_mgi,
    gerar_resumo_mgi,
)

logger = logging.getLogger(__name__)


def resposta_sucesso(resposta: str, dados: dict = None, session_data: dict = None):
    """Response padrao de sucesso"""
    return Response({
        "resposta": resposta,
        "dados": dados or {},
        "session_data": session_data or {},
    }, status=status.HTTP_200_OK)


def resposta_erro(erro: str, codigo: str, http_status: int = 400):
    """Response padrao de erro"""
    return Response({"erro": erro, "codigo": codigo}, status=http_status)


def get_orgao_id(request):
    """Extrai orgao_id do usuario (RLS)"""
    if hasattr(request.user, "orgao_id"):
        return request.user.orgao_id
    return uuid.UUID("00000000-0000-0000-0000-000000000000")


# =============================================================================
# ANALISE
# =============================================================================

@api_view(["POST"])
@rate_limit_user(limit=30, window=60)
def criar_analise(request):
    """POST /api/analise-riscos/criar/"""
    try:
        data = request.data
        user = request.user
        orgao_id = get_orgao_id(request)

        tipo_origem = data.get("tipo_origem", "POP")
        origem_id = data.get("origem_id")

        if not origem_id:
            return resposta_erro("origem_id obrigatorio", "ORIGEM_OBRIGATORIA")

        analise = AnaliseRiscos.objects.create(
            orgao_id=orgao_id,
            tipo_origem=tipo_origem,
            origem_id=origem_id,
            status=StatusAnalise.RASCUNHO.value,
            criado_por=user,
        )

        logger.info(f"Analise criada: {analise.id} por {user.username}")

        return Response({
            "resposta": "Analise criada com sucesso",
            "dados": {"id": str(analise.id), "status": analise.status},
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.exception("Erro ao criar analise")
        return resposta_erro(str(e), "ERRO_INTERNO", 500)


@api_view(["GET"])
@rate_limit_user(limit=60, window=60)
def listar_analises(request):
    """GET /api/analise-riscos/listar/"""
    try:
        orgao_id = get_orgao_id(request)

        analises = AnaliseRiscos.objects.filter(orgao_id=orgao_id).order_by("-criado_em")

        dados = [
            {
                "id": str(a.id),
                "tipo_origem": a.tipo_origem,
                "status": a.status,
                "etapa_atual": a.etapa_atual,
                "area_decipex": a.area_decipex,
                "criado_em": a.criado_em.isoformat(),
            }
            for a in analises[:50]
        ]

        return resposta_sucesso(
            resposta=f"{len(dados)} analises encontradas",
            dados={"analises": dados},
        )
    except Exception as e:
        logger.exception("Erro ao listar analises")
        return resposta_erro(str(e), "ERRO_INTERNO", 500)


@api_view(["GET"])
@rate_limit_user(limit=60, window=60)
def detalhar_analise(request, analise_id):
    """GET /api/analise-riscos/<id>/"""
    try:
        orgao_id = get_orgao_id(request)

        analise = AnaliseRiscos.objects.filter(
            id=analise_id, orgao_id=orgao_id
        ).first()

        if not analise:
            return resposta_erro("Analise nao encontrada", "NAO_ENCONTRADA", 404)

        # Construir lista de riscos com leitura MGI
        riscos = []
        for r in analise.riscos.filter(ativo=True):
            # Gerar leitura institucional MGI apenas se risco foi avaliado (P/I definidos)
            leitura_mgi_dict = None
            if r.score_risco is not None:
                leitura = gerar_leitura_mgi(
                    titulo=r.titulo,
                    categoria_tecnica=r.categoria,
                    score=r.score_risco,
                    descricao=r.descricao or "",
                    justificativa=r.justificativa or "",
                    bloco_origem=r.bloco_origem or "",
                    tipo_origem=analise.tipo_origem,
                )
                leitura_mgi_dict = {
                    "categoria_mgi": leitura.categoria_mgi,
                    "nivel_mgi": leitura.nivel_mgi,
                    "is_integridade": leitura.is_integridade,
                    "fora_do_apetite": leitura.fora_do_apetite,
                    "justificativa_categoria": leitura.justificativa_categoria,
                    "justificativa_apetite": leitura.justificativa_apetite,
                    "integridade_motivo": leitura.integridade_motivo,
                    "integridade_gatilhos": leitura.integridade_gatilhos,
                }

            # Derivar status de tratamento e estrategia (sem migration)
            ultima_resposta = r.respostas.order_by("-id").first()
            tem_resposta = ultima_resposta is not None
            status_tratamento = (
                StatusTratamento.RESPONDIDO.value
                if tem_resposta
                else StatusTratamento.PENDENTE_DE_DELIBERACAO.value
            )

            riscos.append({
                "id": str(r.id),
                "titulo": r.titulo,
                "descricao": r.descricao,
                "categoria": r.categoria,
                "probabilidade": r.probabilidade,
                "impacto": r.impacto,
                "score_risco": r.score_risco,
                "nivel_risco": r.nivel_risco,
                "bloco_origem": r.bloco_origem,
                "grau_confianca": r.grau_confianca,
                "fonte_sugestao": r.fonte_sugestao,
                "ativo": r.ativo,
                # Status de tratamento (derivado, transparencia gerencial)
                "status_tratamento": status_tratamento,
                "resposta_definida": tem_resposta,
                # Dados da resposta (denormalizado para o frontend)
                "estrategia": ultima_resposta.estrategia if ultima_resposta else None,
                "acao_planejada": ultima_resposta.descricao_acao if ultima_resposta else None,
                "responsavel": ultima_resposta.responsavel_nome if ultima_resposta else None,
                # Camada de leitura institucional MGI (None se pendente de avaliacao)
                "leitura_mgi": leitura_mgi_dict,
            })

        # Gerar resumo MGI para a analise
        resumo_mgi = gerar_resumo_mgi(riscos)

        return resposta_sucesso(
            resposta="Analise detalhada",
            dados={
                "id": str(analise.id),
                "modo_entrada": analise.modo_entrada,
                "tipo_origem": analise.tipo_origem,
                "origem_id": str(analise.origem_id) if analise.origem_id else None,
                "status": analise.status,
                "etapa_atual": analise.etapa_atual,
                "contexto_estruturado": analise.contexto_estruturado,
                "respostas_blocos": analise.respostas_blocos,
                "questoes_respondidas": analise.questoes_respondidas,
                "area_decipex": analise.area_decipex,
                "riscos": riscos,
                "resumo_mgi": resumo_mgi,
                "criado_em": analise.criado_em.isoformat(),
                "atualizado_em": analise.atualizado_em.isoformat(),
            },
        )
    except Exception as e:
        logger.exception("Erro ao detalhar analise")
        return resposta_erro(str(e), "ERRO_INTERNO", 500)


@api_view(["PATCH"])
@rate_limit_user(limit=30, window=60)
def atualizar_questionario(request, analise_id):
    """PATCH /api/analise-riscos/<id>/questionario/"""
    try:
        data = request.data
        orgao_id = get_orgao_id(request)

        analise = AnaliseRiscos.objects.filter(
            id=analise_id, orgao_id=orgao_id
        ).first()

        if not analise:
            return resposta_erro("Analise nao encontrada", "NAO_ENCONTRADA", 404)

        if "questoes_respondidas" in data:
            analise.questoes_respondidas = data["questoes_respondidas"]
        if "area_decipex" in data:
            analise.area_decipex = data["area_decipex"]
        if "etapa_atual" in data:
            analise.etapa_atual = data["etapa_atual"]

        analise.save()

        return resposta_sucesso(
            resposta="Questionario atualizado",
            dados={"id": str(analise.id), "etapa_atual": analise.etapa_atual},
        )
    except Exception as e:
        logger.exception("Erro ao atualizar questionario")
        return resposta_erro(str(e), "ERRO_INTERNO", 500)


@api_view(["PATCH"])
@rate_limit_user(limit=30, window=60)
def atualizar_etapa(request, analise_id):
    """PATCH /api/analise-riscos/<id>/etapa/"""
    try:
        data = request.data
        orgao_id = get_orgao_id(request)

        analise = AnaliseRiscos.objects.filter(
            id=analise_id, orgao_id=orgao_id
        ).first()

        if not analise:
            return resposta_erro("Analise nao encontrada", "NAO_ENCONTRADA", 404)

        nova_etapa = data.get("etapa")
        if nova_etapa is None:
            return resposta_erro("etapa obrigatoria", "ETAPA_OBRIGATORIA")

        if not (1 <= nova_etapa <= 6):
            return resposta_erro("Etapa deve ser entre 1 e 6", "ETAPA_INVALIDA")

        # GATE Etapa 4+: P/I obrigatorios
        # Nao pode avancar para Matriz (etapa 4) ou alem sem todos os riscos avaliados
        if nova_etapa >= 4:
            from django.db.models import Q
            riscos_sem_pi = analise.riscos.filter(
                ativo=True
            ).filter(
                Q(probabilidade__isnull=True) | Q(impacto__isnull=True)
            ).count()
            if riscos_sem_pi > 0:
                return resposta_erro(
                    f"{riscos_sem_pi} risco(s) sem Probabilidade/Impacto definido. "
                    "Preencha todos na Etapa 3 antes de avancar.",
                    "PI_OBRIGATORIO"
                )

        analise.etapa_atual = nova_etapa
        if nova_etapa > 1:
            analise.status = StatusAnalise.EM_ANALISE.value
        analise.save()

        return resposta_sucesso(
            resposta=f"Etapa atualizada para {nova_etapa}",
            dados={"id": str(analise.id), "etapa_atual": analise.etapa_atual},
        )
    except Exception as e:
        logger.exception("Erro ao atualizar etapa")
        return resposta_erro(str(e), "ERRO_INTERNO", 500)


@api_view(["PATCH"])
@rate_limit_user(limit=10, window=60)
def finalizar_analise(request, analise_id):
    """PATCH /api/analise-riscos/<id>/finalizar/"""
    try:
        orgao_id = get_orgao_id(request)

        # Garantir usuario valido
        from django.contrib.auth.models import User
        if request.user.is_authenticated:
            user = request.user
        else:
            user, _ = User.objects.get_or_create(
                username='teste_helena',
                defaults={'email': 'teste@helena.com'}
            )

        analise = AnaliseRiscos.objects.filter(
            id=analise_id, orgao_id=orgao_id
        ).first()

        if not analise:
            return resposta_erro("Analise nao encontrada", "NAO_ENCONTRADA", 404)

        analise.status = StatusAnalise.FINALIZADA.value
        analise.save()

        # Criar snapshot de finalizacao
        ultima_versao = AnaliseSnapshot.objects.filter(analise=analise).count()
        AnaliseSnapshot.objects.create(
            analise=analise,
            versao=ultima_versao + 1,
            dados_completos={"status": "FINALIZADA"},
            motivo_snapshot=MotivoSnapshot.FINALIZACAO,
            criado_por=user,
        )

        logger.info(f"Analise finalizada: {analise.id} por {user.username}")

        return resposta_sucesso(
            resposta="Analise finalizada",
            dados={"id": str(analise.id), "status": analise.status},
        )
    except Exception as e:
        logger.exception("Erro ao finalizar analise")
        return resposta_erro(str(e), "ERRO_INTERNO", 500)


# =============================================================================
# RISCOS
# =============================================================================

@api_view(["POST"])
@rate_limit_user(limit=30, window=60)
def adicionar_risco(request, analise_id):
    """POST /api/analise-riscos/<id>/riscos/"""
    try:
        data = request.data
        orgao_id = get_orgao_id(request)

        analise = AnaliseRiscos.objects.filter(
            id=analise_id, orgao_id=orgao_id
        ).first()

        if not analise:
            return resposta_erro("Analise nao encontrada", "NAO_ENCONTRADA", 404)

        titulo = data.get("titulo")
        if not titulo:
            return resposta_erro("titulo obrigatorio", "TITULO_OBRIGATORIO")

        # P/I podem ser None (pendente de avaliacao) - NAO usar defaults
        prob = data.get("probabilidade")
        imp = data.get("impacto")

        # Valida se fornecidos
        if prob is not None and not (1 <= prob <= 5):
            return resposta_erro("Probabilidade deve ser 1-5", "PROB_INVALIDA")
        if imp is not None and not (1 <= imp <= 5):
            return resposta_erro("Impacto deve ser 1-5", "IMPACTO_INVALIDO")

        risco = RiscoIdentificado.objects.create(
            orgao_id=orgao_id,
            analise=analise,
            titulo=titulo,
            descricao=data.get("descricao", ""),
            categoria=data.get("categoria", "OPERACIONAL"),
            probabilidade=prob,
            impacto=imp,
            fonte_sugestao=data.get("fonte_sugestao", "USUARIO"),
        )

        return Response({
            "resposta": "Risco adicionado",
            "dados": {
                "id": str(risco.id),
                "titulo": risco.titulo,
                "score_risco": risco.score_risco,
                "nivel_risco": risco.nivel_risco,
            },
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.exception("Erro ao adicionar risco")
        return resposta_erro(str(e), "ERRO_INTERNO", 500)


@api_view(["PATCH"])
@rate_limit_user(limit=30, window=60)
def analisar_risco(request, analise_id, risco_id):
    """PATCH /api/analise-riscos/<id>/riscos/<risco_id>/analise/"""
    try:
        data = request.data
        orgao_id = get_orgao_id(request)

        risco = RiscoIdentificado.objects.filter(
            id=risco_id, analise_id=analise_id, orgao_id=orgao_id
        ).first()

        if not risco:
            return resposta_erro("Risco nao encontrado", "NAO_ENCONTRADO", 404)

        if "probabilidade" in data:
            prob = data["probabilidade"]
            if not (1 <= prob <= 5):
                return resposta_erro("Probabilidade deve ser 1-5", "PROB_INVALIDA")
            risco.probabilidade = prob

        if "impacto" in data:
            imp = data["impacto"]
            if not (1 <= imp <= 5):
                return resposta_erro("Impacto deve ser 1-5", "IMPACTO_INVALIDO")
            risco.impacto = imp

        risco.save()

        return resposta_sucesso(
            resposta="Analise do risco atualizada",
            dados={
                "id": str(risco.id),
                "probabilidade": risco.probabilidade,
                "impacto": risco.impacto,
                "score_risco": risco.score_risco,
                "nivel_risco": risco.nivel_risco,
            },
        )
    except Exception as e:
        logger.exception("Erro ao analisar risco")
        return resposta_erro(str(e), "ERRO_INTERNO", 500)


@api_view(["DELETE"])
@rate_limit_user(limit=20, window=60)
def remover_risco(request, analise_id, risco_id):
    """DELETE /api/analise-riscos/<id>/riscos/<risco_id>/"""
    try:
        orgao_id = get_orgao_id(request)

        risco = RiscoIdentificado.objects.filter(
            id=risco_id, analise_id=analise_id, orgao_id=orgao_id
        ).first()

        if not risco:
            return resposta_erro("Risco nao encontrado", "NAO_ENCONTRADO", 404)

        risco.ativo = False
        risco.save()

        return resposta_sucesso(
            resposta="Risco removido",
            dados={"id": str(risco.id)},
        )
    except Exception as e:
        logger.exception("Erro ao remover risco")
        return resposta_erro(str(e), "ERRO_INTERNO", 500)


# =============================================================================
# RESPOSTAS
# =============================================================================

@api_view(["POST"])
@rate_limit_user(limit=30, window=60)
def adicionar_resposta(request, analise_id, risco_id):
    """POST /api/analise-riscos/<id>/riscos/<risco_id>/respostas/"""
    try:
        data = request.data
        orgao_id = get_orgao_id(request)

        risco = RiscoIdentificado.objects.filter(
            id=risco_id, analise_id=analise_id, orgao_id=orgao_id
        ).first()

        if not risco:
            return resposta_erro("Risco nao encontrado", "NAO_ENCONTRADO", 404)

        estrategia = data.get("estrategia")
        if not estrategia:
            return resposta_erro("estrategia obrigatoria", "ESTRATEGIA_OBRIGATORIA")

        resposta_risco = RespostaRisco.objects.create(
            orgao_id=orgao_id,
            risco=risco,
            estrategia=estrategia,
            descricao_acao=data.get("descricao_acao", ""),
            responsavel_nome=data.get("responsavel_nome", ""),
            responsavel_area=data.get("responsavel_area", ""),
            prazo=data.get("prazo"),
        )

        return Response({
            "resposta": "Resposta adicionada",
            "dados": {
                "id": str(resposta_risco.id),
                "estrategia": resposta_risco.estrategia,
            },
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.exception("Erro ao adicionar resposta")
        return resposta_erro(str(e), "ERRO_INTERNO", 500)


# =============================================================================
# API v2 - NOVO FLUXO DE ANALISE DE RISCOS
# =============================================================================

BLOCOS_ESPERADOS = {"BLOCO_1", "BLOCO_2", "BLOCO_3", "BLOCO_4", "BLOCO_5", "BLOCO_6"}


def resposta_erro_v2(erro: str, codigo: str, http_status: int = 400, dados: dict = None):
    """Response padrao de erro v2 com dados opcionais"""
    resp = {"erro": erro, "codigo": codigo}
    if dados:
        resp["dados"] = dados
    return Response(resp, status=http_status)


@api_view(["POST"])
@rate_limit_user(limit=30, window=60)
def criar_analise_v2(request):
    """POST /api/analise-riscos/v2/criar/

    Cria nova analise com suporte a modo_entrada.

    Body:
        modo_entrada: QUESTIONARIO | PDF | ID
        tipo_origem: PROJETO | PROCESSO | POP | POLITICA | NORMA | PLANO
        origem_id: UUID (obrigatorio se modo_entrada=ID)
    """
    try:
        data = request.data
        orgao_id = get_orgao_id(request)

        # Garantir usuario valido (mesmo padrao do chat_api)
        from django.contrib.auth.models import User
        if request.user.is_authenticated:
            user = request.user
        else:
            user, _ = User.objects.get_or_create(
                username='teste_helena',
                defaults={'email': 'teste@helena.com'}
            )

        modo_entrada = data.get("modo_entrada", ModoEntrada.QUESTIONARIO.value)
        tipo_origem = data.get("tipo_origem")
        origem_id = data.get("origem_id")

        # Validar tipo_origem obrigatorio
        if not tipo_origem:
            return resposta_erro_v2("tipo_origem obrigatorio", "TIPO_ORIGEM_OBRIGATORIO")

        # Validar tipo_origem valido
        tipos_validos = [t.value for t in TipoOrigem]
        if tipo_origem not in tipos_validos:
            return resposta_erro_v2(
                f"tipo_origem invalido. Valores aceitos: {tipos_validos}",
                "TIPO_ORIGEM_INVALIDO"
            )

        # Validar modo_entrada valido
        modos_validos = [m.value for m in ModoEntrada]
        if modo_entrada not in modos_validos:
            return resposta_erro_v2(
                f"modo_entrada invalido. Valores aceitos: {modos_validos}",
                "MODO_ENTRADA_INVALIDO"
            )

        # Se modo_entrada=ID, origem_id e obrigatorio
        if modo_entrada == ModoEntrada.ID.value and not origem_id:
            return resposta_erro_v2(
                "origem_id obrigatorio quando modo_entrada=ID",
                "ORIGEM_ID_OBRIGATORIO"
            )

        analise = AnaliseRiscos.objects.create(
            orgao_id=orgao_id,
            modo_entrada=modo_entrada,
            tipo_origem=tipo_origem,
            origem_id=origem_id if origem_id else None,
            status=StatusAnalise.RASCUNHO.value,
            etapa_atual=0,
            criado_por=user,
        )

        logger.info(f"Analise v2 criada: {analise.id} modo={modo_entrada} por {user.username}")

        return Response({
            "resposta": "Analise criada com sucesso",
            "dados": {
                "id": str(analise.id),
                "modo_entrada": analise.modo_entrada,
                "tipo_origem": analise.tipo_origem,
                "status": analise.status,
                "etapa_atual": analise.etapa_atual,
            },
            "session_data": {},
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.exception("Erro ao criar analise v2")
        return resposta_erro_v2(str(e), "ERRO_INTERNO", 500)


@api_view(["GET", "PATCH"])
@rate_limit_user(limit=30, window=60)
def salvar_contexto_v2(request, analise_id):
    """GET/PATCH /api/analise-riscos/<id>/contexto/

    GET: Retorna contexto estruturado atual (para carregar no formulario)
    PATCH: Salva contexto estruturado (Etapa 1 - Bloco A + B)

    Body (PATCH):
        contexto_estruturado: {
            bloco_a: {...},
            bloco_b: {...}  // Suporta campos estruturados v2 (aditivos)
        }
    """
    try:
        orgao_id = get_orgao_id(request)

        analise = AnaliseRiscos.objects.filter(
            id=analise_id, orgao_id=orgao_id
        ).first()

        if not analise:
            return resposta_erro_v2("Analise nao encontrada", "NAO_ENCONTRADA", 404)

        # GET: retorna contexto atual
        if request.method == "GET":
            return resposta_sucesso(
                resposta="Contexto carregado",
                dados={
                    "id": str(analise.id),
                    "contexto_estruturado": analise.contexto_estruturado or {},
                    "etapa_atual": analise.etapa_atual,
                },
            )

        # PATCH: salva contexto
        data = request.data

        # Garantir usuario valido
        from django.contrib.auth.models import User
        if request.user.is_authenticated:
            user = request.user
        else:
            user, _ = User.objects.get_or_create(
                username='teste_helena',
                defaults={'email': 'teste@helena.com'}
            )

        contexto_novo = data.get("contexto_estruturado", {})
        validar = data.get("validar", False)  # Cliente pode pedir validacao explicita

        # Merge profundo: preserva campos existentes que nao foram enviados
        contexto_atual = analise.contexto_estruturado or {}
        contexto_merged = _merge_contexto(contexto_atual, contexto_novo)

        # Validar GATE de contexto minimo SOMENTE se:
        # - Cliente pediu explicitamente (validar=true)
        # - Ou esta tentando avancar etapa (etapa_atual >= 1 e quer ir para 2+)
        if validar:
            erros = validar_contexto_minimo(contexto_merged, analise.modo_entrada)
            if erros:
                campos_faltando = list(erros.keys())
                return resposta_erro_v2(
                    "Contexto incompleto",
                    "CONTEXTO_INCOMPLETO",
                    400,
                    dados={"faltando": campos_faltando, "erros": erros}
                )

        # Se ja existir contexto, criar snapshot antes de atualizar
        if contexto_atual and contexto_atual != {}:
            ultima_versao = AnaliseSnapshot.objects.filter(analise=analise).count()
            AnaliseSnapshot.objects.create(
                analise=analise,
                versao=ultima_versao + 1,
                dados_completos={
                    "contexto_estruturado": contexto_atual,
                    "etapa_atual": analise.etapa_atual,
                },
                motivo_snapshot=MotivoSnapshot.EDICAO_CONTEXTO,
                criado_por=user,
            )
            logger.info(f"Snapshot criado para analise {analise.id} antes de editar contexto")

        analise.contexto_estruturado = contexto_merged
        analise.etapa_atual = max(analise.etapa_atual, 1)  # Avanca para etapa 1 se estava em 0
        analise.save()

        return resposta_sucesso(
            resposta="Contexto salvo com sucesso",
            dados={
                "id": str(analise.id),
                "etapa_atual": analise.etapa_atual,
                "contexto_estruturado": analise.contexto_estruturado,
            },
        )
    except Exception as e:
        logger.exception("Erro ao salvar contexto v2")
        return resposta_erro_v2(str(e), "ERRO_INTERNO", 500)


def _merge_contexto(atual: dict, novo: dict) -> dict:
    """
    Merge profundo de contexto: bloco_a e bloco_b separadamente.

    Preserva campos existentes que nao foram enviados no payload novo.
    Isso garante retrocompatibilidade: campos antigos nao sao apagados
    quando o frontend envia apenas campos novos.
    """
    resultado = {}

    # Merge bloco_a
    bloco_a_atual = atual.get("bloco_a", {})
    bloco_a_novo = novo.get("bloco_a", {})
    resultado["bloco_a"] = {**bloco_a_atual, **bloco_a_novo}

    # Merge bloco_b (campos antigos + estruturados v2)
    bloco_b_atual = atual.get("bloco_b", {})
    bloco_b_novo = novo.get("bloco_b", {})
    resultado["bloco_b"] = {**bloco_b_atual, **bloco_b_novo}

    return resultado


@api_view(["PATCH"])
@rate_limit_user(limit=30, window=60)
def salvar_blocos_v2(request, analise_id):
    """PATCH /api/analise-riscos/<id>/blocos/

    Salva respostas dos 6 blocos de identificacao de riscos (Etapa 2).

    Body:
        respostas_blocos: {
            BLOCO_1: {Q1: ..., Q2: ...},
            BLOCO_2: {...},
            ...
        }
    """
    try:
        data = request.data
        orgao_id = get_orgao_id(request)

        # Garantir usuario valido
        from django.contrib.auth.models import User
        if request.user.is_authenticated:
            user = request.user
        else:
            user, _ = User.objects.get_or_create(
                username='teste_helena',
                defaults={'email': 'teste@helena.com'}
            )

        analise = AnaliseRiscos.objects.filter(
            id=analise_id, orgao_id=orgao_id
        ).first()

        if not analise:
            return resposta_erro_v2("Analise nao encontrada", "NAO_ENCONTRADA", 404)

        respostas = data.get("respostas_blocos", {})

        # Validar formato basico
        if not isinstance(respostas, dict):
            return resposta_erro_v2(
                "respostas_blocos deve ser um objeto",
                "FORMATO_INVALIDO"
            )

        # Validar que as chaves sao blocos esperados
        chaves_invalidas = set(respostas.keys()) - BLOCOS_ESPERADOS
        if chaves_invalidas:
            return resposta_erro_v2(
                f"Blocos invalidos: {list(chaves_invalidas)}. Esperados: {list(BLOCOS_ESPERADOS)}",
                "BLOCOS_INVALIDOS"
            )

        # Validar que cada bloco e um dict
        for bloco, valores in respostas.items():
            if not isinstance(valores, dict):
                return resposta_erro_v2(
                    f"{bloco} deve ser um objeto com respostas",
                    "FORMATO_BLOCO_INVALIDO"
                )

        analise.respostas_blocos = respostas
        analise.etapa_atual = max(analise.etapa_atual, 2)  # Avanca para etapa 2 se estava antes
        analise.save()

        return resposta_sucesso(
            resposta="Blocos salvos com sucesso",
            dados={
                "id": str(analise.id),
                "etapa_atual": analise.etapa_atual,
                "blocos_salvos": list(respostas.keys()),
            },
        )
    except Exception as e:
        logger.exception("Erro ao salvar blocos v2")
        return resposta_erro_v2(str(e), "ERRO_INTERNO", 500)


@api_view(["POST"])
@rate_limit_user(limit=10, window=60)
def inferir_riscos_v2(request, analise_id):
    """POST /api/analise-riscos/<id>/inferir/

    Executa inferencia de riscos baseada nas respostas dos blocos.
    Idempotente: nao duplica riscos de mesma regra/bloco/perguntas.

    Requer:
        - contexto_estruturado preenchido (gate)
        - respostas_blocos com ao menos um bloco
    """
    try:
        orgao_id = get_orgao_id(request)

        # Garantir usuario valido
        from django.contrib.auth.models import User
        if request.user.is_authenticated:
            user = request.user
        else:
            user, _ = User.objects.get_or_create(
                username='teste_helena',
                defaults={'email': 'teste@helena.com'}
            )

        analise = AnaliseRiscos.objects.filter(
            id=analise_id, orgao_id=orgao_id
        ).first()

        if not analise:
            return resposta_erro_v2("Analise nao encontrada", "NAO_ENCONTRADA", 404)

        # Gate: contexto deve estar preenchido
        if not analise.contexto_estruturado or analise.contexto_estruturado == {}:
            return resposta_erro_v2(
                "Contexto estruturado deve ser preenchido antes da inferencia",
                "CONTEXTO_NAO_PREENCHIDO"
            )

        # Gate: deve ter respostas de blocos
        if not analise.respostas_blocos or analise.respostas_blocos == {}:
            return resposta_erro_v2(
                "Respostas dos blocos devem ser preenchidas antes da inferencia",
                "BLOCOS_NAO_PREENCHIDOS"
            )

        # Executar inferencia
        riscos_inferidos = inferir_todos_riscos(analise.respostas_blocos)

        # Criar riscos no banco (idempotente)
        riscos_criados = []
        riscos_existentes = 0

        with transaction.atomic():
            for ri in riscos_inferidos:
                # Verificar idempotencia: mesma regra + bloco + perguntas
                perguntas_sorted = sorted(ri.perguntas_acionadoras)
                existe = RiscoIdentificado.objects.filter(
                    analise=analise,
                    regra_aplicada=ri.regra_id,
                    bloco_origem=ri.bloco_origem,
                    perguntas_acionadoras=perguntas_sorted,
                    fonte_sugestao=FonteSugestao.HELENA_INFERENCIA,
                ).exists()

                if existe:
                    riscos_existentes += 1
                    continue

                # P/I ficam None - usuario DEVE avaliar na Etapa 3
                risco = RiscoIdentificado.objects.create(
                    orgao_id=orgao_id,
                    analise=analise,
                    titulo=ri.titulo,
                    categoria=ri.categoria,
                    bloco_origem=ri.bloco_origem,
                    perguntas_acionadoras=perguntas_sorted,
                    regra_aplicada=ri.regra_id,
                    grau_confianca=ri.grau_confianca,
                    justificativa=ri.justificativa,
                    fonte_sugestao=FonteSugestao.HELENA_INFERENCIA,
                    # probabilidade e impacto ficam None (pendente de avaliacao)
                )
                riscos_criados.append({
                    "id": str(risco.id),
                    "titulo": risco.titulo,
                    "categoria": risco.categoria,
                    "bloco_origem": risco.bloco_origem,
                    "grau_confianca": risco.grau_confianca,
                })

            # Atualizar status se criou riscos
            if riscos_criados:
                analise.status = StatusAnalise.EM_ANALISE.value
                analise.save()

        logger.info(
            f"Inferencia analise {analise.id}: {len(riscos_criados)} criados, "
            f"{riscos_existentes} ja existiam"
        )

        return resposta_sucesso(
            resposta=f"{len(riscos_criados)} riscos inferidos",
            dados={
                "id": str(analise.id),
                "riscos_criados": len(riscos_criados),
                "riscos_ja_existentes": riscos_existentes,
                "total_inferidos": len(riscos_inferidos),
                "riscos": riscos_criados,
            },
        )
    except Exception as e:
        logger.exception("Erro ao inferir riscos v2")
        return resposta_erro_v2(str(e), "ERRO_INTERNO", 500)
