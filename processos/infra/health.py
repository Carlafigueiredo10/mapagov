"""Health check endpoint para Cloud Run / Kubernetes."""

import logging
from django.http import JsonResponse
from django.db import connection

logger = logging.getLogger(__name__)


def health_check(request):
    """
    GET /api/health/
    Retorna status do sistema. Checa conectividade com o banco.
    """
    db_ok = False
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_ok = True
    except Exception:
        logger.warning("[HEALTH] Falha na conexão com o banco de dados")

    status = "ok" if db_ok else "degraded"
    status_code = 200 if db_ok else 503

    return JsonResponse({
        "status": status,
        "database": "ok" if db_ok else "unavailable",
    }, status=status_code)
