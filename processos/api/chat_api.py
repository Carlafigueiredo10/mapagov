"""
Chat API - Endpoint principal para Helena (FASE 1)

Integra:
- HelenaCore (orquestrador)
- SessionManager (Redis + PostgreSQL)
- Produtos Helena (etapas, pop, fluxograma, etc.)
"""
import uuid
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from processos.app.helena_core import HelenaCore
from processos.domain.helena_produtos.helena_etapas import HelenaEtapas
from processos.domain.helena_produtos.helena_pop import HelenaPOP
from processos.domain.helena_produtos.helena_mapeamento import HelenaMapeamento
from processos.domain.helena_produtos.helena_plano_acao import HelenaPlanoAcao
from processos.infra.rate_limiting import rate_limit_user  # FASE 2: Rate limiting
# Importar outros produtos conforme necessário

logger = logging.getLogger(__name__)


# Singleton do HelenaCore (criado uma vez)
_helena_core_instance = None


def get_helena_core() -> HelenaCore:
    """
    Retorna instância singleton do HelenaCore.

    Registry com todos os produtos Helena disponíveis.
    """
    global _helena_core_instance

    if _helena_core_instance is None:
        # Registrar produtos Helena
        registry = {
            'pop': HelenaPOP(),
            'etapas': HelenaEtapas(),
            'mapeamento': HelenaMapeamento(),
            'plano_acao': HelenaPlanoAcao(),
            # 'fluxograma': HelenaFluxograma(),
            # 'riscos': HelenaAnaliseRiscos(),
        }

        _helena_core_instance = HelenaCore(registry=registry)
        logger.info(f"HelenaCore inicializado com {len(registry)} produtos")

    return _helena_core_instance


@csrf_exempt  # Temporário - adicionar CSRF token no frontend depois
@require_http_methods(["POST"])
@rate_limit_user(limit=30, window=60)  # FASE 2: 30 mensagens/minuto por usuário
# @login_required  # TEMPORÁRIO: comentado para testes sem autenticação
def chat_v2(request):
    """
    Endpoint principal do chat (FASE 1).

    POST /api/chat-v2/

    Body:
    {
        "mensagem": "texto do usuário",
        "session_id": "uuid-da-sessao" (opcional, cria novo se não existir)
    }

    Response:
    {
        "resposta": "texto da Helena",
        "session_id": "uuid-da-sessao",
        "contexto_atual": "etapas",
        "agentes_disponiveis": ["etapas", "pop"],
        "progresso": "3/5 (60%) [###---]",
        "sugerir_contexto": "pop" (opcional),
        "tipo_interface": "areas" (opcional - ex: areas, dropdown_macro),
        "dados_interface": {...} (opcional - dados para renderizar interface),
        "metadados": {
            "agent_version": "1.0.0",
            "agent_name": "Helena Etapas"
        }
    }
    """
    try:
        # 1. Parse request
        import json
        data = json.loads(request.body)

        mensagem = data.get('mensagem', '').strip()
        session_id = data.get('session_id')

        # Validações
        if not mensagem:
            return JsonResponse({
                'erro': 'Mensagem não pode estar vazia'
            }, status=400)

        # Gera session_id se não existir ou se for inválido
        if not session_id:
            session_id = str(uuid.uuid4())
        else:
            # Validar se é UUID válido
            try:
                uuid.UUID(session_id)
            except (ValueError, AttributeError):
                # Se não for UUID válido, gera novo
                logger.warning(f"Session ID inválido recebido: {session_id}. Gerando novo.")
                session_id = str(uuid.uuid4())

        # 2. Processar via HelenaCore
        helena = get_helena_core()

        # TEMPORÁRIO: Usar user de teste se não autenticado
        from django.contrib.auth.models import User
        user = request.user if request.user.is_authenticated else User.objects.get(username='teste_helena')

        resultado = helena.processar_mensagem(
            mensagem=mensagem,
            session_id=session_id,
            user=user
        )

        # DEBUG CRITICO: Verificar se formulario_pop e dados_extraidos estao na resposta
        if 'formulario_pop' in resultado:
            form = resultado['formulario_pop']
            logger.info("[API] formulario_pop PRESENTE na resposta:")
            logger.info(f"  CAP: {form.get('codigo_cap')} | Macro: {form.get('macroprocesso')} | Atividade: {form.get('atividade')}")
        else:
            logger.error(f"[API] formulario_pop AUSENTE! Chaves: {list(resultado.keys())}")

        if 'dados_extraidos' in resultado:
            dados = resultado['dados_extraidos']
            logger.info(f"[API] dados_extraidos PRESENTE: {list(dados.keys())[:5]}...")
        else:
            logger.warning("[API] dados_extraidos AUSENTE (pode ser normal se estado inicial)")

        # 3. Retornar resposta
        return JsonResponse(resultado, status=200)

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        return JsonResponse({
            'erro': str(e)
        }, status=400)

    except Exception as e:
        import traceback
        print("\n\n" + "="*80)
        print("ERRO COMPLETO NO CHAT_V2:")
        print("="*80)
        traceback.print_exc()
        print("="*80 + "\n\n")
        logger.exception(f"Erro no chat_v2: {e}")
        return JsonResponse({
            'erro': str(e)  # Retorna erro real pro frontend também
        }, status=500)


