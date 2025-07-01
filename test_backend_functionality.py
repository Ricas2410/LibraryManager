#!/usr/bin/env python
"""
Comprehensive test script to check all backend functionality
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import authenticate

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management.settings')
django.setup()

from library.models import User, Book, Author, Category, Publisher, Loan
from library.forms import CustomUserCreationForm, BookForm, LoanForm

def test_database_connectivity():
    """Test database connectivity and data"""
    print("Testing Database Connectivity...")
    
    try:
        # Test basic queries
        user_count = User.objects.count()
        book_count = Book.objects.count()
        author_count = Author.objects.count()
        category_count = Category.objects.count()
        publisher_count = Publisher.objects.count()
        
        print(f"✅ Database connected successfully")
        print(f"  Users: {user_count}")
        print(f"  Books: {book_count}")
        print(f"  Authors: {author_count}")
        print(f"  Categories: {category_count}")
        print(f"  Publishers: {publisher_count}")
        
        # Test if admin user exists
        try:
            admin_user = User.objects.get(username='admin')
            print(f"✅ Admin user exists: {admin_user.username}")
            print(f"  Role: {admin_user.role}")
            print(f"  Is active: {admin_user.is_active}")
            print(f"  Can manage users: {admin_user.can_manage_users()}")
        except User.DoesNotExist:
            print("❌ Admin user does not exist")
            
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_user_creation():
    """Test user creation functionality"""
    print("\nTesting User Creation...")
    
    try:
        # Test form creation
        form_data = {
            'username': 'testuser123',
            'email': 'testuser123@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'role': 'student',
            'enrollment_number': 'STU123'
        }
        
        form = CustomUserCreationForm(data=form_data)
        print(f"Form is valid: {form.is_valid()}")
        
        if form.is_valid():
            user = form.save()
            print(f"✅ User created successfully: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Role: {user.role}")
            
            # Clean up
            user.delete()
            print("✅ Test user cleaned up")
        else:
            print(f"❌ Form validation errors: {form.errors}")
            
    except Exception as e:
        print(f"❌ User creation error: {e}")

def test_book_form():
    """Test book form functionality"""
    print("\nTesting Book Form...")
    
    try:
        # Get some authors and categories
        authors = Author.objects.all()[:2]
        categories = Category.objects.all()[:2]
        
        print(f"Available authors: {[str(a) for a in authors]}")
        print(f"Available categories: {[str(c) for c in categories]}")
        
        if not authors:
            print("❌ No authors found in database")
            return
            
        if not categories:
            print("❌ No categories found in database")
            return
        
        # Test form creation
        form_data = {
            'title': 'Test Book',
            'authors': [str(a.id) for a in authors],
            'categories': [str(c.id) for c in categories],
            'total_copies': 5,
            'isbn': 'TEST-123-456',  # Test flexible ISBN
            'language': 'English'
        }
        
        form = BookForm(data=form_data)
        print(f"Book form is valid: {form.is_valid()}")
        
        if form.is_valid():
            book = form.save()
            print(f"✅ Book created successfully: {book.title}")
            print(f"  ISBN: {book.isbn}")
            print(f"  Authors: {[str(a) for a in book.authors.all()]}")
            print(f"  Categories: {[str(c) for c in book.categories.all()]}")
            
            # Clean up
            book.delete()
            print("✅ Test book cleaned up")
        else:
            print(f"❌ Book form validation errors: {form.errors}")
            
    except Exception as e:
        print(f"❌ Book form error: {e}")

def test_loan_functionality():
    """Test loan creation functionality"""
    print("\nTesting Loan Functionality...")
    
    try:
        # Get available books and users
        available_books = Book.objects.filter(available_copies__gt=0)[:1]
        borrowers = User.objects.filter(role__in=['student', 'teacher'])[:1]
        
        print(f"Available books: {[str(b) for b in available_books]}")
        print(f"Available borrowers: {[str(u) for u in borrowers]}")
        
        if not available_books:
            print("❌ No available books found")
            return
            
        if not borrowers:
            print("❌ No borrowers found")
            return
        
        book = available_books[0]
        borrower = borrowers[0]
        
        # Test loan form
        from datetime import datetime, timedelta
        due_date = datetime.now() + timedelta(days=14)
        
        form_data = {
            'book': str(book.id),
            'borrower': str(borrower.id),
            'due_date': due_date.strftime('%Y-%m-%dT%H:%M'),
            'notes': 'Test loan'
        }
        
        form = LoanForm(data=form_data)
        print(f"Loan form is valid: {form.is_valid()}")
        
        if form.is_valid():
            print("✅ Loan form validation passed")
            print(f"  Book: {book.title}")
            print(f"  Borrower: {borrower.username}")
            print(f"  Due date: {due_date}")
        else:
            print(f"❌ Loan form validation errors: {form.errors}")
            
    except Exception as e:
        print(f"❌ Loan functionality error: {e}")

def test_authentication():
    """Test authentication functionality"""
    print("\nTesting Authentication...")
    
    try:
        # Test admin authentication
        admin_user = authenticate(username='admin', password='admin123')
        if admin_user:
            print(f"✅ Admin authentication successful: {admin_user.username}")
        else:
            print("❌ Admin authentication failed")
            
        # Test invalid authentication
        invalid_user = authenticate(username='invalid', password='invalid')
        if not invalid_user:
            print("✅ Invalid authentication correctly rejected")
        else:
            print("❌ Invalid authentication incorrectly accepted")
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")

def test_model_methods():
    """Test model methods"""
    print("\nTesting Model Methods...")
    
    try:
        # Test book availability
        books = Book.objects.all()[:1]
        if books:
            book = books[0]
            print(f"Book: {book.title}")
            print(f"  Is available: {book.is_available()}")
            print(f"  Available copies: {book.available_copies}")
            print(f"  Total copies: {book.total_copies}")
            print("✅ Book model methods working")
        
        # Test user permissions
        users = User.objects.all()[:1]
        if users:
            user = users[0]
            print(f"User: {user.username}")
            print(f"  Can borrow books: {user.can_borrow_books()}")
            print(f"  Can manage books: {user.can_manage_books()}")
            print(f"  Can manage users: {user.can_manage_users()}")
            print("✅ User model methods working")
            
    except Exception as e:
        print(f"❌ Model methods error: {e}")

def main():
    """Run all tests"""
    print("🔍 Testing Backend Functionality")
    print("=" * 50)
    
    # Run all tests
    db_ok = test_database_connectivity()
    if db_ok:
        test_user_creation()
        test_book_form()
        test_loan_functionality()
        test_authentication()
        test_model_methods()
    
    print("\n" + "=" * 50)
    print("✅ Backend functionality tests completed!")

if __name__ == '__main__':
    main()
