# Generated manually for custom models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('processos', '0012_add_performance_indexes'),
    ]

    operations = [
        # Tabela de controle de índices (anti race-condition)
        migrations.CreateModel(
            name='ControleIndices',
            fields=[
                ('area_codigo', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('ultimo_indice', models.IntegerField(default=107)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'controle_indices',
                'verbose_name': 'Controle de Índices',
                'verbose_name_plural': 'Controles de Índices',
            },
        ),

        # Tabela de atividades sugeridas
        migrations.CreateModel(
            name='AtividadeSugerida',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cap_provisorio', models.CharField(max_length=50, unique=True)),
                ('cap_oficial', models.CharField(max_length=50, null=True, blank=True)),
                ('status', models.CharField(max_length=20, choices=[
                    ('sugerida', 'Sugerida'),
                    ('validada', 'Validada'),
                    ('rejeitada', 'Rejeitada'),
                    ('publicada', 'Publicada'),
                ])),

                # Arquitetura
                ('area_codigo', models.CharField(max_length=10)),
                ('macroprocesso', models.TextField()),
                ('processo', models.TextField()),
                ('subprocesso', models.TextField()),
                ('atividade', models.TextField()),
                ('entrega_esperada', models.TextField()),

                # Rastreabilidade (UTC)
                ('autor_cpf', models.CharField(max_length=14)),
                ('autor_nome', models.CharField(max_length=200)),
                ('autor_area', models.CharField(max_length=10)),
                ('data_sugestao_utc', models.DateTimeField()),
                ('descricao_original', models.TextField()),

                # Hash único (anti-duplicata antes da persistência)
                ('hash_sugestao', models.CharField(max_length=64, unique=True)),

                # Validação
                ('validador_cpf', models.CharField(max_length=14, null=True, blank=True)),
                ('validador_nome', models.CharField(max_length=200, null=True, blank=True)),
                ('data_validacao_utc', models.DateTimeField(null=True, blank=True)),
                ('comentario_validador', models.TextField(null=True, blank=True)),

                # Similaridade (sempre salvo, mesmo < 0.8)
                ('score_similaridade', models.FloatField(null=True, blank=True)),
                ('sugestoes_similares', models.JSONField(default=list, blank=True)),
                ('scores_similares_todos', models.JSONField(default=list, blank=True)),

                # Confiança da IA
                ('confianca', models.CharField(max_length=10, choices=[
                    ('alta', 'Alta'),
                    ('media', 'Média'),
                    ('baixa', 'Baixa'),
                ])),

                # Rastreabilidade do fluxo
                ('origem_fluxo', models.CharField(max_length=30)),  # 'match_exato', 'match_fuzzy', 'nova_atividade_ia'
                ('interacao_id', models.CharField(max_length=50)),

                # Timestamps
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'atividades_sugeridas',
                'verbose_name': 'Atividade Sugerida',
                'verbose_name_plural': 'Atividades Sugeridas',
                'ordering': ['-data_sugestao_utc'],
            },
        ),

        # Tabela de histórico de alterações
        migrations.CreateModel(
            name='HistoricoAtividade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('atividade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='processos.atividadesugerida', related_name='historico')),
                ('tipo_evento', models.CharField(max_length=20, choices=[
                    ('criacao', 'Criação'),
                    ('edicao', 'Edição'),
                    ('aprovacao', 'Aprovação'),
                    ('rejeicao', 'Rejeição'),
                    ('mesclagem', 'Mesclagem'),
                ])),
                ('usuario_cpf', models.CharField(max_length=14)),
                ('usuario_nome', models.CharField(max_length=200)),
                ('data_evento_utc', models.DateTimeField(auto_now_add=True)),
                ('alteracoes_json', models.JSONField(default=dict, blank=True)),
                ('comentario', models.TextField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'historico_atividades',
                'verbose_name': 'Histórico de Atividade',
                'verbose_name_plural': 'Históricos de Atividades',
                'ordering': ['-data_evento_utc'],
            },
        ),

        # Índices para performance
        migrations.AddIndex(
            model_name='atividadesugerida',
            index=models.Index(fields=['status'], name='idx_status'),
        ),
        migrations.AddIndex(
            model_name='atividadesugerida',
            index=models.Index(fields=['area_codigo'], name='idx_area'),
        ),
        migrations.AddIndex(
            model_name='atividadesugerida',
            index=models.Index(fields=['autor_cpf'], name='idx_autor'),
        ),
        migrations.AddIndex(
            model_name='historicoatividade',
            index=models.Index(fields=['atividade'], name='idx_atividade_hist'),
        ),
        migrations.AddIndex(
            model_name='historicoatividade',
            index=models.Index(fields=['data_evento_utc'], name='idx_data_evento'),
        ),

        # Popular tabela controle_indices com as 8 áreas (SQLite compatible)
        migrations.RunSQL(
            sql="""
                INSERT INTO controle_indices (area_codigo, ultimo_indice, updated_at) VALUES
                ('CGBEN', 107, datetime('now')),
                ('CGPAG', 107, datetime('now')),
                ('COATE', 107, datetime('now')),
                ('CGGAF', 107, datetime('now')),
                ('DIGEP', 107, datetime('now')),
                ('CGRIS', 107, datetime('now')),
                ('CGCAF', 107, datetime('now')),
                ('CGECO', 107, datetime('now'));
            """,
            reverse_sql="DELETE FROM controle_indices WHERE area_codigo IN ('CGBEN', 'CGPAG', 'COATE', 'CGGAF', 'DIGEP', 'CGRIS', 'CGCAF', 'CGECO');"
        ),
    ]
