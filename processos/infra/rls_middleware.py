"""
FASE 2 - RLS Middleware

Middleware que configura variáveis de sessão do PostgreSQL para Row-Level Security.

Para cada requisição:
1. Identifica o usuário autenticado
2. Obtém o Orgão do usuário
3. Configura app.current_orgao_id no PostgreSQL
4. Configura app.is_superuser para auditores

ESCOPO ATUAL (migração 0008):
- Políticas RLS ativas apenas em: ChatSession, ChatMessage
- Demais tabelas ainda não possuem políticas RLS
"""

import logging
from django.db import connection
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


class RLSMiddleware:
    """
    Middleware para configurar Row-Level Security (RLS) do PostgreSQL.

    Configura variáveis de sessão que são usadas pelas políticas RLS:
    - app.current_orgao_id: ID do órgão do usuário atual
    - app.is_superuser: Se o usuário é superuser (para auditoria)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Configurar RLS antes de processar a requisição
        self._setup_rls(request)

        # Processar requisição
        response = self.get_response(request)

        # Limpar variáveis após a requisição (segurança)
        self._cleanup_rls()

        return response

    def _setup_rls(self, request):
        """
        Configura variáveis de sessão do PostgreSQL para RLS.

        NOTA: RLS só funciona em PostgreSQL. Em SQLite (desenvolvimento),
        o middleware ainda funciona mas não aplica políticas RLS.
        """
        # Verificar se é PostgreSQL
        db_vendor = connection.vendor

        if db_vendor == 'sqlite':
            # Em SQLite, RLS não funciona. Apenas logar para desenvolvimento.
            logger.debug("SQLite detectado - RLS não disponível (normal em desenvolvimento)")
            return

        user = request.user

        # Usuário não autenticado
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            # Para requisições públicas, não configurar RLS
            # (as queries falharão se tentarem acessar dados protegidos)
            return

        try:
            # Determinar Orgão do usuário
            orgao_id = self._get_user_orgao_id(user)

            if orgao_id is None:
                logger.warning(
                    f"Usuário {user.username} (ID: {user.id}) não tem Orgão associado. "
                    "RLS não será configurado."
                )
                return

            # Configurar variáveis de sessão do PostgreSQL
            with connection.cursor() as cursor:
                # Orgão atual
                cursor.execute(
                    "SET LOCAL app.current_orgao_id = %s;",
                    [orgao_id]
                )

                # Superuser flag (para auditoria)
                cursor.execute(
                    "SET LOCAL app.is_superuser = %s;",
                    [user.is_superuser]
                )

            logger.debug(
                f"RLS configurado: user={user.username}, "
                f"orgao_id={orgao_id}, "
                f"is_superuser={user.is_superuser}"
            )

        except Exception as e:
            logger.exception(f"Erro ao configurar RLS: {e}")
            # Não interromper requisição, mas logar erro
            # Em produção, considere retornar 500 para segurança

    def _cleanup_rls(self):
        """
        Limpa variáveis de sessão do PostgreSQL (segurança).

        IMPORTANTE: Django usa connection pooling, então variáveis
        SET LOCAL persistem até o fim da transação. Limpar explicitamente
        é uma boa prática de segurança.

        NOTA: RESET só funciona em PostgreSQL. Em SQLite, ignoramos.
        """
        try:
            # Verificar se é PostgreSQL
            db_vendor = connection.vendor

            if db_vendor == 'postgresql':
                with connection.cursor() as cursor:
                    # RESET LOCAL limpa apenas variáveis SET LOCAL
                    cursor.execute("RESET app.current_orgao_id;")
                    cursor.execute("RESET app.is_superuser;")
            elif db_vendor == 'sqlite':
                # SQLite não suporta RESET nem SET LOCAL
                # Em SQLite, variáveis de sessão não persistem entre conexões
                # então não precisa limpar explicitamente
                pass

        except Exception as e:
            logger.warning(f"Erro ao limpar variáveis RLS: {e}")
            # Não crítico, apenas warning

    def _get_user_orgao_id(self, user) -> int | None:
        """
        Obtém o ID do Orgão do usuário.

        Estratégias (em ordem):
        1. user.orgao (se modelo User customizado tem campo orgao)
        2. user.profile.orgao (se há perfil separado)
        3. Primeiro Orgao no banco (fallback para testes)

        Returns:
            ID do órgão ou None se não encontrado
        """
        # Estratégia 1: Campo direto no User
        if hasattr(user, 'orgao') and user.orgao is not None:
            return user.orgao.id

        # Estratégia 2: Profile separado
        if hasattr(user, 'profile') and hasattr(user.profile, 'orgao'):
            if user.profile.orgao is not None:
                return user.profile.orgao.id

        # Estratégia 3: Primeiro Orgao (APENAS para testes/desenvolvimento)
        # REMOVER em produção!
        from processos.models_new.orgao import Orgao
        primeiro_orgao = Orgao.objects.first()
        if primeiro_orgao:
            logger.warning(
                f"Usuário {user.username} não tem Orgão. "
                f"Usando primeiro Orgão ({primeiro_orgao.sigla}) para testes."
            )
            return primeiro_orgao.id

        return None


class RLSContextManager:
    """
    Context manager para configurar RLS temporariamente (útil para testes e scripts).

    Uso:
        from processos.infra.rls_middleware import RLSContextManager

        with RLSContextManager(orgao_id=1, is_superuser=False):
            # Queries aqui respeitarão RLS para orgao_id=1
            sessions = ChatSession.objects.all()  # Apenas do Orgão 1
    """

    def __init__(self, orgao_id: int, is_superuser: bool = False):
        self.orgao_id = orgao_id
        self.is_superuser = is_superuser

    def __enter__(self):
        # Só funciona em PostgreSQL
        if connection.vendor == 'postgresql':
            with connection.cursor() as cursor:
                cursor.execute("SET LOCAL app.current_orgao_id = %s;", [self.orgao_id])
                cursor.execute("SET LOCAL app.is_superuser = %s;", [self.is_superuser])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Só funciona em PostgreSQL
        if connection.vendor == 'postgresql':
            with connection.cursor() as cursor:
                cursor.execute("RESET app.current_orgao_id;")
                cursor.execute("RESET app.is_superuser;")
