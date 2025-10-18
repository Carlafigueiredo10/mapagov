import json
import os
from datetime import datetime
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.core import serializers as dj_serializers
from django.conf import settings
from processos.models import POP, POPSnapshot, POPChangeLog
from processos.utils.backup_storage import build_uploader_from_env, BackupUploaderError


class Command(BaseCommand):
    help = "Gera backup lógico (JSON) de POPs, snapshots e changelog em backups/YYYY/MM/DD/"

    def add_arguments(self, parser):
        parser.add_argument(
            '--include-deleted', action='store_true', help='Inclui POPs soft-deleted'
        )
        parser.add_argument(
            '--no-snapshots', action='store_true', help='Não inclui snapshots (reduz tamanho)'
        )
        parser.add_argument(
            '--no-changelog', action='store_true', help='Não inclui changelog'
        )
        parser.add_argument(
            '--output-dir', type=str, help='Diretório base para backups (default: ./backups)'
        )
        parser.add_argument(
            '--tag', type=str, help='Tag opcional para facilitar identificação (ex: pre-migration)'
        )
        parser.add_argument(
            '--pretty', action='store_true', help='Formata JSON com indent=2 (maior tamanho)'
        )
        parser.add_argument(
            '--limit', type=int, help='Limita quantidade de POPs (debug)'
        )
        parser.add_argument(
            '--upload', action='store_true', help='Força upload após gerar backup (mesmo se BACKUP_UPLOAD_AUTO desligado)'
        )
        parser.add_argument(
            '--no-upload', action='store_true', help='Inibe upload mesmo se BACKUP_UPLOAD_AUTO=1'
        )

    def handle(self, *args, **options):
        base_dir = options.get('output-dir') or 'backups'
        now = datetime.utcnow()
        dated_path = Path(base_dir) / now.strftime('%Y') / now.strftime('%m') / now.strftime('%d')
        dated_path.mkdir(parents=True, exist_ok=True)

        tag = options.get('tag')
        timestamp = now.strftime('%Y%m%dT%H%M%SZ')

        pop_qs = POP.objects.all()
        if not options.get('include_deleted', False):
            pop_qs = pop_qs.filter(is_deleted=False)
        if options.get('limit'):
            pop_qs = pop_qs.order_by('-updated_at')[: options['limit']]

        pop_filename = f"pops_{timestamp}{'_' + tag if tag else ''}.json"
        snapshot_filename = f"pop_snapshots_{timestamp}{'_' + tag if tag else ''}.json"
        changelog_filename = f"pop_changelog_{timestamp}{'_' + tag if tag else ''}.json"

        indent = 2 if options.get('pretty', False) else None

        # Serializar POPs
        self._dump_queryset(pop_qs, dated_path / pop_filename, indent)
        self.stdout.write(self.style.SUCCESS(f"POPs salvos em {dated_path / pop_filename}"))

        if not options.get('no-snapshots', False):
            snapshot_qs = POPSnapshot.objects.filter(pop__in=pop_qs)
            self._dump_queryset(snapshot_qs, dated_path / snapshot_filename, indent)
            self.stdout.write(self.style.SUCCESS(f"Snapshots salvos em {dated_path / snapshot_filename}"))

        if not options.get('no-changelog', False):
            changelog_qs = POPChangeLog.objects.filter(pop__in=pop_qs)
            self._dump_queryset(changelog_qs, dated_path / changelog_filename, indent)
            self.stdout.write(self.style.SUCCESS(f"ChangeLog salvo em {dated_path / changelog_filename}"))

        meta = {
            'generated_at': timestamp,
            'pop_count': pop_qs.count(),
            'includes_snapshots': not options.get('no-snapshots', False),
            'includes_changelog': not options.get('no-changelog', False),
            'tag': tag,
            'deleted_included': options.get('include_deleted', False),
            'limit': options.get('limit'),
            'django_version': settings.VERSION if hasattr(settings, 'VERSION') else None,
        }
        with open(dated_path / f"meta_{timestamp}{'_' + tag if tag else ''}.json", 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=indent, ensure_ascii=False)

        generated_files = [
            dated_path / pop_filename,
        ]
        if not options.get('no-snapshots', False):
            generated_files.append(dated_path / snapshot_filename)
        if not options.get('no-changelog', False):
            generated_files.append(dated_path / changelog_filename)
        generated_files.append(dated_path / f"meta_{timestamp}{'_' + tag if tag else ''}.json")

        do_auto = os.getenv('BACKUP_UPLOAD_AUTO', '0') in ('1','true','True')
        force_upload = options.get('upload', False)
        skip_upload = options.get('no-upload', False)

        if (do_auto or force_upload) and not skip_upload:
            try:
                uploader = build_uploader_from_env()
                prefix = f"{now.strftime('%Y/%m/%d')}"  # mesma estrutura
                uploader.upload_files(generated_files, prefix=prefix)
                self.stdout.write(self.style.SUCCESS("Upload concluído."))
            except BackupUploaderError as e:
                self.stderr.write(self.style.ERROR(f"Falha upload: {e}"))
            except Exception as e:  # noqa
                self.stderr.write(self.style.ERROR(f"Erro inesperado upload: {e}"))

        self.stdout.write(self.style.SUCCESS("Backup concluído."))

    def _dump_queryset(self, qs, filepath: Path, indent=None):
        data = dj_serializers.serialize('json', qs)
        if indent:
            # Pretty print
            json_data = json.loads(data)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=indent, ensure_ascii=False)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(data)
