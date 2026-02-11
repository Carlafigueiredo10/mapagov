# Data migration: popula Area a partir do CSV e linka POPs existentes.
# Tambem normaliza status vestigiais (in_progress/review/approved) -> draft.

import csv
import os

from django.db import migrations


def populate_areas_and_link_pops(apps, schema_editor):
    Area = apps.get_model('processos', 'Area')
    POP = apps.get_model('processos', 'POP')

    csv_path = os.path.join(
        os.path.dirname(__file__), '..', '..', 'documentos_base', 'areas_organizacionais.csv'
    )

    area_map = {}

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            codigo = row['codigo'].strip()
            if not codigo:
                continue

            area, _ = Area.objects.update_or_create(
                codigo=codigo,
                defaults={
                    'nome': row['nome_completo'].strip(),
                    'nome_curto': row['nome_curto'].strip(),
                    'slug': codigo.lower(),
                    'prefixo': row['prefixo'].strip(),
                    'ordem': float(row['ordem']),
                    'ativo': row['ativo'].strip().lower() == 'true',
                    'descricao': row['descricao'].strip().strip('"'),
                    'tem_subareas': row['tem_subareas'].strip().lower() == 'true',
                },
            )
            area_map[codigo] = area

    # Segunda passada: linkar area_pai (ex.: DIGEP-RO -> DIGEP)
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            codigo = row['codigo'].strip()
            pai_codigo = row.get('area_pai', '').strip()
            if pai_codigo and codigo in area_map and pai_codigo in area_map:
                area = area_map[codigo]
                area.area_pai = area_map[pai_codigo]
                area.save(update_fields=['area_pai'])

    # Linkar POPs existentes: match area_codigo -> Area
    for pop in POP.objects.filter(is_deleted=False).exclude(area_codigo=None).exclude(area_codigo=''):
        matched = Area.objects.filter(codigo=pop.area_codigo).first()
        if matched:
            pop.area = matched
            pop.save(update_fields=['area'])

    # Normalizar status vestigiais -> draft
    vestigiais = ['in_progress', 'review', 'approved']
    POP.objects.filter(status__in=vestigiais).update(status='draft')


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('processos', '0022_area_pop_fk'),
    ]

    operations = [
        migrations.RunPython(populate_areas_and_link_pops, reverse_noop),
    ]
