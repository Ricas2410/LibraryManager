"""
Context processors for library management system
"""
from django.db.models import Q
from .models import Loan, Reservation, Notification


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
        
        context.update({
            'unread_notifications_count': unread_notifications_count,
        })
    
    return context
