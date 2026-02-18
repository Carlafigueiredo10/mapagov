"""
Migração SNI: normaliza prefixos de área para 2 dígitos.

- Area.prefixo: "1" -> "01", "5.1" -> "05.01"
- POP.codigo_processo: "1.02.03.04.108" -> "01.02.03.04.108"

Irreversível (RunPython.noop) — não há como "desnormalizar" sem ambiguidade.
"""

from django.db import migrations

from processos.domain.governanca.normalize import normalize_area_prefix, normalize_cap


def forward(apps, schema_editor):
    Area = apps.get_model('processos', 'Area')
    POP = apps.get_model('processos', 'POP')

    # Areas — bulk_update em lotes de 500
    areas = list(Area.objects.all().iterator())
    for area in areas:
        area.prefixo = normalize_area_prefix(area.prefixo)
    if areas:
        Area.objects.bulk_update(areas, ['prefixo'], batch_size=500)

    # POPs — bulk_update em lotes de 500
    pops = list(
        POP.objects.exclude(codigo_processo__isnull=True)
                   .exclude(codigo_processo='')
                   .iterator()
    )
    for pop in pops:
        pop.codigo_processo = normalize_cap(pop.codigo_processo)
    if pops:
        POP.objects.bulk_update(pops, ['codigo_processo'], batch_size=500)


class Migration(migrations.Migration):

    dependencies = [
        ('processos', '0025_agatha_fields'),
    ]

    operations = [
        migrations.RunPython(forward, migrations.RunPython.noop),
    ]
