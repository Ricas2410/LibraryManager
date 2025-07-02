import os
import shutil
import zipfile
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

BACKUP_DIR = os.path.join(settings.BASE_DIR, 'backups')

class Command(BaseCommand):
    help = 'Create a full system backup (database, media, settings)' 

    def handle(self, *args, **options):
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'backup_{timestamp}.zip'
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        os.makedirs(BACKUP_DIR, exist_ok=True)

        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
            # Add database
            db_path = settings.DATABASES['default']['NAME']
            if os.path.exists(db_path):
                backup_zip.write(db_path, os.path.join('db', os.path.basename(db_path)))
            # Add media
            for folder, _, files in os.walk(settings.MEDIA_ROOT):
                for file in files:
                    abs_path = os.path.join(folder, file)
                    rel_path = os.path.relpath(abs_path, settings.MEDIA_ROOT)
                    backup_zip.write(abs_path, os.path.join('media', rel_path))
            # Add settings
            backup_zip.write(settings.SETTINGS_MODULE.replace('.', '/')+'.py', 'settings.py')
            # Add .env
            env_path = os.path.join(settings.BASE_DIR, '.env')
            if os.path.exists(env_path):
                backup_zip.write(env_path, '.env')
        self.stdout.write(self.style.SUCCESS(f'Backup created: {backup_path}'))
