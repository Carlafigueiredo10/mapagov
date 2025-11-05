"""
API REST para Helena Planejamento Estratégico

Endpoints:
- POST /api/planejamento-estrategico/iniciar/
- POST /api/planejamento-estrategico/processar/
- POST /api/planejamento-estrategico/salvar/
- GET  /api/planejamento-estrategico/listar/
- GET  /api/planejamento-estrategico/{id}/
- POST /api/planejamento-estrategico/{id}/aprovar/
- POST /api/planejamento-estrategico/{id}/revisar/
- GET  /api/planejamento-estrategico/{id}/exportar/
"""
import logging
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from processos.domain.helena_planejamento_estrategico import (
    HelenaPlanejamentoEstrategico,
    MODELOS_ESTRATEGICOS,
    PERGUNTAS_DIAGNOSTICO
)
from processos.models_new import PlanejamentoEstrategico

logger = logging.getLogger(__name__)


# ============================================================================
# ENDPOINTS PRINCIPAIS
# ============================================================================

@csrf_exempt
@api_view(['POST'])
def iniciar_planejamento(request):
    """
    Inicializa nova sessão de planejamento

    POST /api/planejamento-estrategico/iniciar/

    Body: {}

    Response:
    {
        "session_data": {...},
        "mensagem_inicial": "Olá! Sou a Helena...",
        "modelos_disponiveis": [...],
        "perguntas_diagnostico": [...]
    }
    """
    try:
        import uuid

        helena = HelenaPlanejamentoEstrategico()
        estado_inicial = helena.inicializar_estado()

        # Primeira mensagem
        resposta_boas_vindas = helena.processar("oi", estado_inicial)

        # Gera session_id e adiciona ao session_data
        session_id = str(uuid.uuid4())
        session_data = resposta_boas_vindas['session_data']
        session_data['session_id'] = session_id

        return Response({
            'session_data': session_data,
            'mensagem_inicial': resposta_boas_vindas['resposta'],
            'modelos_disponiveis': [
                {
                    'id': modelo_id,
                    'nome': config['nome_curto'],
                    'nome_completo': config['nome'],
                    'descricao': config['descricao'],
                    'icone': config['icone'],
                    'complexidade': config['complexidade'],
                    'prazo': config['prazo'],
                    'maturidade': config['maturidade'],
                    'tags': config['tags'],
                    'componentes': config['componentes'],
                    'vantagens_publico': config['vantagens_publico'],
                    'quando_usar': config['quando_usar']
                }
                for modelo_id, config in MODELOS_ESTRATEGICOS.items()
            ],
            'perguntas_diagnostico': PERGUNTAS_DIAGNOSTICO
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"[PE API] Erro ao iniciar: {e}", exc_info=True)
        return Response({
            'erro': 'Erro ao inicializar planejamento',
            'detalhes': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
def processar_mensagem(request):
    """
    Processa mensagem do usuário na conversa

    POST /api/planejamento-estrategico/processar/

    Body:
    {
        "mensagem": "quero fazer o diagnostico",
        "session_data": {...}
    }

    Response:
    {
        "resposta": "Ótimo! Vou fazer 5 perguntas...",
        "session_data": {...},
        "estado_atual": "diagnostico_p1",
        "progresso": "1/5",
        "percentual_conclusao": 20,
        "metadados": {
            "modelo_selecionado": "okr",
            "diagnostico_completo": false,
            "validacao": {...}
        }
    }
    """
    try:
        data = request.data
        mensagem = data.get('mensagem', '').strip()
        session_data = data.get('session_data', {})

        if not mensagem:
            return Response({
                'erro': 'Mensagem não pode estar vazia'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Processa com Helena
        helena = HelenaPlanejamentoEstrategico()
        resposta = helena.processar(mensagem, session_data)

        # Adiciona validação se modelo selecionado
        metadados = {}
        novo_estado = resposta['session_data']

        if novo_estado.get('modelo_selecionado'):
            validacao = helena._validar_estrutura_modelo(
                novo_estado['modelo_selecionado'],
                novo_estado.get('estrutura_planejamento', {})
            )
            metadados['validacao'] = validacao

        metadados['modelo_selecionado'] = novo_estado.get('modelo_selecionado')
        metadados['diagnostico_completo'] = len(novo_estado.get('diagnostico', {})) == 5
        metadados['pontuacao_modelos'] = novo_estado.get('pontuacao_modelos', {})

        return Response({
            'resposta': resposta['resposta'],
            'session_data': novo_estado,
            'estado_atual': novo_estado.get('estado_atual'),
            'progresso': resposta.get('progresso', ''),
            'percentual_conclusao': novo_estado.get('percentual_conclusao', 0),
            'metadados': metadados
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"[PE API] Erro ao processar mensagem: {e}", exc_info=True)
        return Response({
            'erro': 'Erro ao processar mensagem',
            'detalhes': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
def salvar_planejamento(request):
    """
    Salva planejamento no banco de dados

    POST /api/planejamento-estrategico/salvar/

    Body:
    {
        "session_data": {...},
        "usuario_id": 1
    }

    Response:
    {
        "sucesso": true,
        "planejamento_id": 42,
        "mensagem": "Planejamento salvo com sucesso!",
        "planejamento": {...}
    }
    """
    try:
        data = request.data
        session_data = data.get('session_data', {})
        usuario_id = data.get('usuario_id')

        # Validação
        if not session_data.get('modelo_selecionado'):
            return Response({
                'erro': 'Modelo não selecionado'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Salva usando Helena
        helena = HelenaPlanejamentoEstrategico()
        planejamento_id = helena._salvar_planejamento(session_data)

        # Retorna planejamento salvo
        planejamento = PlanejamentoEstrategico.objects.get(id=planejamento_id)

        return Response({
            'sucesso': True,
            'planejamento_id': planejamento_id,
            'mensagem': 'Planejamento salvo com sucesso!',
            'planejamento': planejamento.to_dict()
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"[PE API] Erro ao salvar: {e}", exc_info=True)
        return Response({
            'erro': 'Erro ao salvar planejamento',
            'detalhes': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def listar_planejamentos(request):
    """
    Lista planejamentos do usuário

    GET /api/planejamento-estrategico/listar/
    Query params:
    - modelo: filtrar por modelo
    - status: filtrar por status
    - limit: quantidade (default 50)
    - offset: paginação

    Response:
    {
        "total": 10,
        "planejamentos": [...]
    }
    """
    try:
        # Filtros
        modelo = request.GET.get('modelo')
        status_filtro = request.GET.get('status')
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))

        queryset = PlanejamentoEstrategico.objects.all()

        if modelo:
            queryset = queryset.filter(modelo=modelo)
        if status_filtro:
            queryset = queryset.filter(status=status_filtro)

        # TODO: Filtrar por usuário quando autenticação estiver ativa
        # queryset = queryset.filter(criado_por=request.user)

        total = queryset.count()
        planejamentos = queryset[offset:offset+limit]

        return Response({
            'total': total,
            'planejamentos': [p.to_dict() for p in planejamentos]
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"[PE API] Erro ao listar: {e}", exc_info=True)
        return Response({
            'erro': 'Erro ao listar planejamentos',
            'detalhes': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def obter_planejamento(request, planejamento_id):
    """
    Obtém planejamento por ID

    GET /api/planejamento-estrategico/{id}/

    Response:
    {
        "planejamento": {...},
        "indicadores": [...],
        "comentarios": [...]
    }
    """
    try:
        planejamento = PlanejamentoEstrategico.objects.get(id=planejamento_id)

        return Response({
            'planejamento': planejamento.to_dict(),
            'indicadores': [
                {
                    'id': ind.id,
                    'codigo': ind.codigo,
                    'nome': ind.nome,
                    'tipo': ind.tipo,
                    'meta': float(ind.meta),
                    'valor_atual': float(ind.valor_atual) if ind.valor_atual else None,
                    'percentual_atingido': ind.percentual_atingido,
                    'status_semaforo': ind.status_semaforo
                }
                for ind in planejamento.indicadores.all()
            ],
            'comentarios': [
                {
                    'id': com.id,
                    'autor': com.autor.username,
                    'conteudo': com.conteudo,
                    'tipo': com.tipo,
                    'resolvido': com.resolvido,
                    'criado_em': com.criado_em.isoformat()
                }
                for com in planejamento.comentarios.all()
            ]
        }, status=status.HTTP_200_OK)

    except PlanejamentoEstrategico.DoesNotExist:
        return Response({
            'erro': 'Planejamento não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"[PE API] Erro ao obter planejamento: {e}", exc_info=True)
        return Response({
            'erro': 'Erro ao obter planejamento',
            'detalhes': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
def aprovar_planejamento(request, planejamento_id):
    """
    Aprova planejamento

    POST /api/planejamento-estrategico/{id}/aprovar/

    Body:
    {
        "usuario_id": 1
    }

    Response:
    {
        "sucesso": true,
        "mensagem": "Planejamento aprovado!",
        "planejamento": {...}
    }
    """
    try:
        planejamento = PlanejamentoEstrategico.objects.get(id=planejamento_id)

        # TODO: Pegar usuário real da sessão
        from django.contrib.auth.models import User
        usuario = User.objects.get(username='teste_helena')

        planejamento.aprovar(usuario)

        return Response({
            'sucesso': True,
            'mensagem': 'Planejamento aprovado com sucesso!',
            'planejamento': planejamento.to_dict()
        }, status=status.HTTP_200_OK)

    except PlanejamentoEstrategico.DoesNotExist:
        return Response({
            'erro': 'Planejamento não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"[PE API] Erro ao aprovar: {e}", exc_info=True)
        return Response({
            'erro': 'Erro ao aprovar planejamento',
            'detalhes': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
def criar_revisao(request, planejamento_id):
    """
    Cria nova versão do planejamento

    POST /api/planejamento-estrategico/{id}/revisar/

    Body:
    {
        "usuario_id": 1
    }

    Response:
    {
        "sucesso": true,
        "nova_versao_id": 43,
        "mensagem": "Nova versão criada!",
        "planejamento": {...}
    }
    """
    try:
        planejamento = PlanejamentoEstrategico.objects.get(id=planejamento_id)

        # TODO: Pegar usuário real
        from django.contrib.auth.models import User
        usuario = User.objects.get(username='teste_helena')

        nova_versao = planejamento.criar_revisao(usuario)

        return Response({
            'sucesso': True,
            'nova_versao_id': nova_versao.id,
            'mensagem': f'Nova versão v{nova_versao.versao} criada com sucesso!',
            'planejamento': nova_versao.to_dict()
        }, status=status.HTTP_201_CREATED)

    except PlanejamentoEstrategico.DoesNotExist:
        return Response({
            'erro': 'Planejamento não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"[PE API] Erro ao criar revisão: {e}", exc_info=True)
        return Response({
            'erro': 'Erro ao criar revisão',
            'detalhes': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def exportar_planejamento(request, planejamento_id):
    """
    Exporta planejamento em JSON ou PDF

    GET /api/planejamento-estrategico/{id}/exportar/?formato=json|pdf

    Response:
    - JSON: application/json
    - PDF: application/pdf
    """
    try:
        planejamento = PlanejamentoEstrategico.objects.get(id=planejamento_id)
        formato = request.GET.get('formato', 'json')

        if formato == 'json':
            # Export JSON
            return Response(
                planejamento.to_dict(),
                status=status.HTTP_200_OK,
                headers={
                    'Content-Disposition': f'attachment; filename="planejamento_{planejamento_id}.json"'
                }
            )

        elif formato == 'pdf':
            # TODO: Implementar geração de PDF
            # from processos.utils.geradores import GeradorDocumentoPlanejamento
            # gerador = GeradorDocumentoPlanejamento()
            # pdf_content = gerador.gerar_pdf(planejamento)

            return Response({
                'erro': 'Export PDF em desenvolvimento',
                'alternativa': 'Use formato=json'
            }, status=status.HTTP_501_NOT_IMPLEMENTED)

        else:
            return Response({
                'erro': 'Formato inválido',
                'formatos_disponiveis': ['json', 'pdf']
            }, status=status.HTTP_400_BAD_REQUEST)

    except PlanejamentoEstrategico.DoesNotExist:
        return Response({
            'erro': 'Planejamento não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"[PE API] Erro ao exportar: {e}", exc_info=True)
        return Response({
            'erro': 'Erro ao exportar planejamento',
            'detalhes': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# ENDPOINTS AUXILIARES
# ============================================================================

@api_view(['GET'])
def obter_modelos(request):
    """
    Lista todos os modelos disponíveis

    GET /api/planejamento-estrategico/modelos/

    Response:
    {
        "modelos": [...]
    }
    """
    return Response({
        'modelos': [
            {
                'id': modelo_id,
                'nome': config['nome_curto'],
                'nome_completo': config['nome'],
                'descricao': config['descricao'],
                'icone': config['icone'],
                'complexidade': config['complexidade'],
                'prazo': config['prazo'],
                'maturidade': config['maturidade'],
                'tags': config['tags'],
                'componentes': config['componentes'],
                'vantagens_publico': config['vantagens_publico'],
                'quando_usar': config['quando_usar']
            }
            for modelo_id, config in MODELOS_ESTRATEGICOS.items()
        ]
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def obter_diagnostico(request):
    """
    Retorna perguntas do diagnóstico

    GET /api/planejamento-estrategico/diagnostico/

    Response:
    {
        "perguntas": [...]
    }
    """
    return Response({
        'perguntas': PERGUNTAS_DIAGNOSTICO
    }, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def iniciar_modelo_direto(request):
    """
    Inicializa modelo diretamente (sem diagnóstico ou seleção manual)

    POST /api/planejamento-estrategico/iniciar-modelo/

    Body:
    {
        "modelo": "okr"
    }

    Response:
    {
        "session_data": {...},
        "mensagem_confirmacao": "Você escolheu o método OKR. Confirma?",
        "modelo_selecionado": "okr",
        "info_modelo": {...}
    }
    """
    try:
        import uuid

        modelo_id = request.data.get('modelo', '').lower()

        # Valida modelo
        if modelo_id not in MODELOS_ESTRATEGICOS:
            return Response({
                'erro': 'Modelo inválido',
                'modelos_disponiveis': list(MODELOS_ESTRATEGICOS.keys())
            }, status=status.HTTP_400_BAD_REQUEST)

        # Cria session_data inicial
        helena = HelenaPlanejamentoEstrategico()
        session_data = helena.inicializar_estado()

        # Gera session_id
        session_id = str(uuid.uuid4())
        session_data['session_id'] = session_id

        # Pré-configura modelo
        session_data['modelo_selecionado'] = modelo_id

        # 🔄 RESET: Zera progresso inicial
        session_data['percentual_conclusao'] = 0

        info_modelo = MODELOS_ESTRATEGICOS[modelo_id]

        # Mensagem de confirmação
        mensagem_confirmacao = f"""Você escolheu o método **{info_modelo['nome_curto']}**.

{info_modelo['descricao']}

Deseja confirmar e começar?"""

        return Response({
            'session_data': session_data,
            'mensagem_confirmacao': mensagem_confirmacao,
            'modelo_selecionado': modelo_id,
            'info_modelo': {
                'nome': info_modelo['nome_curto'],
                'nome_completo': info_modelo['nome'],
                'descricao': info_modelo['descricao'],
                'icone': info_modelo['icone']
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"[PE API] Erro ao iniciar modelo direto: {e}", exc_info=True)
        return Response({
            'erro': 'Erro ao iniciar modelo',
            'detalhes': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
def confirmar_modelo(request):
    """
    Confirma seleção de modelo e inicia agente especializado

    POST /api/planejamento-estrategico/confirmar-modelo/

    Body:
    {
        "session_data": {...}
    }

    Response:
    {
        "resposta": "Ótimo! Para começar seu OKR, qual trimestre...",
        "session_data": {...},
        "estado_atual": "construcao_modelo"
    }
    """
    try:
        session_data = request.data.get('session_data', {})

        if not session_data.get('modelo_selecionado'):
            return Response({
                'erro': 'Modelo não foi selecionado'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Força estado para construção do modelo
        from processos.domain.helena_planejamento_estrategico.schemas import EstadoPlanejamento
        session_data['estado_atual'] = EstadoPlanejamento.CONSTRUCAO_MODELO
        session_data['modo_entrada'] = 'direto'

        # 🔄 RESET: Zera progresso e estrutura para nova sessão
        session_data['estrutura_planejamento'] = {}
        session_data['percentual_conclusao'] = 0

        # Processa com agente especializado
        helena = HelenaPlanejamentoEstrategico()

        # Envia mensagem inicial ao agente (ele vai retornar a primeira pergunta)
        resposta = helena.processar("iniciar", session_data)

        return Response({
            'resposta': resposta['resposta'],
            'session_data': resposta['session_data'],
            'estado_atual': resposta['session_data'].get('estado_atual')
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"[PE API] Erro ao confirmar modelo: {e}", exc_info=True)
        return Response({
            'erro': 'Erro ao confirmar modelo',
            'detalhes': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
def calcular_recomendacao(request):
    """
    Calcula recomendação de modelo baseado em respostas

    POST /api/planejamento-estrategico/recomendar/

    Body:
    {
        "respostas": {
            "maturidade": "iniciante",
            "horizonte": "curto",
            "contexto": "execucao",
            "equipe": "pequena",
            "objetivo": "operacional"
        }
    }

    Response:
    {
        "recomendacao_principal": "okr",
        "top_3": ["okr", "5w2h", "swot"],
        "pontuacao": {...},
        "justificativa": "..."
    }
    """
    try:
        respostas = request.data.get('respostas', {})

        # Simula processamento do diagnóstico
        helena = HelenaPlanejamentoEstrategico()
        session_data = helena.inicializar_estado()
        session_data['diagnostico'] = respostas

        # Calcula pontuação
        pontuacao = {modelo: 0 for modelo in MODELOS_ESTRATEGICOS.keys()}

        for pergunta in PERGUNTAS_DIAGNOSTICO:
            resposta_valor = respostas.get(pergunta['id'])
            if resposta_valor:
                opcao = next((o for o in pergunta['opcoes'] if o['valor'] == resposta_valor), None)
                if opcao:
                    for modelo, pts in opcao['pontos'].items():
                        pontuacao[modelo] += pts

        # Ordena
        top_3 = sorted(pontuacao.items(), key=lambda x: x[1], reverse=True)[:3]
        principal = top_3[0][0]

        return Response({
            'recomendacao_principal': principal,
            'top_3': [m[0] for m in top_3],
            'pontuacao': pontuacao,
            'justificativa': MODELOS_ESTRATEGICOS[principal]['descricao']
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"[PE API] Erro ao calcular recomendação: {e}", exc_info=True)
        return Response({
            'erro': 'Erro ao calcular recomendação',
            'detalhes': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
