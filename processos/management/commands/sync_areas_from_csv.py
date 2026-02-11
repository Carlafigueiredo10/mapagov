"""
Sincroniza areas organizacionais do CSV para o banco.
Idempotente: usa update_or_create por codigo.

Uso:
    python manage.py sync_areas_from_csv
    python manage.py sync_areas_from_csv --dry-run
"""

import csv
import os

from django.core.management.base import BaseCommand
from processos.models import Area


class Command(BaseCommand):
    help = "Sincroniza areas organizacionais do CSV (documentos_base/areas_organizacionais.csv) para o banco."

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Mostra o que faria sem aplicar.')

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        csv_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..',
            'documentos_base', 'areas_organizacionais.csv'
        )

        if not os.path.exists(csv_path):
            self.stderr.write(self.style.ERROR(f"CSV nao encontrado: {csv_path}"))
            return

        criados = 0
        atualizados = 0
        area_map = {}

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                codigo = row['codigo'].strip()
                if not codigo:
                    continue

                defaults = {
                    'nome': row['nome_completo'].strip(),
                    'nome_curto': row['nome_curto'].strip(),
                    'slug': codigo.lower(),
                    'prefixo': row['prefixo'].strip(),
                    'ordem': float(row['ordem']),
                    'ativo': row['ativo'].strip().lower() == 'true',
                    'descricao': row['descricao'].strip().strip('"'),
                    'tem_subareas': row['tem_subareas'].strip().lower() == 'true',
                }

                if dry_run:
                    exists = Area.objects.filter(codigo=codigo).exists()
                    action = 'UPDATE' if exists else 'CREATE'
                    self.stdout.write(f"  [{action}] {codigo} - {defaults['nome_curto']}")
                else:
                    _, created = Area.objects.update_or_create(
                        codigo=codigo,
                        defaults=defaults,
                    )
                    if created:
                        criados += 1
                    else:
                        atualizados += 1

                area_map[codigo] = row.get('area_pai', '').strip()

        # Segunda passada: linkar area_pai
        if not dry_run:
            for codigo, pai_codigo in area_map.items():
                if pai_codigo:
                    try:
                        area = Area.objects.get(codigo=codigo)
                        pai = Area.objects.get(codigo=pai_codigo)
                        if area.area_pai_id != pai.id:
                            area.area_pai = pai
                            area.save(update_fields=['area_pai'])
                    except Area.DoesNotExist:
                        pass

        if dry_run:
            self.stdout.write(self.style.NOTICE("DRY RUN - nenhuma alteracao aplicada."))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Sync concluido: {criados} criados, {atualizados} atualizados."
            ))
