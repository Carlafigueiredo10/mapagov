"""
Sistema de Autenticação e Controle de Acesso — MapaGov

Models:
- UserProfile: extensão do User Django (OneToOne) com status de acesso
- AccessApproval: votos de aprovadores para cadastros externos

Regras:
- MGI (@gestao.gov.br): access_status='approved' automaticamente, mas exige email_verified
- Externos: access_status='pending' até 3 aprovações (ou 2 rejeições)
- Acesso liberado apenas se: email_verified=True AND access_status='approved'
"""

from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

# ============================================================================
# CONSTANTES
# ============================================================================

MGI_DOMAIN = '@gestao.gov.br'
ACCESS_APPROVER_GROUP = 'ACCESS_APPROVER'
REQUIRED_APPROVALS = 3
REQUIRED_REJECTIONS = 2

ROLE_CHOICES = [
    ('operator', 'Operador'),
    ('area_manager', 'Gestor de Area'),
    ('general_manager', 'Gestor Geral'),
    ('admin', 'Administrador'),
]
ROLE_HIERARCHY = ['operator', 'area_manager', 'general_manager', 'admin']


def is_mgi_email(email: str) -> bool:
    """Verifica se o email pertence ao domínio MGI."""
    return email.strip().lower().endswith(MGI_DOMAIN)


def is_approver(user) -> bool:
    """
    Verifica se o usuario e um aprovador autorizado.
    Aprovador = superuser OR role >= area_manager.
    Mantém fallback para grupo ACCESS_APPROVER (compatibilidade).
    """
    if not user.is_active:
        return False
    if user.is_superuser:
        return True
    try:
        return user.profile.has_role('area_manager')
    except (UserProfile.DoesNotExist, AttributeError):
        # Fallback: grupo Django (compatibilidade com usuarios pre-migracao)
        return user.groups.filter(name=ACCESS_APPROVER_GROUP).exists()


def get_active_approvers_count() -> int:
    """Retorna o número de aprovadores ativos elegíveis."""
    superuser_ids = set(
        User.objects.filter(is_superuser=True, is_active=True)
        .values_list('id', flat=True)
    )
    group_ids = set(
        User.objects.filter(
            groups__name=ACCESS_APPROVER_GROUP, is_active=True
        ).values_list('id', flat=True)
    )
    return len(superuser_ids | group_ids)


# ============================================================================
# MODELS
# ============================================================================

class UserProfile(models.Model):
    """
    Perfil estendido do usuário MapaGov.

    Não substitui o User do Django — usa OneToOneField para evitar
    conflitos com FKs existentes (POP, POPChangeLog, HelenaSession, etc.).
    """

    PROFILE_TYPE_CHOICES = [
        ('mgi', 'MGI (gestao.gov.br)'),
        ('externo', 'Externo'),
    ]

    ACCESS_STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    profile_type = models.CharField(
        max_length=10,
        choices=PROFILE_TYPE_CHOICES,
        default='externo',
    )
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    access_status = models.CharField(
        max_length=10,
        choices=ACCESS_STATUS_CHOICES,
        default='pending',
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='operator',
        db_index=True,
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)

    # Vínculo institucional
    orgao = models.ForeignKey(
        'processos.Orgao',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_profiles',
    )
    area = models.ForeignKey(
        'processos.Area',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_profiles',
    )

    # Dados pessoais
    nome_completo = models.CharField(max_length=255, blank=True)
    cargo = models.CharField(max_length=255, blank=True)
    setor_trabalho = models.CharField(
        max_length=255, blank=True,
        verbose_name='Setor de trabalho',
        help_text='Informado por usuarios nao-Decipex no cadastro.',
    )
    is_decipex = models.BooleanField(default=False, verbose_name='Pertence a Decipex')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'
        indexes = [
            models.Index(fields=['access_status']),
            models.Index(fields=['profile_type', 'access_status']),
        ]

    def __str__(self):
        return f"{self.user.email} ({self.get_access_status_display()})"

    @property
    def is_mgi(self) -> bool:
        return self.profile_type == 'mgi'

    @property
    def can_access(self) -> bool:
        """Acesso liberado apenas se email verificado E status aprovado."""
        return self.email_verified and self.access_status == 'approved'

    @property
    def role_level(self) -> int:
        """Retorna nivel hierarquico do role (0=operator, 3=admin)."""
        try:
            return ROLE_HIERARCHY.index(self.role)
        except ValueError:
            return 0

    def has_role(self, minimum_role: str) -> bool:
        """Verifica se o role do usuario e >= minimum_role."""
        try:
            required = ROLE_HIERARCHY.index(minimum_role)
        except ValueError:
            return False
        return self.role_level >= required

    def approve(self):
        """Marca o perfil como aprovado."""
        self.access_status = 'approved'
        self.approved_at = timezone.now()
        self.save(update_fields=['access_status', 'approved_at', 'updated_at'])

    def reject(self):
        """Marca o perfil como rejeitado."""
        self.access_status = 'rejected'
        self.rejected_at = timezone.now()
        self.save(update_fields=['access_status', 'rejected_at', 'updated_at'])

    def verify_email(self):
        """Marca o email como verificado."""
        self.email_verified = True
        self.email_verified_at = timezone.now()
        self.save(update_fields=['email_verified', 'email_verified_at', 'updated_at'])


