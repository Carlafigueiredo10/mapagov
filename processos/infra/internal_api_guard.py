"""
Guard para endpoints internos do PE.

Protege endpoints inativos com chave via header X-Internal-Key.
Fail-closed: se INTERNAL_API_KEY não está no ambiente, endpoint fica desabilitado (503).
"""
import os
import logging
from functools import wraps
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def require_internal_key(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        expected = os.environ.get('INTERNAL_API_KEY', '')

        if not expected:
            logger.warning("[PE Guard] Endpoint %s chamado mas INTERNAL_API_KEY nao configurada", request.path)
            return Response(
                {'erro': 'Endpoint desabilitado'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        provided = request.headers.get('X-Internal-Key', '')

        if not provided or provided != expected:
            logger.warning("[PE Guard] Acesso negado a %s (chave ausente ou invalida)", request.path)
            return Response(
                {'erro': 'Acesso restrito', 'detalhe': 'Endpoint interno. Requer X-Internal-Key.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        return view_func(request, *args, **kwargs)

    return wrapper
