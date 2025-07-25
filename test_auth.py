#!/usr/bin/env python
import requests
import json

# Test if authentication is working
API_BASE_URL = 'http://localhost:8000/api'

# First, try to login to get a token
login_data = {
    'email': 'test@example.com',  # Replace with actual test user email
    'password': 'testpass123'     # Replace with actual test user password
}

try:
    print("Testing authentication...")
    
    # Try to login
    response = requests.post(f"{API_BASE_URL}/auth/login/", json=login_data)
    print(f"Login response status: {response.status_code}")
    
    if response.status_code == 200:
        login_result = response.json()
        token = login_result.get('token')
        print(f"Login successful, token: {token[:20]}...")
        
        # Test authenticated endpoints
        headers = {'Authorization': f'Token {token}'}
        
        # Test dashboard endpoint
        dashboard_response = requests.get(f"{API_BASE_URL}/dashboard/", headers=headers)
        print(f"Dashboard endpoint status: {dashboard_response.status_code}")
        
        # Test assets endpoint
        assets_response = requests.get(f"{API_BASE_URL}/assets/", headers=headers)
        print(f"Assets endpoint status: {assets_response.status_code}")
        
        # Test marketplace create endpoint (the failing one)
        marketplace_data = {
            'asset_id': 1,  # Replace with actual asset ID
            'listing_price': 100000,
            'description': 'Test listing'
        }
        
        marketplace_response = requests.post(f"{API_BASE_URL}/marketplace/create/", 
                                           json=marketplace_data, headers=headers)
        print(f"Marketplace create status: {marketplace_response.status_code}")
        print(f"Marketplace create response: {marketplace_response.text}")
        
    else:
        print(f"Login failed: {response.text}")
        
except Exception as e:
    print(f"Error testing authentication: {e}") 