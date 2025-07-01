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

from library.models import User, Category, Author, Publisher

# Update admin user role
try:
    admin_user = User.objects.get(username='admin')
    admin_user.role = 'admin'
    admin_user.first_name = 'Admin'
    admin_user.last_name = 'User'
    admin_user.save()
    print("✓ Admin user updated successfully")
except User.DoesNotExist:
    print("✗ Admin user not found")

# Create some basic categories
categories = [
    {'name': 'Fiction', 'description': 'Fictional literature and novels'},
    {'name': 'Science', 'description': 'Scientific books and textbooks'},
    {'name': 'History', 'description': 'Historical books and biographies'},
    {'name': 'Mathematics', 'description': 'Mathematics textbooks and references'},
    {'name': 'Literature', 'description': 'Classic and modern literature'},
]

for cat_data in categories:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    if created:
        print(f"✓ Category '{category.name}' created")

# Create some basic authors
authors = [
    {'first_name': 'William', 'last_name': 'Shakespeare'},
    {'first_name': 'Jane', 'last_name': 'Austen'},
    {'first_name': 'George', 'last_name': 'Orwell'},
    {'first_name': 'Harper', 'last_name': 'Lee'},
]

for author_data in authors:
    author, created = Author.objects.get_or_create(
        first_name=author_data['first_name'],
        last_name=author_data['last_name']
    )
    if created:
        print(f"✓ Author '{author.get_full_name()}' created")

# Create some basic publishers
publishers = [
    {'name': 'Penguin Random House'},
    {'name': 'HarperCollins'},
    {'name': 'Scholastic'},
]

for pub_data in publishers:
    publisher, created = Publisher.objects.get_or_create(
        name=pub_data['name']
    )
    if created:
        print(f"✓ Publisher '{publisher.name}' created")

print("Setup completed successfully!")
