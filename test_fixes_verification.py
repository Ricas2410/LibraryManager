#!/usr/bin/env python
"""
Test script to verify the fixes are working properly
"""
import os
import sys
import django
import requests
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management.settings')
django.setup()

from library.models import Book, Author, Category, Publisher, Loan, Notification

def test_notifications_api():
    """Test the notifications API fix"""
    print("🔍 Testing Notifications API...")
    
    try:
        # Test unauthenticated request
        response = requests.get('http://127.0.0.1:8000/api/notifications/')
        print(f"Unauthenticated request status: {response.status_code}")
        
        if response.status_code == 401:
            data = response.json()
            if 'error' in data and data['error'] == 'Authentication required':
                print("✅ Notifications API correctly handles unauthenticated requests")
            else:
                print("❌ Unexpected response format for unauthenticated request")
        else:
            print(f"❌ Expected 401 status, got {response.status_code}")
            
        # Test with authenticated user using Django test client
        client = Client()
        User = get_user_model()
        
        # Try to get or create a test user
        try:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.create_superuser('testadmin', 'test@example.com', 'testpass123')
            
            # Login
            client.force_login(user)
            
            # Test authenticated request
            response = client.get('/api/notifications/')
            print(f"Authenticated request status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'notifications' in data and 'unread_count' in data:
                    print("✅ Notifications API working correctly for authenticated users")
                    print(f"   - Notifications count: {len(data['notifications'])}")
                    print(f"   - Unread count: {data['unread_count']}")
                else:
                    print("❌ Missing expected fields in response")
            else:
                print(f"❌ Expected 200 status for authenticated request, got {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing authenticated request: {e}")
            
    except Exception as e:
        print(f"❌ Error testing notifications API: {e}")

def test_author_model():
    """Test the Author model with death_date field"""
    print("\n🔍 Testing Author Model...")
    
    try:
        # Try to create an author with death_date
        author = Author.objects.create(
            first_name="Test",
            last_name="Author",
            birth_date="1900-01-01",
            death_date="1980-12-31",
            nationality="Test Country"
        )
        print("✅ Author model with death_date field working correctly")
        print(f"   - Created author: {author.get_full_name()}")
        print(f"   - Birth date: {author.birth_date}")
        print(f"   - Death date: {author.death_date}")
        
        # Clean up
        author.delete()
        
    except Exception as e:
        print(f"❌ Error testing Author model: {e}")

def test_author_form():
    """Test the Author form"""
    print("\n🔍 Testing Author Form...")
    
    try:
        client = Client()
        User = get_user_model()
        
        # Get admin user
        user = User.objects.filter(is_superuser=True).first()
        if user:
            client.force_login(user)
            
            # Test GET request to author add page
            response = client.get('/authors/add/')
            print(f"Author add page status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Author add page loads successfully")
                
                # Test POST request to create author
                post_data = {
                    'first_name': 'Test',
                    'last_name': 'Author',
                    'birth_date': '1900-01-01',
                    'death_date': '1980-12-31',
                    'nationality': 'Test Country',
                    'biography': 'Test biography'
                }
                
                response = client.post('/authors/add/', post_data)
                print(f"Author creation POST status: {response.status_code}")
                
                if response.status_code == 302:  # Redirect after successful creation
                    print("✅ Author creation successful")
                    
                    # Clean up - find and delete the created author
                    test_author = Author.objects.filter(first_name='Test', last_name='Author').first()
                    if test_author:
                        test_author.delete()
                        print("   - Test author cleaned up")
                else:
                    print(f"❌ Author creation failed: {response.status_code}")
                    if hasattr(response, 'content'):
                        print(f"Response content: {response.content[:500]}")
            else:
                print(f"❌ Author add page failed to load: {response.status_code}")
        else:
            print("❌ No admin user found for testing")
            
    except Exception as e:
        print(f"❌ Error testing Author form: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting fixes verification tests...\n")
    
    test_notifications_api()
    test_author_model()
    test_author_form()
    
    print("\n✅ All tests completed!")

if __name__ == '__main__':
    main()
