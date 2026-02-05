"""
Migration: Remove RESGUARDAR strategy

Alinha o sistema ao Guia de Gestao de Riscos do MGI.
RESGUARDAR nao existe no Guia - era interpretacao local.

Operacoes:
1. Data migration: RESGUARDAR -> ACEITAR (idempotente)
2. Altera choices do campo estrategia para 4 valores oficiais
"""
from django.db import migrations, models


def forward_resguardar_to_aceitar(apps, schema_editor):
    """
    Converte respostas com RESGUARDAR para ACEITAR.
    Idempotente: seguro rodar multiplas vezes.
    """
    RespostaRisco = apps.get_model("processos", "RespostaRisco")
    updated = RespostaRisco.objects.filter(estrategia="RESGUARDAR").update(
        estrategia="ACEITAR"
    )
    if updated > 0:
        print(f"\n  -> Convertidos {updated} registros de RESGUARDAR para ACEITAR")


def backward_noop(apps, schema_editor):
    """
    Nao reverte: ACEITAR e semanticamente correto.
    Reverter criaria inconsistencia.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("processos", "0017_analise_riscos_v2"),
    ]

    operations = [
        # 1. Data migration primeiro (antes de alterar choices)
        migrations.RunPython(forward_resguardar_to_aceitar, backward_noop),

        # 2. Alterar choices para 4 estrategias oficiais do Guia MGI
        migrations.AlterField(
            model_name="respostarisco",
            name="estrategia",
            field=models.CharField(
                max_length=20,
                choices=[
                    ("MITIGAR", "MITIGAR"),
                    ("EVITAR", "EVITAR"),
                    ("COMPARTILHAR", "COMPARTILHAR"),
                    ("ACEITAR", "ACEITAR"),
                ],
            ),
        ),
    ]