class AccessApproval(models.Model):
    """
    Voto de um aprovador sobre cadastro de usuário externo.

    Regras:
    - 3 aprovações → acesso liberado
    - 2 rejeições → acesso negado
    - Se < 3 aprovadores elegíveis, exige TODOS (mínimo 1)
    - FK PROTECT: admin não deve ser deletado, apenas desativado
    """

    VOTE_CHOICES = [
        ('approve', 'Aprovado'),
        ('reject', 'Rejeitado'),
    ]

    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='approvals',
    )
    admin = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='votes_cast',
    )
    vote = models.CharField(max_length=10, choices=VOTE_CHOICES)
    justificativa = models.TextField(blank=True)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Aprovação de Acesso'
        verbose_name_plural = 'Aprovações de Acesso'
        unique_together = ['user_profile', 'admin']
        ordering = ['-voted_at']

    def __str__(self):
        return f"{self.admin.email} → {self.user_profile.user.email}: {self.vote}"


# ============================================================================
# LÓGICA DE VOTAÇÃO
# ============================================================================

def process_vote(user_profile: UserProfile) -> str | None:
    """
    Avalia votos após nova votação e atualiza status se necessário.

    Retorna:
    - 'approved' se aprovado
    - 'rejected' se rejeitado
    - None se ainda pendente
    """
    if user_profile.access_status != 'pending':
        return user_profile.access_status

    # Conta apenas votos de admins ativos
    votes = user_profile.approvals.filter(admin__is_active=True)
    approve_count = votes.filter(vote='approve').count()
    reject_count = votes.filter(vote='reject').count()

    # Quantos aprovadores elegíveis existem?
    total_approvers = get_active_approvers_count()
    required_approvals = min(REQUIRED_APPROVALS, total_approvers)
    required_rejections = min(REQUIRED_REJECTIONS, total_approvers)

    # Garante mínimo de 1
    required_approvals = max(required_approvals, 1)
    required_rejections = max(required_rejections, 1)

    if approve_count >= required_approvals:
        user_profile.approve()
        return 'approved'

    if reject_count >= required_rejections:
        user_profile.reject()
        return 'rejected'

    return None


# ============================================================================
# HELPERS
# ============================================================================

def get_or_create_profile(user) -> 'UserProfile':
    """
    Retorna o UserProfile do usuario, criando com defaults consistentes se nao existir.
    Usado por: signal post_save, fallback do /me/, e qualquer ponto que precise de profile.
    """
    try:
        return user.profile
    except UserProfile.DoesNotExist:
        email = user.email.strip().lower() if user.email else ''
        profile_type = 'mgi' if is_mgi_email(email) else 'externo'
        access_status = 'approved' if profile_type == 'mgi' else 'pending'
        return UserProfile.objects.create(
            user=user,
            profile_type=profile_type,
            access_status=access_status,
            role='operator',
        )


# ============================================================================
# SIGNALS
# ============================================================================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Cria UserProfile automaticamente ao criar User."""
    if created:
        get_or_create_profile(instance)
