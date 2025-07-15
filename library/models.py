from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
from cloudinary_storage.storage import MediaCloudinaryStorage
import uuid


class User(AbstractUser):
    """Custom User model with role-based access"""
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('librarian', 'Librarian'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def save(self, *args, **kwargs):
        # Set role to admin for superusers
        if self.is_superuser and self.role == 'student':
            self.role = 'admin'
        super().save(*args, **kwargs)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')],
        blank=True, null=True
    )
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    enrollment_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    class_grade = models.CharField(max_length=10, blank=True, null=True)

    # Additional notification email (optional - could be parent, guardian, or secondary contact)
    notification_email = models.EmailField(
        blank=True,
        null=True,
        help_text="Optional additional email for notifications (parent, guardian, or secondary contact)"
    )

    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_active_member = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def can_borrow_books(self):
        """Check if user can borrow books"""
        return self.is_active_member and self.role in ['student', 'teacher']

    def can_manage_books(self):
        """Check if user can manage books"""
        return self.role in ['admin', 'librarian']

    def can_manage_users(self):
        """Check if user can manage other users"""
        return self.role == 'admin'


class Category(models.Model):
    """Book categories/genres"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Author(models.Model):
    """Book authors"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    biography = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    death_date = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Publisher(models.Model):
    """Book publishers"""
    name = models.CharField(max_length=200, unique=True)
    address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Section(models.Model):
    """Library sections for organizing books"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    floor = models.CharField(max_length=20, default="Ground Floor")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ShelfLocation(models.Model):
    """Specific shelf locations within sections"""
    code = models.CharField(max_length=20, unique=True, help_text="e.g., A1, B2, C3")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='shelf_locations')
    description = models.CharField(max_length=200, blank=True, null=True)
    capacity = models.PositiveIntegerField(default=50, help_text="Maximum number of books")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} ({self.section.name})"


class Floor(models.Model):
    """Library floors"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    """Book model with comprehensive details"""
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('reserved', 'Reserved'),
        ('missing', 'Missing'),
        ('damaged', 'Damaged'),
        ('maintenance', 'Under Maintenance'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    authors = models.ManyToManyField(Author, related_name='books')
    isbn = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="ISBN (any format) - Optional"
    )
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    publication_date = models.DateField(blank=True, null=True)
    edition = models.CharField(max_length=50, blank=True, null=True)
    pages = models.PositiveIntegerField(validators=[MinValueValidator(1)], blank=True, null=True)
    language = models.CharField(max_length=50, default='English')
    categories = models.ManyToManyField(Category, related_name='books')

    # Physical details
    cover_image = models.ImageField(
        upload_to='book_covers/',
        blank=True,
        null=True,
        storage=MediaCloudinaryStorage()
    )
    physical_description = models.TextField(blank=True, null=True)

    # Location details
    shelf_location = models.ForeignKey(ShelfLocation, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    floor = models.ForeignKey(Floor, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')

    # Status and availability
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    total_copies = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    available_copies = models.PositiveIntegerField(default=1, validators=[MinValueValidator(0)])

    # Additional details
    summary = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True, help_text="Internal notes for librarians")
    acquisition_date = models.DateField(default=timezone.now)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='books_created')

    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['isbn']),
            models.Index(fields=['status']),
            models.Index(fields=['shelf_location']),
        ]

    def __str__(self):
        return f"{self.title} - {self.isbn}"

    def is_available(self):
        """Check if book is available for borrowing"""
        return self.status == 'available' and self.available_copies > 0

    def get_authors_display(self):
        """Get comma-separated list of authors"""
        return ", ".join([str(author) for author in self.authors.all()])

    def get_categories_display(self):
        """Get comma-separated list of categories"""
        return ", ".join([str(category) for category in self.categories.all()])

    def update_availability(self):
        """Update book status based on available copies"""
        if self.available_copies == 0:
            if self.status == 'available':
                self.status = 'borrowed'
        elif self.available_copies > 0 and self.status == 'borrowed':
            self.status = 'available'
        self.save()


class Loan(models.Model):
    """Book loan/borrowing records"""
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='loans_issued')

    # Dates
    issue_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(blank=True, null=True)

    # Status and details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    renewal_count = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(3)])
    notes = models.TextField(blank=True, null=True)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fine_paid = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['borrower']),
            models.Index(fields=['book']),
        ]

    def __str__(self):
        return f"{self.book.title} - {self.borrower.get_full_name()}"

    def save(self, *args, **kwargs):
        # Set due date if not provided (default 14 days)
        if not self.due_date:
            self.due_date = self.issue_date + timedelta(days=14)

        # Update status based on dates
        if self.return_date:
            self.status = 'returned'
        elif self.due_date < timezone.now() and self.status == 'active':
            self.status = 'overdue'

        super().save(*args, **kwargs)

    def is_overdue(self):
        """Check if loan is overdue"""
        return self.status == 'active' and self.due_date < timezone.now()

    def days_overdue(self):
        """Calculate days overdue"""
        if self.is_overdue():
            return (timezone.now() - self.due_date).days
        return 0

    def calculate_fine(self, daily_fine=1.00):
        """Calculate fine for overdue books"""
        if self.is_overdue():
            return self.days_overdue() * daily_fine
        return 0.00

    def can_renew(self):
        """Check if loan can be renewed"""
        return (self.status == 'active' and
                self.renewal_count < 3 and
                not self.is_overdue())

    def renew(self, days=14):
        """Renew the loan"""
        if self.can_renew():
            self.due_date = self.due_date + timedelta(days=days)
            self.renewal_count += 1
            self.save()
            return True
        return False


class Reservation(models.Model):
    """Book reservation system"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')

    # Dates
    reservation_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField()
    fulfilled_date = models.DateTimeField(blank=True, null=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    priority = models.PositiveIntegerField(default=1)  # Queue position
    notes = models.TextField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['priority', 'reservation_date']
        unique_together = ['book', 'user', 'status']  # One active reservation per user per book
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['book', 'status']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.book.title} - {self.user.get_full_name()}"

    def save(self, *args, **kwargs):
        # Set expiry date if not provided (default 7 days)
        if not self.expiry_date:
            self.expiry_date = self.reservation_date + timedelta(days=7)

        # Update status based on dates
        if self.expiry_date < timezone.now() and self.status == 'active':
            self.status = 'expired'

        super().save(*args, **kwargs)

    def is_expired(self):
        """Check if reservation is expired"""
        return self.expiry_date < timezone.now() and self.status == 'active'

    def fulfill(self):
        """Mark reservation as fulfilled"""
        self.status = 'fulfilled'
        self.fulfilled_date = timezone.now()
        self.save()


