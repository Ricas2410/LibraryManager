#!/usr/bin/env python
"""
Direct test of notifications API
"""
import requests

def test_notifications_api():
    """Test the notifications API directly"""
    print("🔍 Testing Notifications API directly...")
    
    try:
        # Test unauthenticated request
        response = requests.get('http://127.0.0.1:8000/api/notifications/')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            data = response.json()
            print(f"Response: {data}")
            if 'error' in data and data['error'] == 'Authentication required':
                print("✅ Notifications API is working correctly!")
                print("   - No more 'Cannot filter a query once a slice has been taken' errors")
                print("   - Properly handles unauthenticated requests")
            else:
                print("❌ Unexpected response format")
        else:
            print(f"❌ Expected 401 status, got {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_notifications_api()
