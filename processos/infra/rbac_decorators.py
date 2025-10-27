"""
FASE 2 - RBAC Decorators

Decorators para verificar permissões em views Django.

Uso:
    from processos.infra.rbac_decorators import require_permission

    @require_permission('processo.criar')
    def criar_processo(request):
        # Só executado se usuário tem permissão
        ...
"""

from functools import wraps
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect
from processos.models_new.rbac import user_has_permission
from processos.models_new.orgao import Orgao
import logging

logger = logging.getLogger(__name__)


def require_permission(permission_code: str, orgao_param: str = 'orgao_id'):
    """
    Decorator para verificar permissão em uma view.

    Args:
        permission_code: Código da permissão (ex: 'processo.criar')
        orgao_param: Nome do parâmetro que contém o ID do órgão
                     Pode estar em request.GET, request.POST ou kwargs da URL

    Uso:
        @require_permission('processo.criar')
        def criar_processo(request):
            ...

        @require_permission('processo.editar', orgao_param='org_id')
        def editar_processo(request, org_id):
            ...

    Returns:
        - View original se tem permissão
        - 403 Forbidden se não tem permissão
        - 401 Unauthorized se não autenticado
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # 1. Verificar autenticação
            if not request.user.is_authenticated:
                if request.META.get('HTTP_ACCEPT', '').startswith('application/json'):
                    return JsonResponse({
                        'erro': 'Autenticação necessária'
                    }, status=401)
                return redirect('login')

            # 2. Obter Orgão
            orgao = _get_orgao_from_request(request, orgao_param, kwargs)

            if orgao is None:
                logger.warning(
                    f"Orgão não encontrado para permissão '{permission_code}'. "
                    f"User: {request.user.username}"
                )
                if request.META.get('HTTP_ACCEPT', '').startswith('application/json'):
                    return JsonResponse({
                        'erro': 'Órgão não especificado ou não encontrado'
                    }, status=400)
                return HttpResponseForbidden("Órgão não especificado")

            # 3. Verificar permissão
            has_perm = user_has_permission(request.user, permission_code, orgao)

            if not has_perm:
                logger.warning(
                    f"Permissão negada: {request.user.username} tentou "
                    f"'{permission_code}' em {orgao.sigla}"
                )

                if request.META.get('HTTP_ACCEPT', '').startswith('application/json'):
                    return JsonResponse({
                        'erro': f'Você não tem permissão para {permission_code}'
                    }, status=403)

                return HttpResponseForbidden(
                    f"Você não tem permissão para executar esta ação ({permission_code})"
                )

            # 4. Permissão OK - executar view
            return view_func(request, *args, **kwargs)

        return wrapped_view
    return decorator


def require_any_permission(*permission_codes: str):
    """
    Decorator para verificar se usuário tem QUALQUER uma das permissões.

    Uso:
        @require_any_permission('processo.editar', 'processo.visualizar')
        def ver_processo(request):
            # OK se tem editar OU visualizar
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'erro': 'Autenticação necessária'}, status=401)

            orgao = _get_orgao_from_request(request, 'orgao_id', kwargs)
            if not orgao:
                return JsonResponse({'erro': 'Órgão não encontrado'}, status=400)

            # Verificar se tem QUALQUER permissão
            has_any = any(
                user_has_permission(request.user, perm, orgao)
                for perm in permission_codes
            )

            if not has_any:
                logger.warning(
                    f"Permissão negada: {request.user.username} precisa de uma de "
                    f"{permission_codes} em {orgao.sigla}"
                )
                return JsonResponse({
                    'erro': f'Permissão insuficiente'
                }, status=403)

            return view_func(request, *args, **kwargs)

        return wrapped_view
    return decorator


def require_all_permissions(*permission_codes: str):
    """
    Decorator para verificar se usuário tem TODAS as permissões.

    Uso:
        @require_all_permissions('processo.editar', 'processo.excluir')
        def excluir_com_confirmacao(request):
            # Só OK se tem editar E excluir
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'erro': 'Autenticação necessária'}, status=401)

            orgao = _get_orgao_from_request(request, 'orgao_id', kwargs)
            if not orgao:
                return JsonResponse({'erro': 'Órgão não encontrado'}, status=400)

            # Verificar se tem TODAS as permissões
            missing_perms = [
                perm for perm in permission_codes
                if not user_has_permission(request.user, perm, orgao)
            ]

            if missing_perms:
                logger.warning(
                    f"Permissão negada: {request.user.username} está faltando "
                    f"{missing_perms} em {orgao.sigla}"
                )
                return JsonResponse({
                    'erro': f'Permissões insuficientes: faltam {missing_perms}'
                }, status=403)

            return view_func(request, *args, **kwargs)

        return wrapped_view
    return decorator


def _get_orgao_from_request(request, param_name: str, url_kwargs: dict) -> Orgao | None:
    """
    Helper para obter Orgão do request.

    Busca em (ordem):
    1. URL kwargs (ex: /api/processo/<orgao_id>/)
    2. POST data
    3. GET parameters
    4. User.orgao (se campo existe)
    5. Primeiro Orgao (fallback para testes)

    Returns:
        Instância de Orgão ou None
    """
    orgao_id = None

    # 1. URL kwargs
    if param_name in url_kwargs:
        orgao_id = url_kwargs[param_name]

    # 2. POST data
    elif request.method == 'POST' and param_name in request.POST:
        orgao_id = request.POST.get(param_name)

    # 3. GET parameters
    elif param_name in request.GET:
        orgao_id = request.GET.get(param_name)

    # 4. User.orgao
    elif hasattr(request.user, 'orgao') and request.user.orgao:
        return request.user.orgao

    # 5. Primeiro Orgao (fallback para testes - REMOVER em produção!)
    else:
        logger.warning(
            f"Orgão não especificado para {request.user.username}. "
            "Usando primeiro Orgao (apenas para testes)."
        )
        return Orgao.objects.first()

    # Buscar Orgão por ID
    if orgao_id:
        try:
            return Orgao.objects.get(id=int(orgao_id))
        except (Orgao.DoesNotExist, ValueError):
            logger.warning(f"Orgão {orgao_id} não encontrado")
            return None

    return None
