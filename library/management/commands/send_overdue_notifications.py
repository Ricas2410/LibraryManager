from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from library.models import Loan, LibrarySettings


class Command(BaseCommand):
    help = 'Send overdue notification emails to users with overdue books'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending emails'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get library settings
        library_settings = LibrarySettings.get_settings()
        
        # Find overdue loans
        overdue_loans = Loan.objects.filter(
            status='active',
            due_date__lt=timezone.now()
        ).select_related('borrower', 'book')
        
        if not overdue_loans.exists():
            self.stdout.write(
                self.style.SUCCESS('No overdue loans found.')
            )
            return
        
        sent_count = 0
        error_count = 0
        
        for loan in overdue_loans:
            try:
                days_overdue = (timezone.now().date() - loan.due_date.date()).days
                fine_amount = loan.calculate_fine(library_settings.daily_fine_rate)
                
                subject = f'OVERDUE: "{loan.book.title}" - {days_overdue} days overdue'
                
                message = f"""
Dear {loan.borrower.get_full_name()},

This is an OVERDUE notice for the following book:

Book: {loan.book.title}
Author(s): {loan.book.get_authors_display()}
Due Date: {loan.due_date.strftime('%B %d, %Y')}
Days Overdue: {days_overdue}
Current Fine: ${fine_amount:.2f}

Please return this book immediately to avoid additional late fees. 

Daily fine rate: ${library_settings.daily_fine_rate}/day
Maximum fine: ${library_settings.max_fine_amount}

You can return the book during library hours or contact us to arrange return.

Library Contact Information:
{library_settings.library_name}
{library_settings.library_address or ''}
Phone: {library_settings.library_phone or 'N/A'}
Email: {library_settings.library_email or 'N/A'}

Thank you for your immediate attention to this matter.

Library Team
                """.strip()
                
                if dry_run:
                    recipients = [loan.borrower.email]
                    if loan.borrower.notification_email:
                        recipients.append(loan.borrower.notification_email)
                    self.stdout.write(
                        f'Would send overdue notice to {", ".join(recipients)}: {subject}'
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
                        f'Sent overdue notice to {", ".join(recipients)} for "{loan.book.title}" ({days_overdue} days overdue)'
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
                    f'Dry run complete. Would send {sent_count} overdue notifications.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully sent {sent_count} overdue notifications.'
                )
            )
            
            if error_count > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'{error_count} emails failed to send.'
                    )
                )
