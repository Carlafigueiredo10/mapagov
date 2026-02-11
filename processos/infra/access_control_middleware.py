"""
AccessControlMiddleware — MapaGov

Bloqueia usuarios autenticados que nao completaram verificacao de email
ou cujo acesso nao foi aprovado.

Roda APOS AuthenticationMiddleware.
Protecao real e aqui — guards do React sao apenas UX.
"""

import logging
from django.http import JsonResponse

logger = logging.getLogger('processos')

# Paths que NUNCA sao bloqueados (lista explicita, nao wildcards de CRUD)
PUBLIC_PATH_PREFIXES = (
    '/api/auth/',         # Login, registro, verificacao, reset
    '/api/catalogo/',     # Catalogo publico (somente leitura)
    '/api/stats/',        # Estatisticas publicas
    '/admin/',            # Django admin (tem sua propria autenticacao)
    '/metrics/',          # Prometheus
    '/static/',
    '/media/',
    '/assets/',
)


class AccessControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # So verificar para usuarios autenticados em paths protegidos
        if (
            request.user.is_authenticated
            and not self._is_public_path(request.path)
        ):
            profile = getattr(request.user, 'profile', None)
            if profile and not profile.can_access:
                logger.info(
                    f"Acesso bloqueado para {request.user.email}: "
                    f"email_verified={profile.email_verified}, "
                    f"access_status={profile.access_status}"
                )
                return JsonResponse({
                    'erro': 'Acesso nao autorizado.',
                    'code': 'access_denied',
                    'email_verified': profile.email_verified,
                    'access_status': profile.access_status,
                }, status=403)

        return self.get_response(request)

    def _is_public_path(self, path):
        return any(path.startswith(prefix) for prefix in PUBLIC_PATH_PREFIXES)
