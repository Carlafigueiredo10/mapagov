"""
Modelo ChatMessage - Mensagens em sessões de chat
"""
from django.db import models
from django.contrib.auth.models import User
from processos.models_new.chat_session import ChatSession
import uuid


class ChatMessage(models.Model):
    """
    Representa uma mensagem individual em uma sessão de chat.

    Características:
    - Idempotência: req_uuid garante não-duplicação em retries
    - Auditoria: rastreia quem disse o quê e quando
    - Performance: índices otimizados para queries comuns
    """

    # Identificação (Idempotência)
    req_uuid = models.UUIDField(
        unique=True,
        db_index=True,
        verbose_name="Request UUID",
        help_text="UUID único por request (garante idempotência em retries)"
    )

    # Relacionamentos
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='mensagens',
        verbose_name="Sessão"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        verbose_name="Usuário",
        help_text="Redundante com session.user, mas útil para auditoria"
    )

    # Conteúdo
    ROLE_CHOICES = [
        ('user', 'Usuário'),
        ('assistant', 'Assistente (Helena)'),
        ('system', 'Sistema'),
    ]
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        verbose_name="Papel",
        help_text="Quem enviou a mensagem"
    )
    content = models.TextField(
        verbose_name="Conteúdo",
        help_text="Texto da mensagem"
    )

    # Contexto
    contexto = models.CharField(
        max_length=50,
        verbose_name="Contexto",
        help_text="Produto Helena ativo quando mensagem foi enviada"
    )

    # Metadados (opcional)
    metadados = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadados",
        help_text="Dados extras: tokens usados, latência, model usado, etc."
    )

    # Auditoria
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )

    class Meta:
        verbose_name = "Mensagem de Chat"
        verbose_name_plural = "Mensagens de Chat"
        ordering = ['criado_em']
        indexes = [
            models.Index(fields=['session', 'criado_em']),  # Query: listar msgs de sessão
            models.Index(fields=['req_uuid']),  # Query: verificar duplicatas
            models.Index(fields=['user', '-criado_em']),  # Query: mensagens por usuário
            models.Index(fields=['contexto', '-criado_em']),  # Query: análise por produto
        ]
        # Constraint: garante unicidade de req_uuid
        constraints = [
            models.UniqueConstraint(
                fields=['req_uuid'],
                name='unique_request_uuid'
            )
        ]

    def __str__(self):
        preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.get_role_display()}: {preview}"

    def to_dict(self) -> dict:
        """Serializa para dicionário"""
        return {
            'req_uuid': str(self.req_uuid),
            'session_id': str(self.session.session_id),
            'role': self.role,
            'content': self.content,
            'contexto': self.contexto,
            'metadados': self.metadados,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
        }

    def is_user_message(self) -> bool:
        """Verifica se mensagem é do usuário"""
        return self.role == 'user'

    def is_assistant_message(self) -> bool:
        """Verifica se mensagem é da Helena"""
        return self.role == 'assistant'

    def get_resposta(self):
        """
        Retorna mensagem seguinte (resposta do assistente).
        Útil para análise de pares pergunta/resposta.
        """
        if self.role == 'user':
            return ChatMessage.objects.filter(
                session=self.session,
                criado_em__gt=self.criado_em,
                role='assistant'
            ).first()
        return None

    def count_tokens(self) -> int:
        """
        Estima quantidade de tokens (aproximação simples).
        Para precisão, usar tiktoken da OpenAI.
        """
        # Aproximação: 1 token ≈ 4 caracteres
        return len(self.content) // 4
