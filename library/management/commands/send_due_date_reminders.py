from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from library.models import Loan, LibrarySettings


class Command(BaseCommand):
    help = 'Send due date reminder emails to users with books due soon'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=3,
            help='Number of days before due date to send reminder (default: 3)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending emails'
        )

    def handle(self, *args, **options):
        days_ahead = options['days']
        dry_run = options['dry_run']
        
        # Get library settings
        library_settings = LibrarySettings.get_settings()
        
        # Calculate the target date (e.g., 3 days from now)
        target_date = timezone.now().date() + timedelta(days=days_ahead)
        
        # Find loans due on the target date
        loans_due = Loan.objects.filter(
            status='active',
            due_date__date=target_date
        ).select_related('borrower', 'book')
        
        if not loans_due.exists():
            self.stdout.write(
                self.style.SUCCESS(f'No loans due in {days_ahead} days.')
            )
            return
        
        sent_count = 0
        error_count = 0
        
        for loan in loans_due:
            try:
                subject = f'Library Reminder: "{loan.book.title}" due in {days_ahead} days'
                
                message = f"""
Dear {loan.borrower.get_full_name()},

This is a friendly reminder that the following book is due in {days_ahead} days:

Book: {loan.book.title}
Author(s): {loan.book.get_authors_display()}
Due Date: {loan.due_date.strftime('%B %d, %Y')}

Please return the book on time to avoid late fees. If you need to renew the book, please contact the library or log into your account.

Library Contact Information:
{library_settings.library_name}
{library_settings.library_address or ''}
Phone: {library_settings.library_phone or 'N/A'}
Email: {library_settings.library_email or 'N/A'}

Thank you for using our library!

Best regards,
Library Team
                """.strip()
                
                if dry_run:
                    recipients = [loan.borrower.email]
                    if loan.borrower.notification_email:
                        recipients.append(loan.borrower.notification_email)
                    self.stdout.write(
                        f'Would send email to {", ".join(recipients)}: {subject}'
                    )
                else:
                    # Send to both user email and additional notification email
                    recipients = [loan.borrower.email]
                    if loan.borrower.notification_email:
                        recipients.append(loan.borrower.notification_email)

                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=recipients,
                        fail_silently=False,
                    )
                    self.stdout.write(
                        f'Sent reminder to {", ".join(recipients)} for "{loan.book.title}"'
                    )
                
                sent_count += 1
                
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to send email to {loan.borrower.email}: {str(e)}'
                    )
                )
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Dry run complete. Would send {sent_count} reminder emails.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully sent {sent_count} reminder emails.'
                )
            )
            
            if error_count > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'{error_count} emails failed to send.'
                    )
                )
