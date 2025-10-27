"""
FASE 3 - Prometheus Metrics

Métricas para monitoramento e observabilidade usando Prometheus.

Tipos de métricas:
- Counter: Contador incremental (requisições totais, erros, etc.)
- Gauge: Valor que pode subir e descer (usuários ativos, sessões ativas)
- Histogram: Distribuição de valores (latência, tamanho de resposta)
- Summary: Quantis de valores (p50, p95, p99)

Dashboard recomendado: Grafana
"""

from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from django.http import HttpResponse
import time
from functools import wraps
from typing import Optional


# ================================================
# Registry Global
# ================================================

# Registry customizado (permite múltiplos em testes)
registry = CollectorRegistry()


# ================================================
# HTTP Metrics
# ================================================

# Counter: Total de requisições HTTP
http_requests_total = Counter(
    'mapagov_http_requests_total',
    'Total de requisições HTTP recebidas',
    ['method', 'endpoint', 'status_code'],
    registry=registry
)

# Histogram: Latência de requisições HTTP
http_request_duration_seconds = Histogram(
    'mapagov_http_request_duration_seconds',
    'Duração de requisições HTTP em segundos',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0),  # Buckets em segundos
    registry=registry
)

# Counter: Erros HTTP (4xx, 5xx)
http_errors_total = Counter(
    'mapagov_http_errors_total',
    'Total de erros HTTP',
    ['method', 'endpoint', 'status_code', 'error_type'],
    registry=registry
)


# ================================================
# Database Metrics
# ================================================

# Counter: Total de queries executadas
db_queries_total = Counter(
    'mapagov_db_queries_total',
    'Total de queries ao banco de dados',
    ['operation'],  # SELECT, INSERT, UPDATE, DELETE
    registry=registry
)

# Histogram: Duração de queries
db_query_duration_seconds = Histogram(
    'mapagov_db_query_duration_seconds',
    'Duração de queries ao banco em segundos',
    ['operation'],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0),
    registry=registry
)

# Counter: Queries lentas (> 100ms)
db_slow_queries_total = Counter(
    'mapagov_db_slow_queries_total',
    'Total de queries lentas (>100ms)',
    registry=registry
)


# ================================================
# Business Metrics
# ================================================

# Counter: Processos criados
processos_criados_total = Counter(
    'mapagov_processos_criados_total',
    'Total de processos criados',
    ['orgao'],
    registry=registry
)

# Counter: POPs gerados
pops_gerados_total = Counter(
    'mapagov_pops_gerados_total',
    'Total de POPs gerados',
    ['orgao'],
    registry=registry
)

# Counter: Chat messages enviadas
chat_messages_total = Counter(
    'mapagov_chat_messages_total',
    'Total de mensagens de chat',
    ['role', 'produto'],  # role: user/assistant, produto: etapas/pop/etc
    registry=registry
)

# Gauge: Sessões ativas
sessions_active = Gauge(
    'mapagov_sessions_active',
    'Número de sessões ativas no momento',
    registry=registry
)

# Gauge: Usuários ativos (últimas 24h)
users_active_24h = Gauge(
    'mapagov_users_active_24h',
    'Usuários ativos nas últimas 24 horas',
    registry=registry
)


# ================================================
# Cache Metrics
# ================================================

# Counter: Cache hits
cache_hits_total = Counter(
    'mapagov_cache_hits_total',
    'Total de cache hits',
    ['cache_type'],  # redis, locmem
    registry=registry
)

# Counter: Cache misses
cache_misses_total = Counter(
    'mapagov_cache_misses_total',
    'Total de cache misses',
    ['cache_type'],
    registry=registry
)

# Gauge: Taxa de cache hit
cache_hit_rate = Gauge(
    'mapagov_cache_hit_rate',
    'Taxa de acerto do cache (0-1)',
    ['cache_type'],
    registry=registry
)


# ================================================
# Security Metrics
# ================================================

# Counter: Tentativas de login
login_attempts_total = Counter(
    'mapagov_login_attempts_total',
    'Total de tentativas de login',
    ['status'],  # success, failed
    registry=registry
)

# Counter: Rate limit exceeded
rate_limit_exceeded_total = Counter(
    'mapagov_rate_limit_exceeded_total',
    'Total de vezes que rate limit foi excedido',
    ['limiter_type'],  # user, ip, orgao
    registry=registry
)

# Counter: Violações de permissão
permission_denied_total = Counter(
    'mapagov_permission_denied_total',
    'Total de acessos negados por falta de permissão',
    ['resource', 'action'],
    registry=registry
)

# Counter: Eventos de segurança
security_events_total = Counter(
    'mapagov_security_events_total',
    'Total de eventos de segurança',
    ['event_type', 'severity'],
    registry=registry
)


# ================================================
# System Metrics
# ================================================

# Gauge: Memória usada (bytes)
memory_usage_bytes = Gauge(
    'mapagov_memory_usage_bytes',
    'Memória usada pelo processo em bytes',
    registry=registry
)

# Gauge: CPU usage (%)
cpu_usage_percent = Gauge(
    'mapagov_cpu_usage_percent',
    'Uso de CPU em porcentagem',
    registry=registry
)


# ================================================
# Middleware para métricas HTTP
# ================================================

