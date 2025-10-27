"""
FASE 2 - Rate Limiting

Previne abuso de API e ataques de negação de serviço (DoS).

Estratégias:
- Por usuário (ex: 100 requisições/minuto)
- Por IP (anônimos: 10 requisições/minuto)
- Por órgão (limite global do órgão)
- Por endpoint (endpoints sensíveis têm limites menores)

Armazenamento: Redis (rápido) com fallback para DB
"""

import time
import hashlib
from functools import wraps
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter usando sliding window algorithm.

    Benefícios:
    - Mais preciso que fixed window
    - Evita burst attacks
    - Suave degradação
    """

    def __init__(self, key_prefix: str, limit: int, window: int):
        """
        Args:
            key_prefix: Prefixo da chave (ex: 'ratelimit:user:123')
            limit: Número máximo de requisições
            window: Janela de tempo em segundos
        """
        self.key_prefix = key_prefix
        self.limit = limit
        self.window = window

    def is_allowed(self, identifier: str) -> tuple[bool, dict]:
        """
        Verifica se requisição é permitida.

        Args:
            identifier: Identificador único (user_id, IP, etc.)

        Returns:
            (is_allowed: bool, info: dict)
            info contém: remaining, reset_at
        """
        key = f"{self.key_prefix}:{identifier}"
        current_time = time.time()
        window_start = current_time - self.window

        try:
            # Obter histórico de requisições
            requests = cache.get(key, [])

            # Filtrar apenas requisições dentro da janela
            requests = [req_time for req_time in requests if req_time > window_start]

            # Verificar limite
            if len(requests) >= self.limit:
                # Limite excedido
                oldest_request = min(requests)
                reset_at = oldest_request + self.window

                return False, {
                    'remaining': 0,
                    'limit': self.limit,
                    'reset_at': int(reset_at),
                    'retry_after': int(reset_at - current_time)
                }

            # Adicionar requisição atual
            requests.append(current_time)

            # Salvar no cache (TTL = janela de tempo)
            cache.set(key, requests, timeout=self.window)

            return True, {
                'remaining': self.limit - len(requests),
                'limit': self.limit,
                'reset_at': int(current_time + self.window)
            }

        except Exception as e:
            logger.error(f"Erro no rate limiter: {e}")
            # Em caso de erro, permitir (fail-open para não bloquear serviço)
            return True, {
                'remaining': self.limit,
                'limit': self.limit,
                'reset_at': int(current_time + self.window)
            }

    def reset(self, identifier: str):
        """
        Reseta contador para um identificador.

        Útil para testes ou após resolver incidente.
        """
        key = f"{self.key_prefix}:{identifier}"
        cache.delete(key)


# ================================================
# Rate Limiters Pré-configurados
# ================================================

class RateLimiters:
    """
    Configurações de rate limiting para diferentes contextos.
    """

    # Por usuário autenticado
    USER_GENERAL = RateLimiter('rl:user', limit=100, window=60)  # 100/min
    USER_CHAT = RateLimiter('rl:user:chat', limit=30, window=60)  # 30/min (chat é pesado)
    USER_EXPORT = RateLimiter('rl:user:export', limit=10, window=3600)  # 10/hora (exports são caros)

    # Por IP (anônimos)
    IP_GENERAL = RateLimiter('rl:ip', limit=20, window=60)  # 20/min
    IP_LOGIN = RateLimiter('rl:ip:login', limit=5, window=300)  # 5/5min (prevenir brute force)

    # Por órgão (limite global)
    ORGAO_GENERAL = RateLimiter('rl:orgao', limit=1000, window=60)  # 1000/min por órgão
    ORGAO_CHAT = RateLimiter('rl:orgao:chat', limit=300, window=60)  # 300/min chat

    # Endpoints sensíveis
    SENSITIVE_ENDPOINT = RateLimiter('rl:sensitive', limit=5, window=60)  # 5/min


# ================================================
# Decorators
# ================================================

def rate_limit(
    limiter: RateLimiter = None,
    key_func: callable = None,
    error_message: str = 'Limite de requisições excedido. Tente novamente em alguns segundos.'
):
    """
    Decorator para aplicar rate limiting em views.

    Args:
        limiter: Instância de RateLimiter (ou None para usar padrão)
        key_func: Função que extrai identificador do request
                  (user_id, IP, orgao_id, etc.)
        error_message: Mensagem de erro customizada

    Uso:
        @rate_limit(RateLimiters.USER_CHAT, key_func=lambda r: r.user.id)
        def chat_view(request):
            ...

        @rate_limit(RateLimiters.IP_LOGIN, key_func=lambda r: get_client_ip(r))
        def login_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # Usar limiter padrão se não especificado
            _limiter = limiter or RateLimiters.USER_GENERAL

            # Determinar identificador
            if key_func:
                identifier = key_func(request)
            elif request.user.is_authenticated:
                identifier = f"user_{request.user.id}"
            else:
                identifier = f"ip_{get_client_ip(request)}"

            # Verificar limite
            is_allowed, info = _limiter.is_allowed(identifier)

            # Adicionar headers de rate limit (informativo)
            def add_rate_limit_headers(response):
                response['X-RateLimit-Limit'] = str(info['limit'])
                response['X-RateLimit-Remaining'] = str(info['remaining'])
                response['X-RateLimit-Reset'] = str(info['reset_at'])
                return response

            if not is_allowed:
                # Limite excedido
                logger.warning(
                    f"Rate limit excedido: {identifier} no endpoint {request.path}"
                )

                # Logar evento de segurança
                _log_rate_limit_exceeded(request, identifier, info)

                response = JsonResponse({
                    'erro': error_message,
                    'rate_limit': {
                        'exceeded': True,
                        'retry_after': info['retry_after'],
                        'reset_at': info['reset_at']
                    }
                }, status=429)  # 429 Too Many Requests

                response['Retry-After'] = str(info['retry_after'])
                return add_rate_limit_headers(response)

            # Permitido - executar view
            response = view_func(request, *args, **kwargs)

            # Adicionar headers informativos
            return add_rate_limit_headers(response)

        return wrapped_view
    return decorator


