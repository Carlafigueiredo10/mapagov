"""
Session Manager - Gerenciamento de Sessões de Chat

Responsável por:
- Get/Create sessões (Redis → DB fallback)
- Salvar mensagens (idempotência via req_uuid)
- Sincronização híbrida (Redis + PostgreSQL)
"""
import uuid
import logging
from typing import Optional, Dict, Any
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from processos.models_new.orgao import Orgao
from processos.models_new.chat_session import ChatSession
from processos.models_new.chat_message import ChatMessage
from processos.infra.redis_cache import RedisSessionCache

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Gerencia sessões de chat com estratégia híbrida Redis + PostgreSQL.

    Fluxo:
    1. Request chega → busca Redis (rápido)
    2. Se Redis miss → busca PostgreSQL
    3. Processa mensagem → salva no DB (sempre)
    4. Atualiza Redis (cache)
    5. A cada N mensagens → força sync DB

    Vantagens:
    - Performance: Redis para leituras frequentes
    - Durabilidade: PostgreSQL nunca perde dados
    - Resilience: Se Redis cair, continua funcionando
    """

    SYNC_EVERY_N_MESSAGES = 5  # Sincroniza estado com DB a cada 5 mensagens

    def __init__(self):
        """Inicializa com cache Redis"""
        self.cache = RedisSessionCache()

    def get_or_create_session(
        self,
        session_id: str,
        user: User,
        orgao: Optional[Orgao] = None
    ) -> ChatSession:
        """
        Busca ou cria sessão.

        Estratégia:
        1. Tenta cache Redis
        2. Se miss, busca PostgreSQL
        3. Se não existe, cria nova
        4. Cacheia resultado

        Args:
            session_id: UUID da sessão (string)
            user: Usuário Django autenticado
            orgao: Órgão (se None, pega do user.orgao)

        Returns:
            ChatSession: Instância da sessão

        Raises:
            ValueError: Se user sem órgão e orgao não fornecido
        """
        # 1. Tenta Redis
        cached_data = self.cache.get_session(session_id)
        if cached_data:
            logger.debug(f"Sessão {session_id} vinda do cache Redis")
            try:
                return ChatSession.objects.get(session_id=session_id)
            except ChatSession.DoesNotExist:
                # Cache inconsistente - limpa e recria
                logger.warning(f"Cache inconsistente para {session_id}. Limpando...")
                self.cache.delete_session(session_id)

        # 2. Busca ou cria no PostgreSQL
        if orgao is None:
            # Tenta pegar órgão do user (se tiver)
            if hasattr(user, 'orgao') and user.orgao is not None:
                orgao = user.orgao
            else:
                # Fallback: pega primeiro órgão (temporário para testes)
                orgao = Orgao.objects.first()
                if not orgao:
                    raise ValueError(
                        f"Usuário {user.username} não possui órgão associado "
                        "e não há órgãos cadastrados no sistema"
                    )

        session, created = ChatSession.objects.get_or_create(
            session_id=session_id,
            defaults={
                'user': user,
                'orgao': orgao,
                'contexto_atual': 'pop',  # Contexto padrão - Helena POP primeiro
            }
        )

        if created:
            logger.info(f"Nova sessão criada: {session_id} (user={user.username}, orgao={orgao.sigla})")
        else:
            logger.debug(f"Sessão existente recuperada: {session_id}")

        # 3. Cacheia no Redis
        self.cache.set_session(session_id, session.to_dict())

        return session

    def save_message(
        self,
        session: ChatSession,
        role: str,
        content: str,
        req_uuid: Optional[str] = None,
        contexto: Optional[str] = None,
        metadados: Optional[Dict[str, Any]] = None
    ) -> tuple[ChatMessage, bool]:
        """
        Salva mensagem com idempotência.

        Args:
            session: Sessão de chat
            role: 'user', 'assistant' ou 'system'
            content: Texto da mensagem
            req_uuid: UUID do request (garante idempotência). Se None, gera novo.
            contexto: Contexto atual (se None, usa session.contexto_atual)
            metadados: Dados extras (tokens, latência, etc.)

        Returns:
            tuple: (ChatMessage, created) onde created indica se foi inserido (False = duplicata)

        Raises:
            ValueError: Se role inválido
        """
        if role not in ['user', 'assistant', 'system']:
            raise ValueError(f"Role inválido: {role}. Permitidos: user, assistant, system")

        if req_uuid is None:
            req_uuid = str(uuid.uuid4())

        if contexto is None:
            contexto = session.contexto_atual

        if metadados is None:
            metadados = {}

        # Idempotência: tenta criar, se já existe ignora
        try:
            with transaction.atomic():
                message, created = ChatMessage.objects.get_or_create(
                    req_uuid=req_uuid,
                    defaults={
                        'session': session,
                        'user': session.user,
                        'role': role,
                        'content': content,
                        'contexto': contexto,
                        'metadados': metadados,
                    }
                )

                if created:
                    logger.debug(f"Mensagem salva: {role} ({len(content)} chars)")
                else:
                    logger.warning(f"Mensagem duplicada ignorada: req_uuid={req_uuid}")

                return message, created

        except IntegrityError as e:
            # Constraint violation - requisição duplicada
            logger.warning(f"IntegrityError ao salvar mensagem (retry detectado): {e}")
            existing = ChatMessage.objects.get(req_uuid=req_uuid)
            return existing, False

    def update_session_state(
        self,
        session: ChatSession,
        contexto: Optional[str] = None,
        estados: Optional[Dict[str, Any]] = None,
        agent_version: Optional[tuple[str, str]] = None
    ) -> None:
        """
        Atualiza estado da sessão.

        Args:
            session: Sessão a atualizar
            contexto: Novo contexto (se mudar)
            estados: Novos estados dos agentes
            agent_version: tuple (agente_nome, versão) para atualizar
        """
        updated = False

        if contexto and contexto != session.contexto_atual:
            session.contexto_atual = contexto
            updated = True

        if estados:
            session.estados.update(estados)
            updated = True

        if agent_version:
            agente_nome, versao = agent_version
            session.agent_versions[agente_nome] = versao
            updated = True

        if updated:
            session.save(update_fields=['contexto_atual', 'estados', 'agent_versions', 'atualizado_em'])
            # Atualiza cache
            self.cache.set_session(str(session.session_id), session.to_dict())
            logger.debug(f"Sessão atualizada: {session.session_id}")

    def should_sync_to_db(self, session_id: str) -> bool:
        """
        Verifica se deve sincronizar estado com DB.

        Sincroniza a cada N mensagens para balancear performance/durabilidade.

        Args:
            session_id: UUID da sessão

        Returns:
            bool: True se deve sincronizar
        """
        msg_count = self.cache.get_message_count(session_id)
        return msg_count % self.SYNC_EVERY_N_MESSAGES == 0

    def finalize_session(self, session_id: str) -> None:
        """
        Finaliza sessão (ao fechar chat).

        - Força sync com DB
        - Limpa cache Redis
        - Marca sessão como concluída

        Args:
            session_id: UUID da sessão
        """
        try:
            session = ChatSession.objects.get(session_id=session_id)

            # Sincroniza estado final
            cached = self.cache.get_session(session_id)
            if cached and cached.get('estados'):
                session.estados = cached['estados']
                session.status = 'concluida'
                session.save(update_fields=['estados', 'status', 'atualizado_em'])

            # Limpa cache
            self.cache.delete_session(session_id)

            logger.info(f"Sessão finalizada: {session_id}")

        except ChatSession.DoesNotExist:
            logger.warning(f"Tentativa de finalizar sessão inexistente: {session_id}")

    def get_session_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> list[ChatMessage]:
        """
        Retorna histórico de mensagens da sessão.

        Args:
            session_id: UUID da sessão
            limit: Quantidade máxima de mensagens (None = todas)

        Returns:
            list[ChatMessage]: Lista de mensagens ordenadas por data
        """
        queryset = ChatMessage.objects.filter(
            session__session_id=session_id
        ).select_related('user').order_by('criado_em')

        if limit:
            queryset = queryset[:limit]

        return list(queryset)

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """
        Retorna estatísticas da sessão.

        Args:
            session_id: UUID da sessão

        Returns:
            dict: Estatísticas (total_msgs, user_msgs, assistant_msgs, etc.)
        """
        try:
            session = ChatSession.objects.get(session_id=session_id)
            messages = session.mensagens.all()

            return {
                'session_id': session_id,
                'total_mensagens': messages.count(),
                'mensagens_usuario': messages.filter(role='user').count(),
                'mensagens_helena': messages.filter(role='assistant').count(),
                'contexto_atual': session.contexto_atual,
                'agentes_usados': list(session.agent_versions.keys()),
                'status': session.status,
                'criado_em': session.criado_em.isoformat() if session.criado_em else None,
                'atualizado_em': session.atualizado_em.isoformat() if session.atualizado_em else None,
            }
        except ChatSession.DoesNotExist:
            return {'error': 'Sessão não encontrada'}