class PrometheusMetricsMiddleware:
    """
    Middleware que coleta métricas HTTP automaticamente.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ignorar endpoint de métricas (evitar recursão)
        if request.path == '/metrics':
            return self.get_response(request)

        # Timestamp de início
        start_time = time.time()

        # Processar request
        response = self.get_response(request)

        # Calcular duração
        duration = time.time() - start_time

        # Extrair informações
        method = request.method
        endpoint = self._normalize_path(request.path)
        status_code = response.status_code

        # Incrementar counter de requisições
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()

        # Registrar latência
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

        # Registrar erros (4xx e 5xx)
        if status_code >= 400:
            error_type = 'client_error' if status_code < 500 else 'server_error'
            http_errors_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                error_type=error_type
            ).inc()

        return response

    def _normalize_path(self, path: str) -> str:
        """
        Normaliza path para agrupar rotas dinâmicas.

        Exemplos:
        /api/chat-v2/sessao/123/ → /api/chat-v2/sessao/:id/
        /processos/456/editar/ → /processos/:id/editar/
        """
        # TODO: Implementar regex para normalização de IDs
        # Por enquanto, retornar path completo
        # (em produção, substituir UUIDs e IDs por :id)
        return path


# ================================================
# View para endpoint /metrics
# ================================================

def metrics_view(request):
    """
    Endpoint que expõe métricas para o Prometheus scraper.

    GET /metrics

    Configuração no prometheus.yml:
    ```yaml
    scrape_configs:
      - job_name: 'mapagov'
        static_configs:
          - targets: ['localhost:8000']
        metrics_path: '/metrics'
        scrape_interval: 15s
    ```
    """
    metrics_output = generate_latest(registry)
    return HttpResponse(
        metrics_output,
        content_type=CONTENT_TYPE_LATEST
    )


# ================================================
# Decorators para métricas de negócio
# ================================================

def track_business_event(metric: Counter):
    """
    Decorator para rastrear eventos de negócio.

    Uso:
        @track_business_event(processos_criados_total)
        def criar_processo(request, orgao):
            ...
            # Automaticamente incrementa processos_criados_total
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Tentar extrair orgao dos kwargs ou result
            orgao = kwargs.get('orgao')
            if orgao and hasattr(orgao, 'sigla'):
                metric.labels(orgao=orgao.sigla).inc()
            else:
                metric.labels(orgao='unknown').inc()

            return result
        return wrapper
    return decorator


def track_chat_message(role: str, produto: str):
    """
    Decorator para rastrear mensagens de chat.

    Uso:
        @track_chat_message(role='user', produto='etapas')
        def processar_mensagem_usuario(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            chat_messages_total.labels(role=role, produto=produto).inc()
            return result
        return wrapper
    return decorator


# ================================================
# Helpers para atualizar gauges
# ================================================

def update_sessions_active_count():
    """
    Atualiza gauge de sessões ativas.

    Deve ser chamado periodicamente (ex: via Celery task a cada minuto).
    """
    from processos.models_new.chat_session import ChatSession
    from django.utils import timezone
    from datetime import timedelta

    # Considerar ativa se atualizada nas últimas 15 minutos
    cutoff = timezone.now() - timedelta(minutes=15)
    count = ChatSession.objects.filter(
        atualizado_em__gte=cutoff,
        status='ativa'
    ).count()

    sessions_active.set(count)


def update_users_active_24h_count():
    """
    Atualiza gauge de usuários ativos nas últimas 24h.
    """
    from processos.models_new.audit_log import AuditLog
    from django.utils import timezone
    from datetime import timedelta

    cutoff = timezone.now() - timedelta(hours=24)
    count = AuditLog.objects.filter(
        timestamp__gte=cutoff
    ).values('user_id').distinct().count()

    users_active_24h.set(count)


def update_system_metrics():
    """
    Atualiza métricas de sistema (memória, CPU).

    Requer psutil: pip install psutil
    """
    try:
        import psutil
        import os

        process = psutil.Process(os.getpid())

        # Memória
        mem_info = process.memory_info()
        memory_usage_bytes.set(mem_info.rss)  # Resident Set Size

        # CPU (% nos últimos segundos)
        cpu_percent = process.cpu_percent(interval=1.0)
        cpu_usage_percent.set(cpu_percent)

    except ImportError:
        # psutil não instalado
        pass
    except Exception as e:
        # Erro ao coletar métricas
        from processos.infra.structured_logging import get_logger
        logger = get_logger(__name__)
        logger.warning("Erro ao coletar métricas de sistema", exception=e)


# ================================================
# Task Celery para atualizar métricas periodicamente
# ================================================

# Descomentar quando tiver Celery configurado
# from celery import shared_task
#
# @shared_task
# def update_all_metrics():
#     """
#     Task Celery que atualiza todas as métricas periodicamente.
#
#     Configurar no celerybeat:
#     CELERY_BEAT_SCHEDULE = {
#         'update-metrics': {
#             'task': 'processos.infra.metrics.update_all_metrics',
#             'schedule': 60.0,  # A cada 60 segundos
#         },
#     }
#     """
#     update_sessions_active_count()
#     update_users_active_24h_count()
#     update_system_metrics()
