"""
FASE 3 - Structured Logging

Logs estruturados em JSON para melhor observabilidade e integração com ferramentas
de monitoramento (ELK Stack, CloudWatch, Datadog, etc.).

Benefícios:
- Logs parseáveis por máquinas
- Filtros avançados (por user_id, orgao_id, etc.)
- Integração fácil com ferramentas de observabilidade
- Rastreamento de requests (correlation_id)
- Métricas derivadas de logs
"""

import logging
import json
import time
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from django.conf import settings
import traceback


class StructuredLogger:
    """
    Logger estruturado que emite logs em formato JSON.

    Campos padrão em cada log:
    - timestamp: ISO 8601
    - level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    - message: Mensagem legível
    - correlation_id: ID para rastrear request completo
    - user_id: ID do usuário (se autenticado)
    - orgao_id: ID do órgão
    - environment: dev, staging, prod
    - service: nome do serviço
    - extras: campos adicionais
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.name = name

    def _build_log_entry(
        self,
        level: str,
        message: str,
        correlation_id: Optional[str] = None,
        user_id: Optional[int] = None,
        orgao_id: Optional[int] = None,
        duration_ms: Optional[float] = None,
        **extras
    ) -> Dict[str, Any]:
        """
        Constrói entrada de log estruturada.
        """
        entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': level,
            'message': message,
            'logger': self.name,
            'environment': getattr(settings, 'ENVIRONMENT', 'dev'),
            'service': 'mapagov',
        }

        # Adicionar contexto de request
        if correlation_id:
            entry['correlation_id'] = correlation_id

        if user_id:
            entry['user_id'] = user_id

        if orgao_id:
            entry['orgao_id'] = orgao_id

        if duration_ms is not None:
            entry['duration_ms'] = round(duration_ms, 2)

        # Adicionar extras
        if extras:
            entry['extras'] = extras

        return entry

    def debug(self, message: str, **kwargs):
        """Log nível DEBUG"""
        entry = self._build_log_entry('DEBUG', message, **kwargs)
        self.logger.debug(json.dumps(entry, ensure_ascii=False))

    def info(self, message: str, **kwargs):
        """Log nível INFO"""
        entry = self._build_log_entry('INFO', message, **kwargs)
        self.logger.info(json.dumps(entry, ensure_ascii=False))

    def warning(self, message: str, **kwargs):
        """Log nível WARNING"""
        entry = self._build_log_entry('WARNING', message, **kwargs)
        self.logger.warning(json.dumps(entry, ensure_ascii=False))

    def error(self, message: str, exception: Exception = None, **kwargs):
        """Log nível ERROR"""
        entry = self._build_log_entry('ERROR', message, **kwargs)

        # Adicionar traceback se houver exception
        if exception:
            entry['exception'] = {
                'type': type(exception).__name__,
                'message': str(exception),
                'traceback': traceback.format_exc()
            }

        self.logger.error(json.dumps(entry, ensure_ascii=False))

    def critical(self, message: str, exception: Exception = None, **kwargs):
        """Log nível CRITICAL"""
        entry = self._build_log_entry('CRITICAL', message, **kwargs)

        if exception:
            entry['exception'] = {
                'type': type(exception).__name__,
                'message': str(exception),
                'traceback': traceback.format_exc()
            }

        self.logger.critical(json.dumps(entry, ensure_ascii=False))


# ================================================
# Request Logging Middleware
# ================================================

class RequestLoggingMiddleware:
    """
    Middleware que loga todas as requisições HTTP com contexto completo.

    Gera correlation_id único por request para rastreamento end-to-end.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = StructuredLogger('mapagov.requests')

    def __call__(self, request):
        # Gerar correlation_id único
        correlation_id = str(uuid.uuid4())
        request.correlation_id = correlation_id

        # Timestamp de início
        start_time = time.time()

        # Processar request
        response = self.get_response(request)

        # Calcular duração
        duration_ms = (time.time() - start_time) * 1000

        # Extrair informações do request
        user_id = request.user.id if request.user.is_authenticated else None
        orgao_id = None
        if hasattr(request.user, 'orgao') and request.user.orgao:
            orgao_id = request.user.orgao.id

        # Log da requisição
        self.logger.info(
            f"{request.method} {request.path} → {response.status_code}",
            correlation_id=correlation_id,
            user_id=user_id,
            orgao_id=orgao_id,
            duration_ms=duration_ms,
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            ip_address=self._get_client_ip(request),
            query_params=dict(request.GET) if request.GET else None,
        )

        # Adicionar correlation_id no response header
        response['X-Correlation-ID'] = correlation_id

        return response

    def _get_client_ip(self, request) -> str:
        """Obtém IP do cliente (suporta proxies)"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('HTTP_X_REAL_IP')
            if not ip:
                ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip


# ================================================
# Database Query Logging
# ================================================

class DatabaseQueryLogger:
    """
    Logger para queries lentas do banco de dados.

    Identifica queries que precisam de otimização.
    """

    def __init__(self, slow_threshold_ms: float = 100):
        """
        Args:
            slow_threshold_ms: Queries acima deste tempo são consideradas lentas
        """
        self.slow_threshold_ms = slow_threshold_ms
        self.logger = StructuredLogger('mapagov.database')

    def log_query(
        self,
        sql: str,
        duration_ms: float,
        correlation_id: Optional[str] = None
    ):
        """
        Loga query se for lenta.
        """
        if duration_ms >= self.slow_threshold_ms:
            self.logger.warning(
                f"Slow query detected: {duration_ms:.2f}ms",
                correlation_id=correlation_id,
                duration_ms=duration_ms,
                sql=sql[:500],  # Limitar tamanho do SQL no log
                slow_query=True
            )


# ================================================
# Business Event Logging
# ================================================

class BusinessEventLogger:
    """
    Logger para eventos de negócio importantes.

    Exemplos:
    - Processo criado
    - POP gerado
    - Usuário criou conta
    - Análise de riscos finalizada
    """

    def __init__(self):
        self.logger = StructuredLogger('mapagov.business_events')

    def log_event(
        self,
        event_type: str,
        description: str,
        user_id: Optional[int] = None,
        orgao_id: Optional[int] = None,
        correlation_id: Optional[str] = None,
        **metadata
    ):
        """
        Registra evento de negócio.

        Args:
            event_type: Tipo do evento (processo_criado, pop_gerado, etc.)
            description: Descrição legível
            metadata: Dados adicionais do evento
        """
        self.logger.info(
            description,
            correlation_id=correlation_id,
            user_id=user_id,
            orgao_id=orgao_id,
            event_type=event_type,
            **metadata
        )


# ================================================
# Helpers para obter logger
# ================================================

def get_logger(name: str) -> StructuredLogger:
    """
    Factory para obter logger estruturado.

    Uso:
        from processos.infra.structured_logging import get_logger

        logger = get_logger(__name__)
        logger.info("Processo criado", processo_id=123, user_id=456)
    """
    return StructuredLogger(name)


# ================================================
# Context Manager para rastreamento
# ================================================

class LogContext:
    """
    Context manager para adicionar contexto a todos os logs dentro do bloco.

    Uso:
        with LogContext(correlation_id=req.correlation_id, user_id=user.id):
            # Todos os logs aqui terão correlation_id e user_id
            logger.info("Processando...")
            ...
    """

    _context = {}

    def __init__(self, **kwargs):
        self.context = kwargs

    def __enter__(self):
        LogContext._context.update(self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key in self.context:
            LogContext._context.pop(key, None)

    @classmethod
    def get_context(cls) -> Dict[str, Any]:
        """Retorna contexto atual"""
        return cls._context.copy()


# ================================================
# Performance Tracking Decorator
# ================================================

def track_performance(event_type: str):
    """
    Decorator para rastrear performance de funções.

    Uso:
        @track_performance('processo_criar')
        def criar_processo(request):
            ...
            # Automaticamente loga duração
    """
    def decorator(func):
        from functools import wraps

        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                logger.info(
                    f"{event_type} completed successfully",
                    duration_ms=duration_ms,
                    event_type=event_type,
                    function=func.__name__,
                    success=True
                )

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                logger.error(
                    f"{event_type} failed",
                    exception=e,
                    duration_ms=duration_ms,
                    event_type=event_type,
                    function=func.__name__,
                    success=False
                )

                raise

        return wrapper
    return decorator


# ======================================================================
# PATCH v3 - Corrigir encoding de logs no Windows (emojis, símbolos, acentos)
# ======================================================================

import sys
import unicodedata

class SafeUTF8Filter(logging.Filter):
    """Remove caracteres não suportados por CP1252 e normaliza logs."""
    def filter(self, record):
        try:
            # Normaliza acentos e remove qualquer caractere não-ASCII
            safe_msg = unicodedata.normalize("NFKD", str(record.msg))
            safe_msg = safe_msg.encode("ascii", "ignore").decode("ascii")
            record.msg = safe_msg
        except Exception:
            record.msg = str(record.msg)
        return True

if sys.platform.startswith('win'):
    logging.getLogger().addFilter(SafeUTF8Filter())
    print("[LOGGING] SafeUTF8Filter ativo — logs normalizados para CP1252 (sem emojis/simbolos Unicode)")
