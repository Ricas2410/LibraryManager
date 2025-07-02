import os
import zipfile
from django.conf import settings
from django.core.management.base import BaseCommand

BACKUP_DIR = os.path.join(settings.BASE_DIR, 'backups')

class Command(BaseCommand):
    help = 'Restore system from a backup zip file.'

    def add_arguments(self, parser):
        parser.add_argument('backup_file', type=str, help='Path to the backup zip file')

    def handle(self, *args, **options):
        backup_file = options['backup_file']
        if not os.path.exists(backup_file):
            self.stdout.write(self.style.ERROR(f'Backup file not found: {backup_file}'))
            return
        with zipfile.ZipFile(backup_file, 'r') as backup_zip:
            for member in backup_zip.namelist():
                if member.startswith('db/'):
                    db_dest = settings.DATABASES['default']['NAME']
                    backup_zip.extract(member, settings.BASE_DIR)
                    os.replace(os.path.join(settings.BASE_DIR, member), db_dest)
                elif member.startswith('media/'):
                    backup_zip.extract(member, settings.MEDIA_ROOT)
                elif member == 'settings.py':
                    settings_dest = os.path.join(settings.BASE_DIR, 'library_management', 'settings.py')
                    backup_zip.extract(member, settings.BASE_DIR)
                    os.replace(os.path.join(settings.BASE_DIR, member), settings_dest)
                elif member == '.env':
                    env_dest = os.path.join(settings.BASE_DIR, '.env')
                    backup_zip.extract(member, settings.BASE_DIR)
                    os.replace(os.path.join(settings.BASE_DIR, member), env_dest)
        self.stdout.write(self.style.SUCCESS('System restored from backup.'))
