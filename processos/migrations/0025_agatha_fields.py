"""
Campos Agatha 3.0 em RiscoIdentificado e RespostaRisco.

Todos opcionais/nullable — sem impacto em dados existentes.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("processos", "0024_userprofile_accessapproval"),
    ]

    operations = [
        # --- RiscoIdentificado: 8 campos ---
        migrations.AddField(
            model_name="riscoidentificado",
            name="causas",
            field=models.JSONField(blank=True, default=list, help_text="Lista de causas do evento de risco"),
        ),
        migrations.AddField(
            model_name="riscoidentificado",
            name="consequencias",
            field=models.JSONField(blank=True, default=list, help_text="Lista de consequencias do evento de risco"),
        ),
        migrations.AddField(
            model_name="riscoidentificado",
            name="controles_existentes",
            field=models.JSONField(blank=True, default=list, help_text="[{descricao, desenho, operacao}] - tripe Agatha"),
        ),
        migrations.AddField(
            model_name="riscoidentificado",
            name="tipo_avaliacao",
            field=models.CharField(
                choices=[("INERENTE", "INERENTE"), ("RESIDUAL_ATUAL", "RESIDUAL_ATUAL")],
                default="RESIDUAL_ATUAL",
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name="riscoidentificado",
            name="probabilidade_pos_plano",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="riscoidentificado",
            name="impacto_pos_plano",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="riscoidentificado",
            name="score_pos_plano",
            field=models.PositiveSmallIntegerField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="riscoidentificado",
            name="nivel_pos_plano",
            field=models.CharField(
                blank=True,
                choices=[("BAIXO", "BAIXO"), ("MEDIO", "MEDIO"), ("ALTO", "ALTO"), ("CRITICO", "CRITICO")],
                default="",
                editable=False,
                max_length=20,
            ),
        ),
        # --- RespostaRisco: 5 campos ---
        migrations.AddField(
            model_name="respostarisco",
            name="tipo_controle",
            field=models.CharField(
                blank=True,
                choices=[("PREVENTIVO", "PREVENTIVO"), ("CORRETIVO", "CORRETIVO")],
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="respostarisco",
            name="objetivo_controle",
            field=models.CharField(
                blank=True,
                choices=[("NOVO", "NOVO"), ("MELHORIA", "MELHORIA")],
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="respostarisco",
            name="como_implementar",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="respostarisco",
            name="data_inicio",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="respostarisco",
            name="data_conclusao_prevista",
            field=models.DateField(blank=True, null=True),
        ),
    ]