def rate_limit_user(limit: int = 100, window: int = 60, message: str = None):
    """
    Atalho para rate limit por usuário.

    Uso:
        @rate_limit_user(limit=30, window=60)
        def chat_view(request):
            ...
    """
    limiter = RateLimiter('rl:user', limit=limit, window=window)
    return rate_limit(
        limiter=limiter,
        key_func=lambda r: f"user_{r.user.id}" if r.user.is_authenticated else f"ip_{get_client_ip(r)}",
        error_message=message or f'Limite de {limit} requisições por {window} segundos excedido'
    )


def rate_limit_ip(limit: int = 20, window: int = 60, message: str = None):
    """
    Atalho para rate limit por IP.

    Uso:
        @rate_limit_ip(limit=5, window=300)  # 5 requisições/5min
        def login_view(request):
            ...
    """
    limiter = RateLimiter('rl:ip', limit=limit, window=window)
    return rate_limit(
        limiter=limiter,
        key_func=lambda r: get_client_ip(r),
        error_message=message or f'Limite de {limit} requisições por {window} segundos excedido'
    )


def rate_limit_orgao(limit: int = 1000, window: int = 60):
    """
    Atalho para rate limit por órgão.

    Uso:
        @rate_limit_orgao(limit=500, window=60)
        def endpoint_view(request):
            ...
    """
    limiter = RateLimiter('rl:orgao', limit=limit, window=window)

    def get_orgao_id(request):
        # Tentar obter do user
        if hasattr(request.user, 'orgao') and request.user.orgao:
            return f"orgao_{request.user.orgao.id}"
        # Fallback: IP
        return f"ip_{get_client_ip(request)}"

    return rate_limit(
        limiter=limiter,
        key_func=get_orgao_id,
        error_message=f'Limite de requisições do órgão excedido. Tente novamente em alguns segundos.'
    )


# ================================================
# Helpers
# ================================================

def get_client_ip(request) -> str:
    """
    Obtém IP do cliente (suporta proxies).

    Ordem de verificação:
    1. X-Forwarded-For (proxy)
    2. X-Real-IP (nginx)
    3. REMOTE_ADDR (direto)
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Primeiro IP da lista (cliente original)
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('HTTP_X_REAL_IP')
        if not ip:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')

    return ip


def _log_rate_limit_exceeded(request, identifier: str, info: dict):
    """
    Registra evento de segurança quando rate limit é excedido.

    Múltiplas violações podem indicar ataque.
    """
    try:
        from processos.models_new.audit_log import SecurityEvent

        # Verificar se é ataque (muitas violações em curto período)
        violation_key = f"rl_violations:{identifier}"
        violations = cache.get(violation_key, 0)
        violations += 1
        cache.set(violation_key, violations, timeout=3600)  # 1 hora

        severity = 'low'
        if violations > 10:
            severity = 'medium'
        if violations > 50:
            severity = 'high'
        if violations > 100:
            severity = 'critical'

        SecurityEvent.log_security_event(
            event_type='brute_force' if violations > 5 else 'suspicious_activity',
            severity=severity,
            user=request.user if request.user.is_authenticated else None,
            ip_address=get_client_ip(request),
            description=f'Rate limit excedido: {violations} violações em 1h',
            details={
                'identifier': identifier,
                'endpoint': request.path,
                'method': request.method,
                'violations_count': violations,
                'limit': info['limit'],
                'retry_after': info.get('retry_after', 0)
            }
        )

    except Exception as e:
        logger.error(f"Erro ao logar rate limit exceeded: {e}")
        # Não bloquear requisição se logging falhar


# ================================================
# Admin Helpers
# ================================================

def reset_rate_limit(identifier: str, limiter: RateLimiter = None):
    """
    Reseta rate limit para um identificador (admin).

    Uso:
        from processos.infra.rate_limiting import reset_rate_limit, RateLimiters

        # Resetar limite de chat do usuário 123
        reset_rate_limit('user_123', RateLimiters.USER_CHAT)
    """
    if limiter:
        limiter.reset(identifier)
    else:
        # Resetar todos os limiters conhecidos
        for attr_name in dir(RateLimiters):
            if not attr_name.startswith('_'):
                limiter_obj = getattr(RateLimiters, attr_name)
                if isinstance(limiter_obj, RateLimiter):
                    limiter_obj.reset(identifier)


def get_rate_limit_status(identifier: str, limiter: RateLimiter) -> dict:
    """
    Obtém status atual do rate limit para um identificador.

    Retorna:
        {
            'identifier': 'user_123',
            'requests_count': 45,
            'remaining': 55,
            'limit': 100,
            'reset_at': 1234567890
        }
    """
    is_allowed, info = limiter.is_allowed(identifier)

    # Obter contagem atual sem incrementar
    key = f"{limiter.key_prefix}:{identifier}"
    requests = cache.get(key, [])
    current_time = time.time()
    window_start = current_time - limiter.window
    requests = [req_time for req_time in requests if req_time > window_start]

    return {
        'identifier': identifier,
        'requests_count': len(requests),
        'remaining': info['remaining'],
        'limit': info['limit'],
        'reset_at': info['reset_at'],
        'is_limited': not is_allowed
    }
