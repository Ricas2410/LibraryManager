from django.urls import path
from . import views

urlpatterns = [
    # Health check endpoint
    path('health/', views.health_check, name='health_check'),

    # Authentication
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register_user, name='register'),
    path('profile/', views.profile, name='profile'),

    # Home
    path('', views.home, name='home'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('request-book/<uuid:book_id>/', views.request_book, name='request_book'),
    path('pending-requests/', views.pending_requests, name='pending_requests'),
    path('approve-request/<uuid:loan_id>/', views.approve_request, name='approve_request'),
    path('reject-request/<uuid:loan_id>/', views.reject_request, name='reject_request'),
    path('cancel-request/<uuid:loan_id>/', views.cancel_request, name='cancel_request'),
    path('my-loans/', views.my_loans, name='my_loans'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    path('my-pending-requests/', views.my_pending_requests, name='my_pending_requests'),
    path('notifications/', views.notifications_list, name='notifications_list'),

    # API endpoints
    path('api/notifications/', views.api_notifications, name='api_notifications'),
    path('api/notifications/<uuid:notification_id>/read/', views.api_mark_notification_read, name='api_mark_notification_read'),
    path('api/notifications/mark-all-read/', views.api_mark_all_notifications_read, name='api_mark_all_notifications_read'),
    path('api/live-search/', views.live_search_api, name='live_search_api'),

    # Books
    path('books/', views.book_list, name='book_list'),
    path('books/<uuid:book_id>/', views.book_detail, name='book_detail'),
    path('books/add/', views.book_add, name='book_add'),
    path('books/<uuid:book_id>/edit/', views.book_edit, name='book_edit'),
    path('books/<uuid:book_id>/delete/', views.book_delete, name='book_delete'),

    # Users (Admin only)
    path('users/', views.user_list, name='user_list'),
    path('users/<uuid:user_id>/', views.user_detail, name='user_detail'),
    path('users/<uuid:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<uuid:user_id>/toggle-status/', views.user_toggle_status, name='user_toggle_status'),

    # Loans
    path('loans/', views.loan_list, name='loan_list'),
    path('loans/create/', views.loan_create, name='loan_create'),
    path('loans/<uuid:loan_id>/return/', views.loan_return, name='loan_return'),
    path('loans/<uuid:loan_id>/renew/', views.loan_renew, name='loan_renew'),
    path('loans/overdue/', views.overdue_loans, name='overdue_loans'),
    path('loans/due-soon/', views.due_soon_loans, name='due_soon_loans'),

    # Reservations
    path('reservations/', views.reservation_list, name='reservation_list'),
    path('books/<uuid:book_id>/reserve/', views.reservation_create, name='reservation_create'),
    path('reservations/<uuid:reservation_id>/cancel/', views.reservation_cancel, name='reservation_cancel'),

    # Reports
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path('reports/loans/export/', views.export_loans_report, name='export_loans_report'),
    path('reports/books/export/', views.export_books_report, name='export_books_report'),

    # Search
    path('search/', views.advanced_search, name='advanced_search'),

    # User Management
    path('user-management/', views.user_management, name='user_management'),
    path('csv-template/', views.download_csv_template, name='download_csv_template'),
    path('import-csv/', views.import_users_csv, name='import_users_csv'),
    path('sync-api/', views.sync_school_api, name='sync_school_api'),

    # Book Import
    path('books/import/', views.book_import_page, name='book_import_page'),
    path('books/csv-template/', views.download_books_csv_template, name='download_books_csv_template'),
    path('books/import-csv/', views.import_books_csv, name='import_books_csv'),

    # Reading History
    path('reading-history/', views.reading_history, name='reading_history'),
    path('admin/reading-history/', views.admin_reading_history, name='admin_reading_history'),
    path('admin/reading-history/student/<uuid:user_id>/', views.student_reading_detail, name='student_reading_detail'),
    path('admin/reading-history/reset/', views.reset_reading_history, name='reset_reading_history'),

    # Settings
    path('settings/', views.library_settings, name='library_settings'),
    path('settings/backup/', views.backup_system, name='backup_system'),
    path('settings/restore/', views.restore_system, name='restore_system'),

    # Management pages
    path('authors/', views.author_list, name='author_list'),
    path('authors/add/', views.author_add, name='author_add'),
    path('authors/<int:author_id>/edit/', views.author_edit, name='author_edit'),
    path('authors/<int:author_id>/delete/', views.author_delete, name='author_delete'),

    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:category_id>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='category_delete'),

    path('publishers/', views.publisher_list, name='publisher_list'),
    path('publishers/add/', views.publisher_add, name='publisher_add'),
    path('publishers/<int:publisher_id>/edit/', views.publisher_edit, name='publisher_edit'),
    path('publishers/<int:publisher_id>/delete/', views.publisher_delete, name='publisher_delete'),

    path('sections/', views.section_list, name='section_list'),
    path('sections/add/', views.section_add, name='section_add'),
    path('sections/<int:section_id>/edit/', views.section_edit, name='section_edit'),
    path('sections/<int:section_id>/delete/', views.section_delete, name='section_delete'),

    path('shelf-locations/', views.shelf_location_list, name='shelf_location_list'),
    path('shelf-locations/add/', views.shelf_location_add, name='shelf_location_add'),
    path('shelf-locations/<int:shelf_id>/edit/', views.shelf_location_edit, name='shelf_location_edit'),
    path('shelf-locations/<int:shelf_id>/delete/', views.shelf_location_delete, name='shelf_location_delete'),

    path('floors/', views.floor_list, name='floor_list'),
    path('floors/add/', views.floor_add, name='floor_add'),
    path('floors/<int:floor_id>/edit/', views.floor_edit, name='floor_edit'),
    path('floors/<int:floor_id>/delete/', views.floor_delete, name='floor_delete'),

    # API endpoints for autocomplete
    path('api/publishers/', views.publisher_autocomplete, name='publisher_autocomplete'),
    path('api/categories/', views.category_autocomplete, name='category_autocomplete'),
    path('api/sections/', views.section_autocomplete, name='section_autocomplete'),
    path('api/shelf-locations/', views.shelf_location_autocomplete, name='shelf_location_autocomplete'),
    path('api/floors/', views.floor_autocomplete, name='floor_autocomplete'),
    path('api/books/', views.book_autocomplete, name='book_autocomplete'),
    path('api/users/', views.user_autocomplete, name='user_autocomplete'),

    # Admin utilities
    path('admin/migrate-images/', views.migrate_images_to_cloudinary, name='migrate_images_to_cloudinary'),

    # PIN Change and Password Reset
    path('change-pin/', views.change_pin, name='change_pin'),
    path('password-reset-request/', views.password_reset_request, name='password_reset_request'),
]
