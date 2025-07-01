from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from library.models import Loan, Notification
from library.views import create_notification


class Command(BaseCommand):
    help = 'Send notifications for books due soon and overdue books'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Books due in 2 days
        due_soon_date = now + timedelta(days=2)
        due_soon_loans = Loan.objects.filter(
            status='active',
            due_date__date=due_soon_date.date()
        ).select_related('borrower', 'book')
        
        # Overdue books
        overdue_loans = Loan.objects.filter(
            status='active',
            due_date__lt=now
        ).select_related('borrower', 'book')
        
        # Send due soon notifications
        for loan in due_soon_loans:
            # Check if notification already sent today
            existing_notification = Notification.objects.filter(
                user=loan.borrower,
                loan=loan,
                notification_type='book_due',
                created_at__date=now.date()
            ).exists()
            
            if not existing_notification:
                create_notification(
                    user=loan.borrower,
                    title="Book Due Soon",
                    message=f"Your book '{loan.book.title}' is due on {loan.due_date.strftime('%B %d, %Y')}. Please return it on time to avoid fines.",
                    notification_type='book_due',
                    book=loan.book,
                    loan=loan
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Due soon notification sent to {loan.borrower.username} for "{loan.book.title}"')
                )
        
        # Send overdue notifications
        for loan in overdue_loans:
            # Update loan status to overdue
            if loan.status != 'overdue':
                loan.status = 'overdue'
                loan.save()
            
            # Check if notification already sent today
            existing_notification = Notification.objects.filter(
                user=loan.borrower,
                loan=loan,
                notification_type='book_overdue',
                created_at__date=now.date()
            ).exists()
            
            if not existing_notification:
                days_overdue = (now.date() - loan.due_date.date()).days
                create_notification(
                    user=loan.borrower,
                    title="Book Overdue",
                    message=f"Your book '{loan.book.title}' is {days_overdue} day{'s' if days_overdue > 1 else ''} overdue. Please return it immediately to avoid additional fines.",
                    notification_type='book_overdue',
                    book=loan.book,
                    loan=loan
                )
                self.stdout.write(
                    self.style.WARNING(f'Overdue notification sent to {loan.borrower.username} for "{loan.book.title}"')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Notification check completed. Due soon: {due_soon_loans.count()}, Overdue: {overdue_loans.count()}')
        )
