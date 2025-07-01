from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (User, Book, Author, Category, Publisher, Loan, Reservation,
                     LibrarySettings, AuditLog, Section, ShelfLocation, Floor)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom User Admin"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active_member', 'date_joined')
    list_filter = ('role', 'is_active_member', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'enrollment_number')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Library Information', {
            'fields': ('role', 'phone_number', 'address', 'date_of_birth',
                      'enrollment_number', 'class_grade', 'profile_picture', 'is_active_member')
        }),
        ('Additional Notifications', {
            'fields': ('notification_email',),
            'classes': ('collapse',),
            'description': 'Optional additional email for notifications (parent, guardian, or secondary contact)'
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Library Information', {
            'fields': ('role', 'email', 'first_name', 'last_name', 'phone_number',
                      'address', 'date_of_birth', 'enrollment_number', 'class_grade', 'is_active_member')
        }),
        ('Additional Notifications', {
            'fields': ('notification_email',),
            'classes': ('collapse',),
            'description': 'Optional additional email for notifications (parent, guardian, or secondary contact)'
        }),
    )


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'nationality', 'birth_date')
    search_fields = ('first_name', 'last_name', 'nationality')
    list_filter = ('nationality',)
    ordering = ('last_name', 'first_name')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'website', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('created_at',)
    ordering = ('name',)
    fields = ('name', 'address', 'phone', 'email', 'website')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'floor', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('floor', 'created_at')
    fields = ('name', 'description', 'floor')


@admin.register(ShelfLocation)
class ShelfLocationAdmin(admin.ModelAdmin):
    list_display = ('code', 'section', 'capacity', 'created_at')
    search_fields = ('code', 'description')
    list_filter = ('section', 'created_at')
    fields = ('code', 'section', 'description', 'capacity')


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    fields = ('name', 'description')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'isbn', 'get_authors_display', 'publisher', 'status', 'available_copies', 'total_copies')
    list_filter = ('status', 'categories', 'publisher', 'language', 'section')
    search_fields = ('title', 'isbn', 'authors__first_name', 'authors__last_name')
    filter_horizontal = ('authors', 'categories')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    ordering = ('title',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subtitle', 'authors', 'isbn', 'publisher')
        }),
        ('Publication Details', {
            'fields': ('publication_date', 'edition', 'pages', 'language', 'categories')
        }),
        ('Physical Details', {
            'fields': ('cover_image', 'physical_description')
        }),
        ('Location', {
            'fields': ('shelf_location', 'section', 'floor')
        }),
        ('Availability', {
            'fields': ('status', 'total_copies', 'available_copies')
        }),
        ('Additional Information', {
            'fields': ('summary', 'notes', 'acquisition_date', 'price')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new book
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('book', 'borrower', 'issue_date', 'due_date', 'return_date', 'status', 'fine_amount')
    list_filter = ('status', 'issue_date', 'due_date', 'fine_paid')
    search_fields = ('book__title', 'borrower__username', 'borrower__first_name', 'borrower__last_name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-issue_date',)

    fieldsets = (
        ('Loan Information', {
            'fields': ('book', 'borrower', 'issued_by')
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date', 'return_date')
        }),
        ('Status & Details', {
            'fields': ('status', 'renewal_count', 'notes')
        }),
        ('Fines', {
            'fields': ('fine_amount', 'fine_paid')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'reservation_date', 'expiry_date', 'status', 'priority')
    list_filter = ('status', 'reservation_date')
    search_fields = ('book__title', 'user__username', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('priority', 'reservation_date')


@admin.register(LibrarySettings)
class LibrarySettingsAdmin(admin.ModelAdmin):
    list_display = ('library_name', 'default_loan_period', 'daily_fine_rate', 'is_active')

    def has_add_permission(self, request):
        # Only allow one settings instance
        return not LibrarySettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of settings
        return False


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'target_user', 'book', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'target_user__username', 'book__title', 'description')
    readonly_fields = ('action', 'user', 'target_user', 'book', 'description', 'ip_address', 'timestamp')
    ordering = ('-timestamp',)

    def has_add_permission(self, request):
        # Audit logs should only be created programmatically
        return False

    def has_change_permission(self, request, obj=None):
        # Audit logs should not be editable
        return False

    def has_delete_permission(self, request, obj=None):
        # Allow deletion for cleanup purposes
        return request.user.is_superuser