@require_http_methods(["POST"])
@login_required
def mudar_contexto(request):
    """
    Muda contexto explicitamente.

    POST /api/chat-v2/mudar-contexto/

    Body:
    {
        "session_id": "uuid-da-sessao",
        "contexto": "pop"
    }
    """
    try:
        import json
        data = json.loads(request.body)

        session_id = data.get('session_id')
        novo_contexto = data.get('contexto')

        if not session_id or not novo_contexto:
            return JsonResponse({
                'erro': 'session_id e contexto são obrigatórios'
            }, status=400)

        helena = get_helena_core()
        resultado = helena.mudar_contexto(
            session_id=session_id,
            novo_contexto=novo_contexto,
            user=request.user
        )

        return JsonResponse(resultado, status=200)

    except ValueError as e:
        return JsonResponse({'erro': str(e)}, status=400)

    except Exception as e:
        logger.exception(f"Erro ao mudar contexto: {e}")
        return JsonResponse({'erro': 'Erro interno'}, status=500)


@require_http_methods(["GET"])
@login_required
def listar_produtos(request):
    """
    Lista produtos Helena disponíveis.

    GET /api/chat-v2/produtos/

    Response:
    {
        "produtos": {
            "etapas": {
                "nome": "Helena Etapas",
                "versao": "1.0.0"
            },
            ...
        }
    }
    """
    try:
        helena = get_helena_core()
        produtos = helena.listar_produtos()

        return JsonResponse({
            'produtos': produtos
        }, status=200)

    except Exception as e:
        logger.exception(f"Erro ao listar produtos: {e}")
        return JsonResponse({'erro': 'Erro interno'}, status=500)


@require_http_methods(["GET"])
@login_required
def info_sessao(request, session_id):
    """
    Retorna informações da sessão.

    GET /api/chat-v2/sessao/<session_id>/

    Response:
    {
        "session_id": "...",
        "total_mensagens": 10,
        "mensagens_usuario": 5,
        "mensagens_helena": 5,
        "contexto_atual": "etapas",
        "agentes_usados": ["etapas"],
        "status": "ativa"
    }
    """
    try:
        helena = get_helena_core()
        info = helena.get_session_info(session_id)

        return JsonResponse(info, status=200)

    except Exception as e:
        logger.exception(f"Erro ao buscar info da sessão: {e}")
        return JsonResponse({'erro': 'Erro interno'}, status=500)


@csrf_exempt  # Temporário - adicionar CSRF token no frontend depois
@require_http_methods(["GET"])
# @login_required  # TEMPORÁRIO: comentado para testes sem autenticação
def buscar_mensagens(request, session_id):
    """
    Retorna histórico de mensagens da sessão.

    GET /api/chat-v2/sessao/<session_id>/mensagens/

    Response:
    {
        "session_id": "...",
        "contexto_atual": "pop",
        "mensagens": [
            {
                "role": "assistant",
                "content": "Olá! Qual seu nome?",
                "contexto": "pop",
                "criado_em": "2025-10-23T10:00:00Z"
            },
            {
                "role": "user",
                "content": "carla",
                "contexto": "pop",
                "criado_em": "2025-10-23T10:00:15Z"
            },
            ...
        ]
    }
    """
    try:
        from processos.models_new.chat_session import ChatSession

        # TEMPORÁRIO: Usar user de teste se não autenticado
        from django.contrib.auth.models import User
        user = request.user if request.user.is_authenticated else User.objects.get(username='teste_helena')

        # Buscar sessão
        try:
            session = ChatSession.objects.get(session_id=session_id, user=user)
        except ChatSession.DoesNotExist:
            # ✅ FIX: Retornar lista vazia ao invés de 404 (sessão pode ainda não ter sido criada)
            return JsonResponse({
                'session_id': session_id,
                'contexto_atual': 'pop',  # Default
                'session_exists': False,
                'mensagens': []
            }, status=200, json_dumps_params={'ensure_ascii': False})

        # Buscar mensagens (ordenadas por data)
        mensagens = session.mensagens.all().order_by('criado_em')

        mensagens_dict = [
            {
                'role': msg.role,
                'content': msg.content,
                'contexto': msg.contexto,
                'metadados': msg.metadados,
                'criado_em': msg.criado_em.isoformat() if msg.criado_em else None
            }
            for msg in mensagens
        ]

        return JsonResponse({
            'session_id': str(session.session_id),
            'contexto_atual': session.contexto_atual,
            'session_exists': True,
            'mensagens': mensagens_dict
        }, status=200, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        logger.exception(f"Erro ao buscar mensagens da sessão: {e}")
        return JsonResponse({'erro': 'Erro interno'}, status=500)


@require_http_methods(["POST"])
@login_required
def finalizar_sessao(request):
    """
    Finaliza sessão (força sync com DB, limpa cache).

    POST /api/chat-v2/finalizar/

    Body:
    {
        "session_id": "uuid-da-sessao"
    }
    """
    try:
        import json
        data = json.loads(request.body)
        session_id = data.get('session_id')

        if not session_id:
            return JsonResponse({'erro': 'session_id obrigatório'}, status=400)

        helena = get_helena_core()
        helena.finalizar_sessao(session_id)

        return JsonResponse({
            'mensagem': 'Sessão finalizada com sucesso',
            'session_id': session_id
        }, status=200)

    except Exception as e:
        logger.exception(f"Erro ao finalizar sessão: {e}")
        return JsonResponse({'erro': 'Erro interno'}, status=500)
