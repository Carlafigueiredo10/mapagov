from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('processos', '0020_unique_cap_ativo'),
    ]

    operations = [
        migrations.CreateModel(
            name='PopDraft',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(db_index=True, help_text='Session ID do frontend (fallback quando user é null)', max_length=255, verbose_name='ID da Sessão')),
                ('area', models.CharField(blank=True, default='', max_length=255, verbose_name='Área organizacional')),
                ('process_code', models.CharField(blank=True, default='', max_length=50, verbose_name='Código do processo (ex: 7.1.1.1)')),
                ('etapa_atual', models.CharField(default='nome_usuario', max_length=50, verbose_name='Etapa atual do wizard')),
                ('payload_json', models.JSONField(default=dict, help_text='Tudo que o usuário já respondeu (estado da state machine)', verbose_name='Dados coletados')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pop_drafts', to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Rascunho POP',
                'verbose_name_plural': 'Rascunhos POP',
                'ordering': ['-updated_at'],
                'indexes': [
                    models.Index(fields=['session_id'], name='processos_p_session_idx'),
                    models.Index(fields=['user', '-updated_at'], name='processos_p_user_up_idx'),
                ],
            },
        ),
    ]
