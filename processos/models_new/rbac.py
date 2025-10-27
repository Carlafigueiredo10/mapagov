"""
FASE 2 - RBAC (Role-Based Access Control)

Sistema de controle de acesso baseado em funções para MapaGov.

Hierarquia de Roles:
- ADMIN_ORGAO: Administrador do órgão (pode tudo no órgão)
- GESTOR: Gestor de processos (criar/editar/excluir processos)
- ANALISTA: Analista (criar/editar processos)
- VISUALIZADOR: Apenas visualização (read-only)
- AUDITOR_SISTEMA: Auditor (acesso multi-orgão, read-only)

Permissões:
- Granulares por recurso (processo, chat, análise de riscos, etc.)
- Herdadas via hierarquia (ADMIN tem todas as permissões)
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from processos.models_new.orgao import Orgao


class Role(models.Model):
    """
    Função/Papel no sistema.

    Exemplos:
    - admin_orgao: Administrador do órgão
    - gestor: Gestor de processos
    - analista: Analista
    """

    ROLE_CHOICES = [
        ('admin_orgao', 'Administrador do Órgão'),
        ('gestor', 'Gestor de Processos'),
        ('analista', 'Analista'),
        ('visualizador', 'Visualizador'),
        ('auditor_sistema', 'Auditor do Sistema'),
    ]

    # Hierarquia de roles (role -> quais roles herda)
    ROLE_HIERARCHY = {
        'admin_orgao': ['gestor', 'analista', 'visualizador'],
        'gestor': ['analista', 'visualizador'],
        'analista': ['visualizador'],
        'visualizador': [],
        'auditor_sistema': [],  # Não herda, tem permissões específicas
    }

    nome = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        unique=True,
        help_text="Nome da função"
    )

    descricao = models.TextField(
        blank=True,
        help_text="Descrição detalhada da função"
    )

    ativo = models.BooleanField(
        default=True,
        help_text="Se a função está ativa no sistema"
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'processos_role'
        verbose_name = 'Função'
        verbose_name_plural = 'Funções'

    def __str__(self):
        return self.get_nome_display()

    def get_inherited_roles(self) -> list[str]:
        """
        Retorna lista de roles herdadas (incluindo a própria).

        Returns:
            ['role_atual', 'role_herdada1', ...]
        """
        inherited = [self.nome]
        inherited.extend(self.ROLE_HIERARCHY.get(self.nome, []))
        return inherited


class Permission(models.Model):
    """
    Permissão granular no sistema.

    Formato: <recurso>.<ação>
    Exemplos:
    - processo.criar
    - processo.editar
    - processo.excluir
    - chat.criar
    - chat.visualizar
    - analise_riscos.criar
    """

    codigo = models.CharField(
        max_length=100,
        unique=True,
        help_text="Código da permissão (ex: processo.criar)"
    )

    nome = models.CharField(
        max_length=200,
        help_text="Nome legível da permissão"
    )

    descricao = models.TextField(
        blank=True,
        help_text="Descrição da permissão"
    )

    recurso = models.CharField(
        max_length=50,
        help_text="Recurso (processo, chat, etc.)",
        db_index=True
    )

    acao = models.CharField(
        max_length=50,
        help_text="Ação (criar, editar, excluir, visualizar)",
        db_index=True
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'processos_permission'
        verbose_name = 'Permissão'
        verbose_name_plural = 'Permissões'
        unique_together = ['recurso', 'acao']
        indexes = [
            models.Index(fields=['recurso', 'acao']),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    def clean(self):
        """Validação: código deve ser <recurso>.<ação>"""
        if '.' not in self.codigo:
            raise ValidationError("Código deve ser no formato '<recurso>.<acao>'")

        partes = self.codigo.split('.')
        if len(partes) != 2:
            raise ValidationError("Código deve ter exatamente um ponto")

        # Sincronizar recurso e ação com código
        self.recurso, self.acao = partes


class RolePermission(models.Model):
    """
    Associação entre Role e Permission.

    Define quais permissões cada role possui.
    """

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='permissions'
    )

    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='roles'
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'processos_role_permission'
        verbose_name = 'Role-Permissão'
        verbose_name_plural = 'Roles-Permissões'
        unique_together = ['role', 'permission']

    def __str__(self):
        return f"{self.role.nome} → {self.permission.codigo}"


class UserRole(models.Model):
    """
    Atribuição de Role para Usuário em um Orgão específico.

    Um usuário pode ter diferentes roles em diferentes órgãos.
    Exemplos:
    - user_1 é ADMIN no Orgão A
    - user_1 é VISUALIZADOR no Orgão B
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='roles'
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_assignments'
    )

    orgao = models.ForeignKey(
        Orgao,
        on_delete=models.CASCADE,
        related_name='user_roles',
        help_text="Órgão onde a role é válida"
    )

    ativo = models.BooleanField(
        default=True,
        help_text="Se a atribuição está ativa"
    )

    data_inicio = models.DateField(
        null=True,
        blank=True,
        help_text="Data de início da atribuição"
    )

    data_fim = models.DateField(
        null=True,
        blank=True,
        help_text="Data de fim da atribuição (null = permanente)"
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'processos_user_role'
        verbose_name = 'Atribuição de Role'
        verbose_name_plural = 'Atribuições de Roles'
        unique_together = ['user', 'role', 'orgao']
        indexes = [
            models.Index(fields=['user', 'orgao', 'ativo']),
        ]

    def __str__(self):
        return f"{self.user.username} → {self.role.nome} @ {self.orgao.sigla}"

    def clean(self):
        """Validação: data_fim deve ser posterior a data_inicio"""
        if self.data_inicio and self.data_fim:
            if self.data_fim <= self.data_inicio:
                raise ValidationError("Data de fim deve ser posterior à data de início")


# ================================================
# Helper Functions para verificar permissões
# ================================================

def user_has_permission(user: User, permission_code: str, orgao: Orgao) -> bool:
    """
    Verifica se usuário tem permissão em um órgão.

    Args:
        user: Usuário
        permission_code: Código da permissão (ex: 'processo.criar')
        orgao: Órgão onde verificar

    Returns:
        True se tem permissão, False caso contrário

    Exemplo:
        if user_has_permission(user, 'processo.criar', orgao):
            # Permitir criação
    """
    # Superuser sempre tem permissão
    if user.is_superuser:
        return True

    # Buscar roles do usuário neste órgão
    user_roles = UserRole.objects.filter(
        user=user,
        orgao=orgao,
        ativo=True
    ).select_related('role')

    # Para cada role, verificar se tem a permissão (incluindo herdadas)
    for user_role in user_roles:
        role = user_role.role
        inherited_roles = role.get_inherited_roles()

        # Verificar se alguma role (atual ou herdada) tem a permissão
        has_perm = RolePermission.objects.filter(
            role__nome__in=inherited_roles,
            permission__codigo=permission_code
        ).exists()

        if has_perm:
            return True

    return False


def get_user_permissions(user: User, orgao: Orgao) -> list[str]:
    """
    Retorna lista de todas as permissões do usuário em um órgão.

    Args:
        user: Usuário
        orgao: Órgão

    Returns:
        Lista de códigos de permissões (ex: ['processo.criar', 'processo.editar'])
    """
    if user.is_superuser:
        # Superuser tem todas as permissões
        return list(Permission.objects.values_list('codigo', flat=True))

    permissions = set()

    # Buscar roles do usuário
    user_roles = UserRole.objects.filter(
        user=user,
        orgao=orgao,
        ativo=True
    ).select_related('role')

    for user_role in user_roles:
        role = user_role.role
        inherited_roles = role.get_inherited_roles()

        # Buscar permissões de todas as roles (incluindo herdadas)
        role_perms = Permission.objects.filter(
            roles__role__nome__in=inherited_roles
        ).values_list('codigo', flat=True)

        permissions.update(role_perms)

    return sorted(list(permissions))
