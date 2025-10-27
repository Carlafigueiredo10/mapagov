"""
Redis Cache - Gerenciamento de cache com Redis

Responsável por:
- Cache de sessões (TTL 15min)
- Fallback gracioso se Redis indisponível
- Contadores (mensagens por sessão)
"""
import redis
import json
import logging
from typing import Optional, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class RedisSessionCache:
    """
    Cliente Redis para cache de sessões de chat.

    Estratégia:
    - TTL padrão: 900s (15 minutos)
    - Modo degradado: retorna None se Redis indisponível
    - Keys: session:{session_id}, session:{session_id}:msg_count
    """

    def __init__(self):
        """
        Inicializa cliente Redis.

        Configuração via settings:
        - REDIS_HOST (default: localhost)
        - REDIS_PORT (default: 6379)
        - REDIS_DB (default: 0)
        """
        try:
            self.client = redis.Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                db=getattr(settings, 'REDIS_DB', 0),
                decode_responses=True,
                socket_connect_timeout=5,  # Timeout para não travar
                socket_timeout=5,
                retry_on_timeout=True
            )
            self.ttl = 900  # 15 minutos
            self.available = self._check_connection()
        except Exception as e:
            logger.warning(f"Redis indisponível: {e}. Modo degradado ativado.")
            self.client = None
            self.available = False

    def _check_connection(self) -> bool:
        """Verifica se Redis está acessível"""
        try:
            if self.client:
                self.client.ping()
                return True
        except Exception as e:
            logger.warning(f"Redis ping falhou: {e}")
        return False

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca sessão no cache.

        Args:
            session_id: UUID da sessão

        Returns:
            dict com dados da sessão ou None se não encontrado/erro
        """
        if not self.available:
            return None

        try:
            key = f'session:{session_id}'
            data = self.client.get(key)
            if data:
                logger.debug(f"Cache HIT: {session_id}")
                return json.loads(data)
            logger.debug(f"Cache MISS: {session_id}")
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar sessão no Redis: {e}")
            return None

    def set_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Salva sessão no cache.

        Args:
            session_id: UUID da sessão
            data: Dados da sessão (será serializado para JSON)

        Returns:
            bool: True se salvou com sucesso
        """
        if not self.available:
            return False

        try:
            key = f'session:{session_id}'
            self.client.setex(
                key,
                self.ttl,
                json.dumps(data, default=str)  # default=str para serializar UUIDs
            )
            logger.debug(f"Cache SET: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar sessão no Redis: {e}")
            return False

    def delete_session(self, session_id: str) -> bool:
        """
        Remove sessão do cache.

        Args:
            session_id: UUID da sessão

        Returns:
            bool: True se removeu com sucesso
        """
        if not self.available:
            return False

        try:
            key = f'session:{session_id}'
            self.client.delete(key)
            logger.debug(f"Cache DELETE: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar sessão no Redis: {e}")
            return False

    def increment_message_count(self, session_id: str) -> int:
        """
        Incrementa contador de mensagens da sessão.

        Usado para decidir quando sincronizar com DB.

        Args:
            session_id: UUID da sessão

        Returns:
            int: Total de mensagens ou 0 se erro
        """
        if not self.available:
            return 0

        try:
            key = f'session:{session_id}:msg_count'
            count = self.client.incr(key)
            self.client.expire(key, self.ttl)
            return count
        except Exception as e:
            logger.error(f"Erro ao incrementar contador: {e}")
            return 0

    def get_message_count(self, session_id: str) -> int:
        """
        Retorna contador de mensagens da sessão.

        Args:
            session_id: UUID da sessão

        Returns:
            int: Total de mensagens ou 0 se erro
        """
        if not self.available:
            return 0

        try:
            key = f'session:{session_id}:msg_count'
            count = self.client.get(key)
            return int(count) if count else 0
        except Exception as e:
            logger.error(f"Erro ao buscar contador: {e}")
            return 0

    def clear_all_sessions(self) -> int:
        """
        Limpa todas as sessões do cache (usar com cuidado).

        Returns:
            int: Quantidade de chaves removidas
        """
        if not self.available:
            return 0

        try:
            keys = self.client.keys('session:*')
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return 0

    def health_check(self) -> Dict[str, Any]:
        """
        Verifica saúde do Redis.

        Returns:
            dict: Status e métricas
        """
        if not self.available:
            return {
                'status': 'unhealthy',
                'available': False,
                'error': 'Redis não disponível'
            }

        try:
            info = self.client.info()
            return {
                'status': 'healthy',
                'available': True,
                'connected_clients': info.get('connected_clients'),
                'used_memory_human': info.get('used_memory_human'),
                'uptime_in_days': info.get('uptime_in_days'),
            }
        except Exception as e:
            return {
                'status': 'error',
                'available': False,
                'error': str(e)
            }
