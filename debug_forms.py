#!/usr/bin/env python
"""
Debug script to test form submissions
"""

import os
import sys
import django
import requests
from django.test import Client

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management.settings')
django.setup()

from library.models import User, Book, Author, Category, Publisher
from django.contrib.auth import authenticate

def test_form_submissions():
    """Test form submissions with a logged-in user"""
    print("Testing Form Submissions...")
    
    # Create a test client
    client = Client()
    
    # Try to login as admin
    login_response = client.post('/login/', {
        'username': 'admin',
        'password': 'admin123'
    })
    
    print(f"Login response status: {login_response.status_code}")
    
    if login_response.status_code == 302:  # Redirect after successful login
        print("✅ Login successful")
        
        # Test loan creation form
        print("\nTesting loan creation form...")
        loan_form_response = client.get('/loans/create/')
        print(f"Loan form GET status: {loan_form_response.status_code}")
        
        if loan_form_response.status_code == 200:
            print("✅ Loan form loads successfully")
            
            # Check if there are books and users to test with
            books = Book.objects.all()[:1]
            users = User.objects.filter(role__in=['student', 'teacher'])[:1]
            
            if books and users:
                book = books[0]
                user = users[0]
                
                print(f"Testing with book: {book.title} and user: {user.username}")
                
                # Test POST to loan creation
                loan_post_data = {
                    'book': str(book.id),
                    'borrower': str(user.id),
                    'due_date': '2025-07-01T12:00',
                    'notes': 'Test loan'
                }
                
                loan_post_response = client.post('/loans/create/', loan_post_data)
                print(f"Loan creation POST status: {loan_post_response.status_code}")
                
                if loan_post_response.status_code == 302:
                    print("✅ Loan creation successful")
                else:
                    print(f"❌ Loan creation failed: {loan_post_response.status_code}")
                    if hasattr(loan_post_response, 'content'):
                        print(f"Response content: {loan_post_response.content[:500]}")
            else:
                print("❌ No books or users available for testing")
        else:
            print(f"❌ Loan form failed to load: {loan_form_response.status_code}")
        
        # Test book request form
        print("\nTesting book request form...")
        books = Book.objects.filter(available_copies__gt=0)[:1]
        
        if books:
            book = books[0]
            book_request_url = f'/request-book/{book.id}/'
            
            book_request_response = client.get(book_request_url)
            print(f"Book request form GET status: {book_request_response.status_code}")
            
            if book_request_response.status_code == 200:
                print("✅ Book request form loads successfully")
                
                # Test POST to book request
                book_request_post = client.post(book_request_url, {})
                print(f"Book request POST status: {book_request_post.status_code}")
                
                if book_request_post.status_code == 302:
                    print("✅ Book request successful")
                else:
                    print(f"❌ Book request failed: {book_request_post.status_code}")
                    if hasattr(book_request_post, 'content'):
                        print(f"Response content: {book_request_post.content[:500]}")
            else:
                print(f"❌ Book request form failed to load: {book_request_response.status_code}")
        else:
            print("❌ No available books for testing")
            
    else:
        print(f"❌ Login failed: {login_response.status_code}")

def check_javascript_console_errors():
    """Check for common JavaScript issues"""
    print("\nChecking JavaScript files...")
    
    js_files = [
        'static/js/library.js',
        'staticfiles/js/library.js'
    ]
    
    for js_file in js_files:
        if os.path.exists(js_file):
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for common issues
            issues = []
            
            if 'console.log' in content:
                issues.append("Contains console.log statements")
            
            if 'addEventListener' not in content:
                issues.append("Missing event listeners")
            
            if 'preventDefault' not in content:
                issues.append("Missing preventDefault calls")
            
            print(f"JavaScript file: {js_file}")
            if issues:
                for issue in issues:
                    print(f"  ⚠️ {issue}")
            else:
                print("  ✅ No obvious issues found")
        else:
            print(f"❌ JavaScript file not found: {js_file}")

def check_form_templates():
    """Check form templates for common issues"""
    print("\nChecking form templates...")
    
    templates = [
        'templates/library/loan_form.html',
        'templates/library/request_book.html'
    ]
    
    for template in templates:
        if os.path.exists(template):
            with open(template, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues = []
            
            if 'csrf_token' not in content:
                issues.append("Missing CSRF token")
            
            if 'method="post"' not in content.lower():
                issues.append("Missing POST method")
            
            if 'type="submit"' not in content:
                issues.append("Missing submit button")
            
            print(f"Template: {template}")
            if issues:
                for issue in issues:
                    print(f"  ❌ {issue}")
            else:
                print("  ✅ No obvious issues found")
        else:
            print(f"❌ Template not found: {template}")

def main():
    """Run all debug tests"""
    print("🔍 Debugging Form Submission Issues")
    print("=" * 50)
    
    test_form_submissions()
    check_javascript_console_errors()
    check_form_templates()
    
    print("\n" + "=" * 50)
    print("✅ Debug tests completed!")

if __name__ == '__main__':
    main()
