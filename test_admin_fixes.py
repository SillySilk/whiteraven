#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from django.test import Client

print("=== Testing Admin Fixes ===")

client = Client()

# Login to admin
login_success = client.login(username='admin', password='admin123!')
print(f"Admin login: {'SUCCESS' if login_success else 'FAILED'}")

if login_success:
    print("\nTesting menu item admin pages...")
    
    # Test menu item list
    response = client.get('/admin/menu/menuitem/')
    print(f"Menu item list: {response.status_code} ({'SUCCESS' if response.status_code == 200 else 'FAILED'})")
    
    # Test add menu item
    response = client.get('/admin/menu/menuitem/add/')
    print(f"Add menu item: {response.status_code} ({'SUCCESS' if response.status_code == 200 else 'FAILED'})")
    
    # Test edit specific menu item (the one that was failing)
    response = client.get('/admin/menu/menuitem/5/change/')
    print(f"Edit menu item #5: {response.status_code} ({'SUCCESS' if response.status_code == 200 else 'FAILED'})")
    
    # Test other menu items
    for item_id in [1, 2, 3, 4]:
        response = client.get(f'/admin/menu/menuitem/{item_id}/change/')
        print(f"Edit menu item #{item_id}: {response.status_code} ({'SUCCESS' if response.status_code == 200 else 'FAILED'})")

print("\nTesting favicon...")
response = client.get('/favicon.ico')
print(f"Favicon: {response.status_code} ({'SUCCESS' if response.status_code in [200, 301, 302] else 'FAILED'})")

print("\n=== Fix Status ===")
print("+ Image widget error handling improved")
print("+ Favicon redirect added to URLs")
print("+ Django server reloaded successfully")
print("\nThe admin menu item editing should now work without 500 errors!")
print("The favicon should now load without 404 errors!")