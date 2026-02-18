"""
Migração CP (Código de Produto) para produtos não-POP.

1. Cria tabela controle_indices_produto (lock transacional por área+produto)
2. Adiciona codigo_cp + produto_codigo em AnaliseRiscos
3. Adiciona codigo_cp + produto_codigo em PlanejamentoEstrategico
4. UniqueConstraints parciais (excluem NULL/vazio; PE exclui cancelado)

Dados existentes NÃO são migrados — CP gerado sob demanda no próximo save.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("processos", "0026_migrate_sni_prefixes"),
    ]

    operations = [
        # 1. Tabela ControleIndicesProduto
        migrations.CreateModel(
            name="ControleIndicesProduto",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("area_codigo", models.CharField(max_length=10)),
                ("produto_codigo", models.CharField(max_length=2)),
                ("ultimo_indice", models.IntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "controle_indices_produto",
                "verbose_name": "Controle de Índices (Produto)",
                "verbose_name_plural": "Controles de Índices (Produto)",
            },
        ),
        migrations.AddConstraint(
            model_name="controleIndicesproduto",
            constraint=models.UniqueConstraint(
                fields=["area_codigo", "produto_codigo"],
                name="unique_area_produto",
            ),
        ),

        # 2. Campos em AnaliseRiscos
        migrations.AddField(
            model_name="analiseriscos",
            name="codigo_cp",
            field=models.CharField(
                blank=True, max_length=20, null=True,
                verbose_name="Código de Produto (CP)",
            ),
        ),
        migrations.AddField(
            model_name="analiseriscos",
            name="produto_codigo",
            field=models.CharField(
                default="01", max_length=2,
                verbose_name="Código do tipo de produto",
            ),
        ),
        migrations.AddConstraint(
            model_name="analiseriscos",
            constraint=models.UniqueConstraint(
                condition=~models.Q(codigo_cp=None) & ~models.Q(codigo_cp=""),
                fields=["codigo_cp"],
                name="unique_cp_analise_riscos",
            ),
        ),

        # 3. Campos em PlanejamentoEstrategico
        migrations.AddField(
            model_name="planejamentoestrategico",
            name="codigo_cp",
            field=models.CharField(
                blank=True, max_length=20, null=True,
                verbose_name="Código de Produto (CP)",
            ),
        ),
        migrations.AddField(
            model_name="planejamentoestrategico",
            name="produto_codigo",
            field=models.CharField(
                default="02", max_length=2,
                verbose_name="Código do tipo de produto",
            ),
        ),
        migrations.AddConstraint(
            model_name="planejamentoestrategico",
            constraint=models.UniqueConstraint(
                condition=~models.Q(codigo_cp=None) & ~models.Q(codigo_cp="") & ~models.Q(status="cancelado"),
                fields=["codigo_cp"],
                name="unique_cp_planejamento",
            ),
        ),
    ]
