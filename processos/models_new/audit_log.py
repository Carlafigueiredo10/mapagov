"""
FASE 2 - Audit Log

Sistema de auditoria completo para rastreabilidade e compliance (LGPD).

Registra:
- Quem fez (usuário)
- O quê (ação)
- Quando (timestamp)
- Onde (IP, user agent)
- Em qual recurso (modelo, ID)
- Resultado (sucesso/erro)
- Dados antes/depois (para rollback)

Benefícios:
- Compliance com LGPD (Art. 48 - Comunicação de incidente)
- Forense (investigação de incidentes)
- Rollback (reverter alterações indevidas)
- Analytics (quem usa o quê, quando)
"""

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import json


class AuditLog(models.Model):
    """
    Log de auditoria genérico.

    Registra todas as ações importantes no sistema.
    """

    ACTION_CHOICES = [
        ('create', 'Criar'),
        ('read', 'Visualizar'),
        ('update', 'Atualizar'),
        ('delete', 'Excluir'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('permission_denied', 'Permissão Negada'),
        ('export', 'Exportar'),
        ('import', 'Importar'),
        ('generate', 'Gerar'),
        # Auth & Access Control
        ('register', 'Registro'),
        ('email_verify', 'Verificação de E-mail'),
        ('access_request', 'Solicitação de Acesso'),
        ('access_approve', 'Aprovação de Acesso'),
        ('access_reject', 'Rejeição de Acesso'),
        ('password_reset', 'Reset de Senha'),
    ]

    # Quem
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text="Usuário que executou a ação"
    )

    username = models.CharField(
        max_length=150,
        help_text="Username (preservado mesmo se user for deletado)"
    )

    # O quê
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        db_index=True,
        help_text="Tipo de ação executada"
    )

    resource = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Recurso afetado (ex: processo, chat, usuario)"
    )

    # Recurso genérico (permite vincular a qualquer model)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Tipo do objeto afetado"
    )

    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="ID do objeto afetado"
    )

    content_object = GenericForeignKey('content_type', 'object_id')

    # Quando
    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="Momento da ação"
    )

    # Onde
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP do cliente"
    )

    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="User Agent do navegador"
    )

    # Contexto organizacional
    orgao = models.ForeignKey(
        'Orgao',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text="Órgão do usuário no momento da ação"
    )

    # Detalhes
    description = models.TextField(
        blank=True,
        help_text="Descrição legível da ação"
    )

    # Resultado
    success = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Se a ação foi bem-sucedida"
    )

    error_message = models.TextField(
        blank=True,
        help_text="Mensagem de erro (se falhou)"
    )

    # Dados para rollback
    old_value = models.JSONField(
        null=True,
        blank=True,
        help_text="Valor anterior (para UPDATE)"
    )

    new_value = models.JSONField(
        null=True,
        blank=True,
        help_text="Novo valor (para CREATE/UPDATE)"
    )

    # Metadados adicionais
    metadata = models.JSONField(
        default=dict,
        help_text="Metadados adicionais (query params, body, etc.)"
    )

    # Duração (performance tracking)
    duration_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Duração da operação em milissegundos"
    )

    class Meta:
        db_table = 'processos_audit_log'
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['resource', 'action', 'timestamp']),
            models.Index(fields=['orgao', 'timestamp']),
            models.Index(fields=['success', 'timestamp']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        result = '✓' if self.success else '✗'
        return f"{result} {self.username} {self.action} {self.resource} @ {self.timestamp}"

    @classmethod
    def log_action(
        cls,
        user,
        action: str,
        resource: str,
        success: bool = True,
        description: str = '',
        old_value=None,
        new_value=None,
        content_object=None,
        ip_address=None,
        user_agent=None,
        orgao=None,
        metadata=None,
        duration_ms=None,
        error_message: str = ''
    ):
        """
        Helper method para criar log de auditoria.

        Uso:
            from processos.models_new.audit_log import AuditLog

            AuditLog.log_action(
                user=request.user,
                action='create',
                resource='processo',
                description='Criou processo de compras',
                new_value={'nome': 'Compras', ...},
                ip_address=request.META.get('REMOTE_ADDR'),
                orgao=orgao
            )
        """
        username = user.username if user and user.is_authenticated else 'anonymous'

        # Content type e object_id do objeto afetado
        ct = None
        obj_id = None
        if content_object:
            ct = ContentType.objects.get_for_model(content_object)
            obj_id = content_object.pk

        return cls.objects.create(
            user=user if (user and user.is_authenticated) else None,
            username=username,
            action=action,
            resource=resource,
            success=success,
            description=description,
            old_value=old_value,
            new_value=new_value,
            content_type=ct,
            object_id=obj_id,
            ip_address=ip_address,
            user_agent=user_agent,
            orgao=orgao,
            metadata=metadata or {},
            duration_ms=duration_ms,
            error_message=error_message
        )

    @classmethod
    def get_user_activity(cls, user, days=30):
        """
        Retorna atividade do usuário nos últimos N dias.
        """
        from datetime import timedelta
        since = timezone.now() - timedelta(days=days)

        return cls.objects.filter(
            user=user,
            timestamp__gte=since
        ).order_by('-timestamp')

    @classmethod
    def get_resource_history(cls, content_object, days=None):
        """
        Retorna histórico de um objeto específico.

        Uso:
            processo = Processo.objects.get(id=123)
            history = AuditLog.get_resource_history(processo)
        """
        ct = ContentType.objects.get_for_model(content_object)

        queryset = cls.objects.filter(
            content_type=ct,
            object_id=content_object.pk
        )

        if days:
            from datetime import timedelta
            since = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(timestamp__gte=since)

        return queryset.order_by('-timestamp')

    @classmethod
    def get_failed_actions(cls, hours=24):
        """
        Retorna ações que falharam nas últimas N horas (para alertas).
        """
        from datetime import timedelta
        since = timezone.now() - timedelta(hours=hours)

        return cls.objects.filter(
            success=False,
            timestamp__gte=since
        ).order_by('-timestamp')


class SecurityEvent(models.Model):
    """
    Eventos de segurança específicos (tentativas de acesso não autorizado, etc.).

    Separado do AuditLog para análise de segurança focada.
    """

    EVENT_TYPES = [
        ('unauthorized_access', 'Tentativa de Acesso Não Autorizado'),
        ('permission_escalation', 'Tentativa de Escalação de Privilégios'),
        ('suspicious_activity', 'Atividade Suspeita'),
        ('brute_force', 'Tentativa de Força Bruta'),
        ('data_leak', 'Tentativa de Vazamento de Dados'),
        ('sql_injection', 'Tentativa de SQL Injection'),
        ('xss_attempt', 'Tentativa de XSS'),
    ]

    SEVERITY_LEVELS = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]

    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPES,
        db_index=True
    )

    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_LEVELS,
        default='medium',
        db_index=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='security_events'
    )

    username = models.CharField(max_length=150)

    ip_address = models.GenericIPAddressField()

    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    description = models.TextField()

    details = models.JSONField(
        default=dict,
        help_text="Detalhes técnicos do evento"
    )

    resolved = models.BooleanField(
        default=False,
        help_text="Se o evento foi investigado/resolvido"
    )

    resolved_at = models.DateTimeField(null=True, blank=True)

    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_security_events'
    )

    notes = models.TextField(
        blank=True,
        help_text="Notas da investigação"
    )

    class Meta:
        db_table = 'processos_security_event'
        verbose_name = 'Evento de Segurança'
        verbose_name_plural = 'Eventos de Segurança'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['severity', 'resolved', 'timestamp']),
            models.Index(fields=['event_type', 'timestamp']),
        ]

    def __str__(self):
        return f"[{self.get_severity_display()}] {self.get_event_type_display()} - {self.username} @ {self.timestamp}"

    @classmethod
    def log_security_event(
        cls,
        event_type: str,
        severity: str,
        user,
        ip_address: str,
        description: str,
        details: dict = None
    ):
        """
        Registra evento de segurança.

        Uso:
            SecurityEvent.log_security_event(
                event_type='unauthorized_access',
                severity='high',
                user=request.user,
                ip_address=request.META.get('REMOTE_ADDR'),
                description='Tentou acessar dados de outro órgão',
                details={'orgao_tentado': 'AGU', 'orgao_usuario': 'TCU'}
            )
        """
        username = user.username if user and user.is_authenticated else 'anonymous'

        return cls.objects.create(
            event_type=event_type,
            severity=severity,
            user=user if (user and user.is_authenticated) else None,
            username=username,
            ip_address=ip_address,
            description=description,
            details=details or {}
        )
