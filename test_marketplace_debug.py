#!/usr/bin/env python
import os
import sys
import django
import requests

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeeval_project.settings')
django.setup()

from rest_framework.authtoken.models import Token
from asset_manager.models import User, Asset

def test_marketplace_authentication():
    """Test marketplace endpoint with actual tokens from database"""
    print("=== Testing Marketplace Authentication ===")
    
    # Get all tokens from database
    tokens = Token.objects.all()
    print(f"Found {tokens.count()} tokens in database:")
    
    for token in tokens:
        # Test this token with marketplace endpoint
        headers = {
            'Authorization': f'Token {token.key}',
            'Content-Type': 'application/json'
        }
        
        # First test profile endpoint
        try:
            response = requests.get('http://localhost:8000/api/auth/profile/', headers=headers)
            print(f"  Profile endpoint: {response.status_code}")
            
            if response.status_code == 200:
                profile_data = response.json()
                print(f"    ✓ Profile working: {profile_data.get('username')}")
                
                # Check if user has any assets
                user_assets = Asset.objects.filter(portfolio__user=token.user)
                print(f"    User has {user_assets.count()} assets")
                
                if user_assets.exists():
                    # Test marketplace endpoint with first asset
                    first_asset = user_assets.first()
                    marketplace_data = {
                        'asset_id': first_asset.id,
                        'listing_price': str(first_asset.current_value),
                        'description': f'Test listing for {first_asset.name}'
                    }
                    
                    marketplace_response = requests.post(
                        'http://localhost:8000/api/marketplace/create/',
                        headers=headers,
                        json=marketplace_data
                    )
                    
                    print(f"    Marketplace endpoint: {marketplace_response.status_code}")
                    print(f"    Response: {marketplace_response.text}")
                    
                    if marketplace_response.status_code == 201:
                        print("    ✓ Marketplace working!")
                    else:
                        print("    ✗ Marketplace failed")
                        
                else:
                    print("    No assets found for this user")
                    
            else:
                print(f"    ✗ Profile failed: {response.text}")
                
        except Exception as e:
            print(f"    ✗ Error testing token: {e}")
        
        print()  # Empty line for readability

if __name__ == "__main__":
    test_marketplace_authentication() 