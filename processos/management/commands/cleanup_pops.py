import sys
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from processos.models import POP, POPSnapshot, POPChangeLog

class Command(BaseCommand):
    help = "Limpa POPs em draft inativos e snapshots não milestone antigos para controle de volume."

    def add_arguments(self, parser):
        parser.add_argument('--days-draft', type=int, default=30, help='Dias de inatividade para remover POP draft/in_progress (soft delete).')
        parser.add_argument('--days-snapshot', type=int, default=90, help='Dias para remover snapshots antigos não milestone.')
        parser.add_argument('--keep-last', type=int, default=10, help='Quantidade de snapshots recentes por POP que sempre serão mantidos.')
        parser.add_argument('--dry-run', action='store_true', help='Mostra o que faria sem aplicar mudanças.')

    def handle(self, *args, **options):
        days_draft = options['days_draft']
        days_snapshot = options['days_snapshot']
        keep_last = options['keep_last']
        dry_run = options['dry_run']

        now = timezone.now()
        cutoff_draft = now - timedelta(days=days_draft)
        cutoff_snapshot = now - timedelta(days=days_snapshot)

        self.stdout.write(self.style.NOTICE(f"Iniciando cleanup_pops (draft>{days_draft}d, snapshots>{days_snapshot}d, keep_last={keep_last}, dry_run={dry_run})"))

        # 1. Soft delete POPs em draft inativos
        pops_qs = POP.objects.filter(is_deleted=False, status='draft', last_activity_at__lt=cutoff_draft)
        pops_count = pops_qs.count()

        # 2. Snapshots não milestone antigos
        snapshots_deleted_total = 0
        pops_soft_deleted = 0

        # 3. Processar POPs
        for pop in pops_qs.iterator(chunk_size=200):
            pops_soft_deleted += 1
            if not dry_run:
                pop.is_deleted = True
                pop.save(update_fields=['is_deleted'])

        self.stdout.write(self.style.WARNING(f"POPs soft-deletados: {pops_soft_deleted}"))

        # 4. Snapshots: para cada POP ativo ou arquivado
        pops_for_snapshots = POP.objects.filter(is_deleted=False)
        for pop in pops_for_snapshots.iterator(chunk_size=200):
            snaps = list(pop.snapshots.order_by('-created_at'))
            if len(snaps) <= keep_last:
                continue
            # Manter últimos keep_last SEMPRE + todos milestone + recentes dentro do período
            preserve_ids = set()
            for s in snaps[:keep_last]:
                preserve_ids.add(s.id)
            for s in snaps:
                if s.milestone:
                    preserve_ids.add(s.id)
            for s in snaps:
                if s.created_at >= cutoff_snapshot:
                    preserve_ids.add(s.id)
            # Deletar o resto
            for s in snaps:
                if s.id not in preserve_ids:
                    if not dry_run:
                        s.delete()
                    snapshots_deleted_total += 1

        self.stdout.write(self.style.WARNING(f"Snapshots removidos: {snapshots_deleted_total}"))

        # 5. Estatísticas de ChangeLog (não removendo ainda)
        changelog_total = POPChangeLog.objects.count()
        self.stdout.write(self.style.NOTICE(f"Total de change logs (sem ação): {changelog_total}"))

        self.stdout.write(self.style.SUCCESS("Cleanup concluído."))
