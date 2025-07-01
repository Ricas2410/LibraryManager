#!/usr/bin/env python
"""
Test form submission directly
"""
import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management.settings')
django.setup()

from library.models import Book, Author, Category, Publisher, Loan

def test_book_request_submission():
    """Test book request form submission"""
    print("🔍 Testing book request form submission...")
    
    try:
        client = Client()
        User = get_user_model()
        
        # Get or create a test user
        user = User.objects.filter(role='student').first()
        if not user:
            user = User.objects.create_user(
                username='teststudent',
                email='student@test.com',
                password='testpass123',
                role='student',
                first_name='Test',
                last_name='Student'
            )
        
        # Get a book to request
        book = Book.objects.filter(available_copies__gt=0).first()
        if not book:
            print("❌ No available books found for testing")
            return
            
        print(f"📚 Testing with book: {book.title}")
        print(f"👤 Testing with user: {user.username}")
        
        # Login the user
        client.force_login(user)
        
        # Test GET request to the request page
        get_response = client.get(f'/request-book/{book.id}/')
        print(f"GET request status: {get_response.status_code}")
        
        if get_response.status_code == 200:
            print("✅ Request book page loads successfully")
            
            # Test POST request to submit the form
            post_response = client.post(f'/request-book/{book.id}/', {})
            print(f"POST request status: {post_response.status_code}")
            
            if post_response.status_code == 302:  # Redirect after successful submission
                print("✅ Book request form submission successful!")
                print(f"   - Redirected to: {post_response.url}")
                
                # Check if a loan was created
                loan = Loan.objects.filter(book=book, borrower=user, status='pending').first()
                if loan:
                    print(f"✅ Loan request created successfully!")
                    print(f"   - Loan ID: {loan.id}")
                    print(f"   - Status: {loan.status}")
                    print(f"   - Due date: {loan.due_date}")
                    
                    # Clean up
                    loan.delete()
                    print("   - Test loan cleaned up")
                else:
                    print("❌ No loan request found in database")
            else:
                print(f"❌ Form submission failed: {post_response.status_code}")
                if hasattr(post_response, 'content'):
                    print(f"Response content: {post_response.content[:500]}")
        else:
            print(f"❌ Request book page failed to load: {get_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing book request: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    print("🚀 Starting form submission tests...\n")
    
    test_book_request_submission()
    
    print("\n✅ All tests completed!")

if __name__ == '__main__':
    main()
