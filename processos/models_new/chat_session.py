"""
Modelo ChatSession - Sessão de conversação com Helena
"""
from django.db import models
from django.contrib.auth.models import User
from processos.models_new.orgao import Orgao
import uuid


class ChatSession(models.Model):
    """
    Sessão de conversação com Helena (Fase 2 — modelo ativo).

    Usado por: HelenaCore, chat_v2, SessionManager
    Modelo legado: HelenaSession (processos.models.HelenaSession)

    Características:
    - Stateless: estado armazenado em JSONB por produto
    - Multi-tenancy: isolado por órgão (FK Orgao)
    - Versionamento: rastreia versões dos agentes usados
    - Cache: sincronizado com Redis via SessionManager
    """

    # Identificação
    session_id = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        db_index=True,
        verbose_name="ID da Sessão",
        help_text="Identificador único da sessão"
    )

    # Relacionamentos
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_sessions',
        verbose_name="Usuário"
    )
    orgao = models.ForeignKey(
        Orgao,
        on_delete=models.PROTECT,  # Nunca deletar órgão com sessões ativas
        related_name='chat_sessions',
        verbose_name="Órgão",
        help_text="Órgão ao qual a sessão pertence (multi-tenancy)"
    )

    # Contexto e Estado
    contexto_atual = models.CharField(
        max_length=50,
        default='pop',
        verbose_name="Contexto Atual",
        help_text="Produto Helena ativo (pop, etapas, fluxograma, riscos, etc.)"
    )
    estados = models.JSONField(
        default=dict,
        verbose_name="Estados dos Agentes",
        help_text="Estado de cada agente: {'etapas': {...}, 'pop': {...}}"
    )

    # Versionamento
    agent_versions = models.JSONField(
        default=dict,
        verbose_name="Versões dos Agentes",
        help_text="Versão de cada agente usado: {'etapas': '1.0.0', 'pop': '1.2.0'}"
    )
    api_version = models.CharField(
        max_length=20,
        default='2025-10-01',
        verbose_name="Versão da API",
        help_text="Versão da API MapaGov usada"
    )

    # Metadados
    titulo = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Título",
        help_text="Título descritivo da sessão (ex: 'Mapeamento de Compras')"
    )
    tags = models.JSONField(
        default=list,
        verbose_name="Tags",
        help_text="Tags para organização: ['urgente', 'licitacao', 'compras']"
    )

    # Status
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('pausada', 'Pausada'),
        ('concluida', 'Concluída'),
        ('arquivada', 'Arquivada'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ativa',
        verbose_name="Status"
    )

    # Auditoria
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    finalizado_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Finalizado em"
    )

    class Meta:
        verbose_name = "Sessão de Chat"
        verbose_name_plural = "Sessões de Chat"
        ordering = ['-atualizado_em']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['orgao', '-criado_em']),
            models.Index(fields=['user', '-criado_em']),
            models.Index(fields=['status', '-atualizado_em']),
        ]

    def __str__(self):
        titulo = self.titulo or f"Sessão {self.session_id.hex[:8]}"
        return f"{titulo} - {self.orgao.sigla}"

    def to_dict(self) -> dict:
        """Serializa para dicionário (usado pelo SessionManager)"""
        return {
            'session_id': str(self.session_id),
            'user_id': self.user.id,
            'orgao_id': self.orgao.id,
            'contexto_atual': self.contexto_atual,
            'estados': self.estados,
            'agent_versions': self.agent_versions,
            'api_version': self.api_version,
            'status': self.status,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None,
        }

    def to_json(self) -> str:
        """Serializa para JSON (usado no Redis cache)"""
        import json
        return json.dumps(self.to_dict())

    def get_estado_agente(self, agente_nome: str) -> dict:
        """Retorna estado de um agente específico"""
        return self.estados.get(agente_nome, {})

    def set_estado_agente(self, agente_nome: str, estado: dict):
        """Define estado de um agente específico"""
        self.estados[agente_nome] = estado

    def count_mensagens(self) -> int:
        """Retorna total de mensagens na sessão"""
        return self.mensagens.count()

    def get_ultima_mensagem(self):
        """Retorna última mensagem (user ou assistant)"""
        return self.mensagens.order_by('-criado_em').first()
