"""
Management command: cria superuser inicial com profile approved + verified.
Para bootstrap do sistema de autenticacao.

Uso:
    python manage.py create_admin --email admin@gestao.gov.br --password SenhaSegura123
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Cria superuser inicial com perfil aprovado e email verificado'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help='Email do administrador')
        parser.add_argument('--password', required=True, help='Senha do administrador')
        parser.add_argument('--nome', default='Administrador', help='Nome completo')

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        password = options['password']
        nome = options['nome']

        if User.objects.filter(email=email).exists():
            self.stderr.write(self.style.WARNING(f'Usuario com email {email} ja existe.'))
            return

        username = email.split('@')[0]
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name=nome.split()[0] if nome else '',
            last_name=' '.join(nome.split()[1:]) if nome else '',
        )

        # Profile ja criado pelo signal, mas garantir status
        profile = user.profile
        profile.email_verified = True
        profile.access_status = 'approved'
        profile.nome_completo = nome
        from django.utils import timezone
        profile.email_verified_at = timezone.now()
        profile.approved_at = timezone.now()
        profile.save()

        self.stdout.write(self.style.SUCCESS(
            f'Admin criado: {email} (superuser, verificado, aprovado)'
        ))
