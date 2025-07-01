#!/usr/bin/env python
"""
Test script to test forms with authenticated user
"""

import os
import sys
import django
import requests
from requests.sessions import Session

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management.settings')
django.setup()

from library.models import User, Book

def test_authenticated_forms():
    """Test forms with authenticated session"""
    print("Testing Forms with Authentication...")
    
    # Create a session
    session = Session()
    
    # First, get the login page to get CSRF token
    login_page = session.get('http://127.0.0.1:8000/login/')
    print(f"Login page status: {login_page.status_code}")
    
    if login_page.status_code == 200:
        # Extract CSRF token
        import re
        csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_page.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"CSRF token found: {csrf_token[:20]}...")
            
            # Login
            login_data = {
                'username': 'admin',
                'password': 'admin123',
                'csrfmiddlewaretoken': csrf_token
            }
            
            login_response = session.post('http://127.0.0.1:8000/login/', data=login_data)
            print(f"Login response status: {login_response.status_code}")
            
            if login_response.status_code == 302:  # Redirect after successful login
                print("✅ Login successful")
                
                # Test notifications API with authenticated session
                notifications_response = session.get('http://127.0.0.1:8000/api/notifications/')
                print(f"Notifications API status: {notifications_response.status_code}")
                
                if notifications_response.status_code == 200:
                    print("✅ Notifications API working with authentication")
                    try:
                        notifications_data = notifications_response.json()
                        print(f"Notifications count: {len(notifications_data.get('notifications', []))}")
                    except:
                        print("❌ Invalid JSON response from notifications API")
                else:
                    print(f"❌ Notifications API failed: {notifications_response.status_code}")
                
                # Test loan creation form
                print("\nTesting loan creation form...")
                loan_form_response = session.get('http://127.0.0.1:8000/loans/create/')
                print(f"Loan form GET status: {loan_form_response.status_code}")
                
                if loan_form_response.status_code == 200:
                    print("✅ Loan form loads successfully")
                    
                    # Extract CSRF token from loan form
                    csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', loan_form_response.text)
                    if csrf_match:
                        csrf_token = csrf_match.group(1)
                        
                        # Get available books and users
                        books = Book.objects.filter(available_copies__gt=0)[:1]
                        users = User.objects.filter(role__in=['student', 'teacher'])[:1]
                        
                        if books and users:
                            book = books[0]
                            user = users[0]
                            
                            print(f"Testing loan creation with book: {book.title} and user: {user.username}")
                            
                            # Test POST to loan creation
                            loan_post_data = {
                                'book': str(book.id),
                                'borrower': str(user.id),
                                'due_date': '2025-07-01T12:00',
                                'notes': 'Test loan from script',
                                'csrfmiddlewaretoken': csrf_token
                            }
                            
                            loan_post_response = session.post('http://127.0.0.1:8000/loans/create/', data=loan_post_data)
                            print(f"Loan creation POST status: {loan_post_response.status_code}")
                            
                            if loan_post_response.status_code == 302:
                                print("✅ Loan creation successful")
                            else:
                                print(f"❌ Loan creation failed: {loan_post_response.status_code}")
                                print(f"Response content: {loan_post_response.text[:500]}")
                        else:
                            print("❌ No books or users available for testing")
                    else:
                        print("❌ Could not find CSRF token in loan form")
                else:
                    print(f"❌ Loan form failed to load: {loan_form_response.status_code}")
                
                # Test book request form
                print("\nTesting book request form...")
                books = Book.objects.filter(available_copies__gt=0)[:1]
                
                if books:
                    book = books[0]
                    book_request_url = f'http://127.0.0.1:8000/request-book/{book.id}/'
                    
                    book_request_response = session.get(book_request_url)
                    print(f"Book request form GET status: {book_request_response.status_code}")
                    
                    if book_request_response.status_code == 200:
                        print("✅ Book request form loads successfully")
                        
                        # Extract CSRF token from book request form
                        csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', book_request_response.text)
                        if csrf_match:
                            csrf_token = csrf_match.group(1)
                            
                            # Test POST to book request
                            book_request_data = {
                                'csrfmiddlewaretoken': csrf_token
                            }
                            
                            book_request_post = session.post(book_request_url, data=book_request_data)
                            print(f"Book request POST status: {book_request_post.status_code}")
                            
                            if book_request_post.status_code == 302:
                                print("✅ Book request successful")
                            else:
                                print(f"❌ Book request failed: {book_request_post.status_code}")
                                print(f"Response content: {book_request_post.text[:500]}")
                        else:
                            print("❌ Could not find CSRF token in book request form")
                    else:
                        print(f"❌ Book request form failed to load: {book_request_response.status_code}")
                else:
                    print("❌ No available books for testing")
                    
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"Response content: {login_response.text[:500]}")
        else:
            print("❌ Could not find CSRF token in login form")
    else:
        print(f"❌ Could not load login page: {login_page.status_code}")

def main():
    """Run all tests"""
    print("🔍 Testing Forms with Authentication")
    print("=" * 50)
    
    test_authenticated_forms()
    
    print("\n" + "=" * 50)
    print("✅ Authentication tests completed!")

if __name__ == '__main__':
    main()
