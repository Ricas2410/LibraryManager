from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Book, Author, Category, Publisher, Loan, Reservation, LibrarySettings
from .forms import CustomUserCreationForm, BookForm, LoanForm

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='student',
            is_active_member=True
        )

    def test_user_creation(self):
        """Test user creation with custom fields"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.role, 'student')
        self.assertTrue(self.user.is_active_member)

    def test_user_full_name(self):
        """Test get_full_name method"""
        self.assertEqual(self.user.get_full_name(), 'Test User')

    def test_user_permissions(self):
        """Test user permission methods"""
        # Student permissions
        self.assertTrue(self.user.can_borrow_books())
        self.assertFalse(self.user.can_manage_books())
        self.assertFalse(self.user.can_manage_users())

        # Librarian permissions
        self.user.role = 'librarian'
        self.user.save()
        self.assertTrue(self.user.can_borrow_books())
        self.assertTrue(self.user.can_manage_books())
        self.assertFalse(self.user.can_manage_users())

        # Admin permissions
        self.user.role = 'admin'
        self.user.save()
        self.assertFalse(self.user.can_borrow_books())
        self.assertTrue(self.user.can_manage_books())
        self.assertTrue(self.user.can_manage_users())


class BookModelTest(TestCase):
    """Test cases for Book model"""

    def setUp(self):
        self.author = Author.objects.create(
            first_name='Test',
            last_name='Author'
        )
        self.category = Category.objects.create(
            name='Fiction',
            description='Fictional books'
        )
        self.publisher = Publisher.objects.create(
            name='Test Publisher'
        )
        self.book = Book.objects.create(
            title='Test Book',
            isbn='978-0-123456-78-9',
            publication_date='2023-01-01',
            pages=200,
            shelf_location='A1',
            section='Fiction',
            total_copies=3,
            available_copies=3,
            publisher=self.publisher
        )
        self.book.authors.add(self.author)
        self.book.categories.add(self.category)

    def test_book_creation(self):
        """Test book creation"""
        self.assertEqual(self.book.title, 'Test Book')
        self.assertEqual(self.book.isbn, '978-0-123456-78-9')
        self.assertEqual(self.book.total_copies, 3)
        self.assertEqual(self.book.available_copies, 3)

    def test_book_availability(self):
        """Test book availability methods"""
        self.assertTrue(self.book.is_available())

        # Make book unavailable
        self.book.available_copies = 0
        self.book.save()
        self.assertFalse(self.book.is_available())

    def test_book_display_methods(self):
        """Test book display methods"""
        self.assertEqual(self.book.get_authors_display(), 'Test Author')
        self.assertEqual(self.book.get_categories_display(), 'Fiction')
