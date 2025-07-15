"""
Management command to migrate existing images from local storage to Cloudinary
"""
import os
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from library.models import Book, LibrarySettings
import cloudinary.uploader


class Command(BaseCommand):
    help = 'Migrate existing images from local storage to Cloudinary'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Migrate book cover images
        self.migrate_book_covers(dry_run)
        
        # Migrate library logos
        self.migrate_library_logos(dry_run)
        
        self.stdout.write(self.style.SUCCESS('Migration completed!'))

    def migrate_book_covers(self, dry_run=False):
        """Migrate book cover images to Cloudinary"""
        self.stdout.write('Migrating book cover images...')
        
        books_with_images = Book.objects.filter(cover_image__isnull=False)
        total_books = books_with_images.count()
        
        if total_books == 0:
            self.stdout.write('No book cover images to migrate.')
            return
        
        self.stdout.write(f'Found {total_books} books with cover images')
        
        migrated = 0
        errors = 0
        
        for i, book in enumerate(books_with_images, 1):
            try:
                # Check if image path looks like a local path
                image_path = str(book.cover_image)
                if not image_path.startswith('book_covers/'):
                    self.stdout.write(f'Skipping {book.title} - already migrated or invalid path')
                    continue
                
                self.stdout.write(f'[{i}/{total_books}] Migrating: {book.title}')
                
                if dry_run:
                    self.stdout.write(f'  Would migrate: {image_path}')
                    continue
                
                # Try to get the image content
                image_content = self.get_image_content(book.cover_image)
                if not image_content:
                    self.stdout.write(f'  ERROR: Could not get image content for {book.title}')
                    errors += 1
                    continue
                
                # Upload to Cloudinary
                filename = os.path.basename(image_path)
                name_without_ext = os.path.splitext(filename)[0]
                
                # Upload to Cloudinary with a clean public_id
                result = cloudinary.uploader.upload(
                    image_content,
                    public_id=f"book_covers/{name_without_ext}",
                    folder="book_covers",
                    overwrite=True,
                    resource_type="image"
                )
                
                # Update the book with the new Cloudinary URL
                cloudinary_url = result['secure_url']
                
                # Save the Cloudinary public_id as the image field
                # The cloudinary storage will handle URL generation
                book.cover_image = f"book_covers/{name_without_ext}.jpg"
                book.save()
                
                self.stdout.write(f'  SUCCESS: Migrated to {cloudinary_url}')
                migrated += 1
                
            except Exception as e:
                self.stdout.write(f'  ERROR: Failed to migrate {book.title}: {str(e)}')
                errors += 1
        
        self.stdout.write(f'Book covers migration complete: {migrated} migrated, {errors} errors')

    def migrate_library_logos(self, dry_run=False):
        """Migrate library logos to Cloudinary"""
        self.stdout.write('Migrating library logos...')
        
        settings_with_logos = LibrarySettings.objects.filter(library_logo__isnull=False)
        
        if not settings_with_logos.exists():
            self.stdout.write('No library logos to migrate.')
            return
        
        for settings in settings_with_logos:
            try:
                logo_path = str(settings.library_logo)
                if not logo_path.startswith('library_logos/'):
                    self.stdout.write('Skipping logo - already migrated or invalid path')
                    continue
                
                self.stdout.write(f'Migrating library logo: {logo_path}')
                
                if dry_run:
                    self.stdout.write(f'  Would migrate: {logo_path}')
                    continue
                
                # Try to get the image content
                image_content = self.get_image_content(settings.library_logo)
                if not image_content:
                    self.stdout.write('  ERROR: Could not get logo content')
                    continue
                
                # Upload to Cloudinary
                filename = os.path.basename(logo_path)
                name_without_ext = os.path.splitext(filename)[0]
                
                result = cloudinary.uploader.upload(
                    image_content,
                    public_id=f"library_logos/{name_without_ext}",
                    folder="library_logos",
                    overwrite=True,
                    resource_type="image"
                )
                
                # Update the settings with the new Cloudinary URL
                cloudinary_url = result['secure_url']
                settings.library_logo = f"library_logos/{name_without_ext}.jpg"
                settings.save()
                
                self.stdout.write(f'  SUCCESS: Migrated logo to {cloudinary_url}')
                
            except Exception as e:
                self.stdout.write(f'  ERROR: Failed to migrate logo: {str(e)}')

    def get_image_content(self, image_field):
        """Get image content from various sources"""
        try:
            # Try to read from the file field directly
            if hasattr(image_field, 'read'):
                image_field.seek(0)
                return image_field.read()
            
            # Try to open the file if it exists locally
            if hasattr(image_field, 'path'):
                try:
                    with open(image_field.path, 'rb') as f:
                        return f.read()
                except (FileNotFoundError, OSError):
                    pass
            
            # If it's a URL, try to download it
            image_url = str(image_field)
            if image_url.startswith('http'):
                response = requests.get(image_url, timeout=30)
                if response.status_code == 200:
                    return response.content
            
            return None
            
        except Exception as e:
            self.stdout.write(f'Error getting image content: {str(e)}')
            return None
