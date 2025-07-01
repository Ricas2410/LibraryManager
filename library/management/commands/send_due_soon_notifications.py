"""
Management command to send notifications for books due soon
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from library.models import Loan, Notification


class Command(BaseCommand):
    help = 'Send notifications for books due soon (within next 3 days)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending emails',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=3,
            help='Number of days ahead to check for due books (default: 3)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days_ahead = options['days']
        
        # Get loans due within specified days
        today = timezone.now().date()
        due_soon_date = today + timedelta(days=days_ahead)
        
        due_soon_loans = Loan.objects.filter(
            status='active',
            due_date__date__gte=today,
            due_date__date__lte=due_soon_date
        ).select_related('book', 'borrower')

        if not due_soon_loans.exists():
            self.stdout.write(
                self.style.SUCCESS(f'No books due within the next {days_ahead} days.')
            )
            return

        self.stdout.write(
            self.style.WARNING(f'Found {due_soon_loans.count()} books due within the next {days_ahead} days.')
        )

        sent_count = 0
        error_count = 0

        for loan in due_soon_loans:
            days_until_due = (loan.due_date.date() - today).days
            
            # Check if we've already sent a notification for this loan recently
            recent_notification = Notification.objects.filter(
                user=loan.borrower,
                loan=loan,
                notification_type='due_soon',
                created_at__date=today
            ).exists()
            
            if recent_notification:
                self.stdout.write(f'Skipping {loan.borrower.email} - notification already sent today')
                continue

            subject = f"Book Due Soon - {loan.book.title}"
            
            if days_until_due == 0:
                urgency = "today"
                urgency_class = "urgent"
            elif days_until_due == 1:
                urgency = "tomorrow"
                urgency_class = "important"
            else:
                urgency = f"in {days_until_due} days"
                urgency_class = "reminder"

            message = f"""Dear {loan.borrower.get_full_name()},

This is a friendly reminder that your borrowed book is due {urgency}.

Book Details:
- Title: {loan.book.title}
- Author(s): {', '.join([author.name for author in loan.book.authors.all()])}
- Due Date: {loan.due_date.strftime('%B %d, %Y')}
- Days Until Due: {days_until_due}

Please return the book on time to avoid late fees. If you need to extend your loan period, please contact the library or use the online renewal system.

You can return the book to:
- Library circulation desk during operating hours
- Book drop box (available 24/7)

Thank you for using our library services!

Best regards,
Library Team

---
This is an automated message. Please do not reply to this email.
"""

            try:
                # Create in-app notification
                Notification.objects.create(
                    user=loan.borrower,
                    title=subject,
                    message=f"Your book '{loan.book.title}' is due {urgency}. Please return it on time to avoid late fees.",
                    notification_type='due_soon',
                    book=loan.book,
                    loan=loan
                )

                if dry_run:
                    recipients = [loan.borrower.email]
                    if loan.borrower.notification_email:
                        recipients.append(loan.borrower.notification_email)
                    self.stdout.write(
                        f'Would send due soon notice to {", ".join(recipients)}: {subject}'
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
                        f'Sent due soon notice to {", ".join(recipients)} for "{loan.book.title}" (due {urgency})'
                    )
                
                sent_count += 1

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'Failed to send notification to {loan.borrower.email}: {str(e)}')
                )

        # Summary
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'Dry run completed. Would have sent {sent_count} notifications.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully sent {sent_count} due soon notifications.')
            )
            
        if error_count > 0:
            self.stdout.write(
                self.style.ERROR(f'{error_count} notifications failed to send.')
            )
