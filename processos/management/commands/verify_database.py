from django.core.management.base import BaseCommand
from django.db import connections
from django.conf import settings
from processos.models import POP, POPSnapshot, POPChangeLog
from django.db import DatabaseError
import time


class Command(BaseCommand):
    help = "Verifica saúde do banco: engine, conexão, contagens e proporções básicas. Código de saída !=0 indica problema."

    def add_arguments(self, parser):
        parser.add_argument('--max-latency-ms', type=int, default=500, help='Limite de latência aceitável para SELECT simples.')
        parser.add_argument('--warn-snapshot-ratio', type=float, default=25.0, help='Percentual máximo snapshots/POPs antes de warning.')

    def handle(self, *args, **options):
        default_db = settings.DATABASES['default']
        engine = default_db['ENGINE']
        if engine.endswith('sqlite3') and not settings.DEBUG:
            self.stderr.write(self.style.ERROR('ERRO: Produção usando SQLite.'))
            return 2
        else:
            self.stdout.write(self.style.SUCCESS(f"Engine: {engine}"))

        # Testar conexão e latência
        cursor = connections['default'].cursor()
        start = time.time()
        try:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        except DatabaseError as e:
            self.stderr.write(self.style.ERROR(f'Falha ao executar SELECT 1: {e}'))
            return 3
        latency_ms = (time.time() - start) * 1000
        if latency_ms > options['max_latency_ms']:
            self.stderr.write(self.style.WARNING(f'ALERTA: Latência {latency_ms:.1f} ms > limite {options['max_latency_ms']} ms'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Latência OK: {latency_ms:.1f} ms'))

        pop_count = POP.objects.count()
        snapshot_count = POPSnapshot.objects.count()
        changelog_count = POPChangeLog.objects.count()

        self.stdout.write(f'POPs: {pop_count}')
        self.stdout.write(f'Snapshots: {snapshot_count}')
        self.stdout.write(f'ChangeLog entries: {changelog_count}')

        exit_code = 0
        if pop_count > 0:
            ratio = (snapshot_count / pop_count) * 100
            if ratio > options['warn_snapshot_ratio']:
                self.stderr.write(self.style.WARNING(f'ALERTA: Ratio snapshots/POPs = {ratio:.1f}% > {options['warn_snapshot_ratio']}% - considere cleanup.'))
                exit_code = max(exit_code, 1)

        # Verificação de integridade hash básica (amostra)
        sample = POP.objects.order_by('-updated_at')[:10]
        mismatches = []
        for pop in sample:
            try:
                current_hash = pop.compute_integrity_hash()
                if pop.integrity_hash and pop.integrity_hash != current_hash:
                    mismatches.append(pop.id)
            except Exception as e:
                self.stderr.write(self.style.WARNING(f'Falha hash POP {pop.id}: {e}'))
                exit_code = max(exit_code, 1)
        if mismatches:
            self.stderr.write(self.style.ERROR(f'Integridade divergente em POP IDs: {mismatches}'))
            exit_code = max(exit_code, 2)
        else:
            self.stdout.write(self.style.SUCCESS('Integridade (amostra) OK'))

        if exit_code == 0:
            self.stdout.write(self.style.SUCCESS('Verificação concluída sem erros.'))
        return exit_code