class LibrarySettings(models.Model):
    """Library configuration and policies"""
    # Loan policies
    default_loan_period = models.PositiveIntegerField(default=14, help_text="Days")
    max_renewals = models.PositiveIntegerField(default=3)
    max_books_per_user = models.PositiveIntegerField(default=5)

    # Fine policies
    daily_fine_rate = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    max_fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)

    # Reservation policies
    reservation_expiry_days = models.PositiveIntegerField(default=7)
    max_reservations_per_user = models.PositiveIntegerField(default=3)

    # Library information
    library_name = models.CharField(max_length=200, default="School Library")
    library_address = models.TextField(blank=True, null=True)
    library_phone = models.CharField(max_length=15, blank=True, null=True)
    library_email = models.EmailField(blank=True, null=True)
    library_logo = models.ImageField(
        upload_to='library_logos/',
        blank=True,
        null=True,
        help_text="Upload library logo",
        storage=MediaCloudinaryStorage()
    )
    login_banner = models.ImageField(
        upload_to='login_banners/',
        blank=True,
        null=True,
        help_text="Upload login page banner image",
        storage=MediaCloudinaryStorage()
    )

    # Operational settings
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Library Settings"
        verbose_name_plural = "Library Settings"

    def __str__(self):
        return f"Library Settings - {self.library_name}"

    @classmethod
    def get_settings(cls):
        """Get or create library settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class ReadingHistory(models.Model):
    """Track books read by users for achievement and reward system"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_history')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reading_records')
    loan = models.OneToOneField(Loan, on_delete=models.CASCADE, related_name='reading_record')

    # Reading details
    date_borrowed = models.DateTimeField()
    date_returned = models.DateTimeField()
    pages_read = models.PositiveIntegerField(default=0)  # From book.pages
    reading_duration_days = models.PositiveIntegerField(default=0)  # Days between borrow and return

    # Achievement tracking
    term_period = models.CharField(max_length=50, default='current')  # e.g., 'Term 1 2024', 'current'
    academic_year = models.CharField(max_length=20, default='2024')

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_returned']
        indexes = [
            models.Index(fields=['user', 'term_period']),
            models.Index(fields=['term_period']),
            models.Index(fields=['date_returned']),
        ]
        unique_together = ['user', 'book', 'loan']  # Prevent duplicates

    def __str__(self):
        return f"{self.user.get_full_name()} read '{self.book.title}'"

    @classmethod
    def get_user_stats(cls, user, term_period='current'):
        """Get reading statistics for a user"""
        records = cls.objects.filter(user=user, term_period=term_period)
        return {
            'total_books': records.count(),
            'total_pages': records.aggregate(total=models.Sum('pages_read'))['total'] or 0,
            'avg_reading_time': records.aggregate(avg=models.Avg('reading_duration_days'))['avg'] or 0,
            'recent_books': records[:5]
        }

    @classmethod
    def get_leaderboard(cls, term_period='current', limit=50):
        """Get reading leaderboard sorted by books read, then pages"""
        from django.db.models import Count, Sum

        leaderboard = cls.objects.filter(term_period=term_period).values(
            'user__id',
            'user__first_name',
            'user__last_name',
            'user__enrollment_number',
            'user__class_grade'
        ).annotate(
            total_books=Count('id'),
            total_pages=Sum('pages_read')
        ).order_by('-total_books', '-total_pages')[:limit]

        return leaderboard

    @classmethod
    def reset_term_data(cls, new_term_period):
        """Reset reading history for new term"""
        # Archive current term data
        current_records = cls.objects.filter(term_period='current')
        current_records.update(term_period=f"archived_{timezone.now().strftime('%Y%m%d')}")

        # The new term starts fresh with term_period='current'
        return True


class AuditLog(models.Model):
    """Audit trail for important actions"""
    ACTION_CHOICES = [
        ('book_added', 'Book Added'),
        ('book_updated', 'Book Updated'),
        ('book_deleted', 'Book Deleted'),
        ('loan_issued', 'Loan Issued'),
        ('loan_returned', 'Loan Returned'),
        ('loan_renewed', 'Loan Renewed'),
        ('reservation_made', 'Reservation Made'),
        ('reservation_cancelled', 'Reservation Cancelled'),
        ('user_created', 'User Created'),
        ('user_updated', 'User Updated'),
        ('settings_updated', 'Settings Updated'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs_target')
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action']),
            models.Index(fields=['user']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.action} by {self.user} at {self.timestamp}"


class Notification(models.Model):
    """User notifications system"""
    NOTIFICATION_TYPES = [
        ('book_due', 'Book Due Soon'),
        ('book_overdue', 'Book Overdue'),
        ('book_returned', 'Book Returned'),
        ('book_available', 'Reserved Book Available'),
        ('request_approved', 'Request Approved'),
        ('request_rejected', 'Request Rejected'),
        ('fine_added', 'Fine Added'),
        ('general', 'General Notification'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='general')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Optional related objects
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"
