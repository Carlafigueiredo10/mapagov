"""
FASE 2 - RBAC Models

Adiciona tabelas de Role-Based Access Control:
- Role: Funções no sistema
- Permission: Permissões granulares
- RolePermission: Associação role-permissão
- UserRole: Atribuição de role para usuário em um órgão
"""

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


def populate_default_roles_and_permissions(apps, schema_editor):
    """
    Popula roles e permissões padrão.
    """
    Role = apps.get_model('processos', 'Role')
    Permission = apps.get_model('processos', 'Permission')
    RolePermission = apps.get_model('processos', 'RolePermission')

    # ================================================
    # 1. Criar Roles
    # ================================================
    roles = {
        'admin_orgao': Role.objects.create(
            nome='admin_orgao',
            descricao='Administrador do órgão. Pode gerenciar usuários, processos e todas as funcionalidades.'
        ),
        'gestor': Role.objects.create(
            nome='gestor',
            descricao='Gestor de processos. Pode criar, editar e excluir processos.'
        ),
        'analista': Role.objects.create(
            nome='analista',
            descricao='Analista. Pode criar e editar processos, mas não excluir.'
        ),
        'visualizador': Role.objects.create(
            nome='visualizador',
            descricao='Visualizador. Apenas visualização (read-only).'
        ),
        'auditor_sistema': Role.objects.create(
            nome='auditor_sistema',
            descricao='Auditor do sistema. Acesso multi-orgão em modo leitura para auditoria.'
        ),
    }

    # ================================================
    # 2. Criar Permissões
    # ================================================
    permissions_data = [
        # Processo
        ('processo.criar', 'Criar Processo', 'processo', 'criar'),
        ('processo.editar', 'Editar Processo', 'processo', 'editar'),
        ('processo.excluir', 'Excluir Processo', 'processo', 'excluir'),
        ('processo.visualizar', 'Visualizar Processo', 'processo', 'visualizar'),

        # Chat
        ('chat.criar', 'Criar Chat/Sessão', 'chat', 'criar'),
        ('chat.visualizar', 'Visualizar Chat', 'chat', 'visualizar'),
        ('chat.excluir', 'Excluir Chat', 'chat', 'excluir'),

        # Análise de Riscos
        ('analise_riscos.criar', 'Criar Análise de Riscos', 'analise_riscos', 'criar'),
        ('analise_riscos.editar', 'Editar Análise de Riscos', 'analise_riscos', 'editar'),
        ('analise_riscos.visualizar', 'Visualizar Análise de Riscos', 'analise_riscos', 'visualizar'),

        # Usuários (gerenciamento)
        ('usuario.criar', 'Criar Usuário', 'usuario', 'criar'),
        ('usuario.editar', 'Editar Usuário', 'usuario', 'editar'),
        ('usuario.excluir', 'Excluir Usuário', 'usuario', 'excluir'),
        ('usuario.visualizar', 'Visualizar Usuário', 'usuario', 'visualizar'),

        # Auditoria
        ('auditoria.visualizar', 'Visualizar Logs de Auditoria', 'auditoria', 'visualizar'),
    ]

    permissions = {}
    for codigo, nome, recurso, acao in permissions_data:
        perm = Permission.objects.create(
            codigo=codigo,
            nome=nome,
            recurso=recurso,
            acao=acao
        )
        permissions[codigo] = perm

    # ================================================
    # 3. Associar Permissões às Roles
    # ================================================

    # VISUALIZADOR: Apenas visualizar
    for perm_code in ['processo.visualizar', 'chat.visualizar', 'analise_riscos.visualizar']:
        RolePermission.objects.create(
            role=roles['visualizador'],
            permission=permissions[perm_code]
        )

    # ANALISTA: Visualizar + Criar + Editar (sem excluir)
    for perm_code in [
        'processo.visualizar', 'processo.criar', 'processo.editar',
        'chat.visualizar', 'chat.criar',
        'analise_riscos.visualizar', 'analise_riscos.criar', 'analise_riscos.editar',
    ]:
        RolePermission.objects.create(
            role=roles['analista'],
            permission=permissions[perm_code]
        )

    # GESTOR: Tudo de processo/chat/riscos
    for perm_code in [
        'processo.visualizar', 'processo.criar', 'processo.editar', 'processo.excluir',
        'chat.visualizar', 'chat.criar', 'chat.excluir',
        'analise_riscos.visualizar', 'analise_riscos.criar', 'analise_riscos.editar',
    ]:
        RolePermission.objects.create(
            role=roles['gestor'],
            permission=permissions[perm_code]
        )

    # ADMIN_ORGAO: Tudo
    for perm in permissions.values():
        RolePermission.objects.create(
            role=roles['admin_orgao'],
            permission=perm
        )

    # AUDITOR_SISTEMA: Apenas visualizar + auditoria
    for perm_code in [
        'processo.visualizar', 'chat.visualizar', 'analise_riscos.visualizar',
        'usuario.visualizar', 'auditoria.visualizar'
    ]:
        RolePermission.objects.create(
            role=roles['auditor_sistema'],
            permission=permissions[perm_code]
        )


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('processos', '0008_add_rls_policies'),
    ]

    operations = [
        # ================================================
        # Tabela: Role
        # ================================================
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(
                    choices=[
                        ('admin_orgao', 'Administrador do Órgão'),
                        ('gestor', 'Gestor de Processos'),
                        ('analista', 'Analista'),
                        ('visualizador', 'Visualizador'),
                        ('auditor_sistema', 'Auditor do Sistema'),
                    ],
                    help_text='Nome da função',
                    max_length=50,
                    unique=True
                )),
                ('descricao', models.TextField(blank=True, help_text='Descrição detalhada da função')),
                ('ativo', models.BooleanField(default=True, help_text='Se a função está ativa no sistema')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Função',
                'verbose_name_plural': 'Funções',
                'db_table': 'processos_role',
            },
        ),

        # ================================================
        # Tabela: Permission
        # ================================================
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(
                    help_text='Código da permissão (ex: processo.criar)',
                    max_length=100,
                    unique=True
                )),
                ('nome', models.CharField(help_text='Nome legível da permissão', max_length=200)),
                ('descricao', models.TextField(blank=True, help_text='Descrição da permissão')),
                ('recurso', models.CharField(
                    db_index=True,
                    help_text='Recurso (processo, chat, etc.)',
                    max_length=50
                )),
                ('acao', models.CharField(
                    db_index=True,
                    help_text='Ação (criar, editar, excluir, visualizar)',
                    max_length=50
                )),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Permissão',
                'verbose_name_plural': 'Permissões',
                'db_table': 'processos_permission',
                'unique_together': {('recurso', 'acao')},
            },
        ),

        # ================================================
        # Tabela: RolePermission
        # ================================================
        migrations.CreateModel(
            name='RolePermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('permission', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='roles',
                    to='processos.permission'
                )),
                ('role', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='permissions',
                    to='processos.role'
                )),
            ],
            options={
                'verbose_name': 'Role-Permissão',
                'verbose_name_plural': 'Roles-Permissões',
                'db_table': 'processos_role_permission',
                'unique_together': {('role', 'permission')},
            },
        ),

        # ================================================
        # Tabela: UserRole
        # ================================================
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ativo', models.BooleanField(default=True, help_text='Se a atribuição está ativa')),
                ('data_inicio', models.DateField(blank=True, help_text='Data de início da atribuição', null=True)),
                ('data_fim', models.DateField(
                    blank=True,
                    help_text='Data de fim da atribuição (null = permanente)',
                    null=True
                )),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('orgao', models.ForeignKey(
                    help_text='Órgão onde a role é válida',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='user_roles',
                    to='processos.orgao'
                )),
                ('role', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='user_assignments',
                    to='processos.role'
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='roles',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Atribuição de Role',
                'verbose_name_plural': 'Atribuições de Roles',
                'db_table': 'processos_user_role',
                'unique_together': {('user', 'role', 'orgao')},
            },
        ),

        # ================================================
        # Índices para performance
        # ================================================
        migrations.AddIndex(
            model_name='permission',
            index=models.Index(fields=['recurso', 'acao'], name='processos_p_recurso_idx'),
        ),
        migrations.AddIndex(
            model_name='userrole',
            index=models.Index(fields=['user', 'orgao', 'ativo'], name='processos_u_user_or_idx'),
        ),

        # ================================================
        # Popular dados iniciais (Roles e Permissions padrão)
        # ================================================
        migrations.RunPython(
            code=populate_default_roles_and_permissions,
            reverse_code=migrations.RunPython.noop
        ),
    ]
