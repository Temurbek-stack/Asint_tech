#!/usr/bin/env python
import os
import sys
import django
import requests

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeeval_project.settings')
django.setup()

from rest_framework.authtoken.models import Token
from asset_manager.models import User

def test_token_validity():
    """Test if the authentication token is valid"""
    print("=== Testing Authentication Token ===")
    
    # The token from the frontend console
    # test_token = "8d65449b7c0d63bde890398e3f109b4186f1af1f"  # REMOVED for security
    print(f"Testing token: {test_token}")
    
    try:
        # Try to find the token in the database
        token_obj = Token.objects.get(key=test_token)
        print(f"✓ Token found in database")
        print(f"✓ Token belongs to user: {token_obj.user.username}")
        print(f"✓ User email: {token_obj.user.email}")
        print(f"✓ User is active: {token_obj.user.is_active}")
        print(f"✓ Token created: {token_obj.created}")
        
        return True
        
    except Token.DoesNotExist:
        print("✗ Token not found in database")
        return False
    except Exception as e:
        print(f"✗ Error checking token: {e}")
        return False

def test_api_call():
    """Test making an API call with the token"""
    print("\n=== Testing API Call ===")
    
    # test_token = "8d65449b7c0d63bde890398e3f109b4186f1af1f"  # REMOVED for security
    
    headers = {
        'Authorization': f'Token {test_token}',
        'Content-Type': 'application/json'
    }
    
    # Test a simple authenticated endpoint first
    try:
        response = requests.get('http://localhost:8000/api/auth/profile/', headers=headers)
        print(f"Profile endpoint status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Authentication working! User: {data.get('username')}")
            return True
        else:
            print(f"✗ Profile endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error calling API: {e}")
        return False

def test_marketplace_endpoint():
    """Test the marketplace create endpoint specifically"""
    print("\n=== Testing Marketplace Endpoint ===")
    
    # test_token = "8d65449b7c0d63bde890398e3f109b4186f1af1f"  # REMOVED for security
    
    headers = {
        'Authorization': f'Token {test_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'asset_id': 1,
        'listing_price': '66781.00',
        'description': 'Test listing'
    }
    
    try:
        response = requests.post('http://localhost:8000/api/marketplace/create/', 
                               headers=headers, 
                               json=payload)
        print(f"Marketplace create status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 201:
            print("✓ Marketplace endpoint working!")
            return True
        else:
            print(f"✗ Marketplace endpoint failed")
            return False
            
    except Exception as e:
        print(f"✗ Error calling marketplace API: {e}")
        return False

if __name__ == "__main__":
    print("Testing authentication and marketplace functionality...\n")
    
    token_valid = test_token_validity()
    if token_valid:
        api_working = test_api_call()
        if api_working:
            test_marketplace_endpoint()
    
    print("\n=== Test Complete ===") 