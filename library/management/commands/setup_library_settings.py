from django.core.management.base import BaseCommand
from library.models import LibrarySettings


class Command(BaseCommand):
    help = 'Set up default library settings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            help='Library name',
            default='Dei Gratia Memorial School Library'
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Library email',
            default='library@deigratiams.edu.gh'
        )
        parser.add_argument(
            '--phone',
            type=str,
            help='Library phone',
            default='+233 XX XXX XXXX'
        )
        parser.add_argument(
            '--address',
            type=str,
            help='Library address',
            default='Dei Gratia Memorial School, Ghana'
        )
        parser.add_argument(
            '--setup-defaults',
            action='store_true',
            help='Set up with default Deigratia Montessori School information'
        )

    def handle(self, *args, **options):
        # Use Deigratia Montessori School defaults if requested
        if options['setup_defaults']:
            name = 'Deigratia Montessori School Library'
            email = 'library@deigratiams.edu.gh'
            phone = '+233 XX XXX XXXX'
            address = 'Deigratia Montessori School, Ghana'
        else:
            name = options['name']
            email = options['email']
            phone = options['phone']
            address = options['address']

        settings, created = LibrarySettings.objects.get_or_create(
            pk=1,
            defaults={
                'library_name': name,
                'library_email': email,
                'library_phone': phone,
                'library_address': address,
                'default_loan_period': 14,
                'max_renewals': 3,
                'max_books_per_user': 5,
                'daily_fine_rate': 1.00,
                'max_fine_amount': 50.00,
                'reservation_expiry_days': 7,
                'max_reservations_per_user': 3,
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Library settings created: {settings.library_name}')
            )
        else:
            # Update existing settings
            settings.library_name = name
            settings.library_email = email
            settings.library_phone = phone
            settings.library_address = address
            settings.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Library settings updated: {settings.library_name}')
            )

        self.stdout.write(
            self.style.SUCCESS('Library settings are ready!')
        )
