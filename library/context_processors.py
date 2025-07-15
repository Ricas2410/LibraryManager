"""
Context processors for library management system
"""
from django.db.models import Q
from .models import Loan, Reservation, Notification, LibrarySettings


def admin_notifications(request):
    """
    Add admin notification counts to template context
    """
    context = {}
    
    # Only add counts for authenticated users who are librarians or admins
    if request.user.is_authenticated and (request.user.role in ['librarian', 'admin'] or request.user.is_superuser):
        
        # Count pending loan requests
        pending_requests_count = Loan.objects.filter(status='pending').count()
        
        # Count active reservations (students waiting for books)
        active_reservations_count = Reservation.objects.filter(status='active').count()
        
        # Count overdue books
        from django.utils import timezone
        from datetime import timedelta

        overdue_loans_count = Loan.objects.filter(
            status='active',
            due_date__lt=timezone.now()
        ).count()

        # Count books due soon (next 3 days)
        today = timezone.now().date()
        due_soon_date = today + timedelta(days=3)
        due_soon_loans_count = Loan.objects.filter(
            status='active',
            due_date__date__gte=today,
            due_date__date__lte=due_soon_date
        ).count()

        # Total admin notifications count
        total_admin_notifications = pending_requests_count + active_reservations_count + overdue_loans_count + due_soon_loans_count
        
        context.update({
            'pending_requests_count': pending_requests_count,
            'active_reservations_count': active_reservations_count,
            'overdue_loans_count': overdue_loans_count,
            'due_soon_loans_count': due_soon_loans_count,
            'total_admin_notifications': total_admin_notifications,
        })
    
    return context


def user_notifications(request):
    """
    Add user notification counts to template context
    """
    context = {}

    if request.user.is_authenticated:
        # Count unread notifications for the current user
        unread_notifications_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        # Get admin notifications count if user is admin/librarian
        admin_notifications_count = 0
        if request.user.role in ['librarian', 'admin'] or request.user.is_superuser:
            from django.utils import timezone
            from datetime import timedelta

            # Count pending loan requests
            pending_requests_count = Loan.objects.filter(status='pending').count()

            # Count active reservations
            active_reservations_count = Reservation.objects.filter(status='active').count()

            # Count overdue books
            overdue_loans_count = Loan.objects.filter(
                status='active',
                due_date__lt=timezone.now()
            ).count()

            # Count books due soon (next 3 days)
            today = timezone.now().date()
            due_soon_date = today + timedelta(days=3)
            due_soon_loans_count = Loan.objects.filter(
                status='active',
                due_date__date__gte=today,
                due_date__date__lte=due_soon_date
            ).count()

            admin_notifications_count = pending_requests_count + active_reservations_count + overdue_loans_count + due_soon_loans_count

        # Calculate total notifications
        total_notifications = unread_notifications_count + admin_notifications_count

        context.update({
            'unread_notifications_count': unread_notifications_count,
            'total_notifications': total_notifications,
        })

    return context


def library_settings(request):
    """
    Context processor to make library settings available in all templates
    """
    try:
        settings = LibrarySettings.get_settings()
        return {
            'library_settings': settings
        }
    except Exception:
        # Return default values if settings don't exist
        return {
            'library_settings': {
                'library_name': 'Library Management System',
                'library_address': '',
                'library_phone': '',
                'library_email': '',
                'library_logo': None,
                'login_banner': None,
            }
        }


def admin_stats(request):
    """
    Context processor to provide admin dashboard statistics
    """
    # Only provide stats for admin pages
    if not request.path.startswith('/admin/'):
        return {}

    try:
        from .models import Book, User, Loan

        stats = {
            'total_books': Book.objects.count(),
            'total_users': User.objects.filter(is_active=True).count(),
            'active_loans': Loan.objects.filter(status='active').count(),
            'pending_requests': Loan.objects.filter(status='pending').count(),
        }
        return stats
    except Exception:
        return {
            'total_books': 0,
            'total_users': 0,
            'active_loans': 0,
            'pending_requests': 0,
        }
