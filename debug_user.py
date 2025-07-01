#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management.settings')

# Setup Django
django.setup()

from library.models import User

# Create a test user
user = User.objects.create_user(
    username='testuser',
    email='test@example.com',
    password='testpass123',
    first_name='Test',
    last_name='User',
    role='student',
    is_active_member=True
)

print(f"User created: {user}")
print(f"User role: {user.role}")
print(f"User is_active_member: {user.is_active_member}")
print(f"Can borrow books: {user.can_borrow_books()}")
print(f"Can manage books: {user.can_manage_books()}")
print(f"Can manage users: {user.can_manage_users()}")

# Clean up
user.delete()
print("User deleted")
