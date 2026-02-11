"""
Management command: auto-rejeita usuarios pendentes com mais de N dias.
Para execucao periodica via cron/scheduler.

Uso:
    python manage.py cleanup_pending_users
    python manage.py cleanup_pending_users --days 60
    python manage.py cleanup_pending_users --dry-run

DESATIVADO temporariamente. Descomentar handle() para ativar.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from processos.models_auth import UserProfile


class Command(BaseCommand):
    help = 'Auto-rejeita usuarios pendentes com mais de N dias sem aprovacao (DESATIVADO)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Dias de inatividade antes de rejeitar (default: 30)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas lista usuarios que seriam rejeitados, sem alterar',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING(
            'Command desativado temporariamente.'
        ))

    # def handle_active(self, *args, **options):
    #     days = options['days']
    #     dry_run = options['dry_run']
    #     cutoff = timezone.now() - timedelta(days=days)
    #
    #     pending = UserProfile.objects.filter(
    #         access_status='pending',
    #         created_at__lt=cutoff,
    #     ).select_related('user')
    #
    #     count = pending.count()
    #
    #     if count == 0:
    #         self.stdout.write('Nenhum usuario pendente com mais de %d dias.' % days)
    #         return
    #
    #     if dry_run:
    #         self.stdout.write(self.style.WARNING(
    #             '[DRY RUN] %d usuario(s) seriam rejeitados:' % count
    #         ))
    #         for p in pending:
    #             self.stdout.write(
    #                 '  - %s (%s) — pendente desde %s'
    #                 % (p.user.email, p.nome_completo, p.created_at.strftime('%Y-%m-%d'))
    #             )
    #         return
    #
    #     now = timezone.now()
    #     updated = pending.update(
    #         access_status='rejected',
    #         rejected_at=now,
    #     )
    #
    #     self.stdout.write(self.style.SUCCESS(
    #         '%d usuario(s) pendente(s) rejeitado(s) (mais de %d dias).' % (updated, days)
    #     ))
