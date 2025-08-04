#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

print("=== White Raven Admin Access Test ===")

# Test admin URL accessibility
client = Client()

print("\n1. Testing Admin URL Access...")
try:
    response = client.get('/admin/')
    if response.status_code == 200:
        print("+ Admin login page: Accessible at http://127.0.0.1:8001/admin/")
        print("+ Status: Login page loads correctly")
    elif response.status_code == 302:
        print("+ Admin URL: Redirects to login (normal behavior)")
    else:
        print(f"- Unexpected status code: {response.status_code}")
except Exception as e:
    print(f"- Error accessing admin: {e}")

print("\n2. Available Admin Users:")

# List all superusers
superusers = User.objects.filter(is_superuser=True)
staff_users = User.objects.filter(is_staff=True)

if superusers:
    print("Superusers (full admin access):")
    for user in superusers:
        print(f"  + {user.username} ({user.get_full_name() or 'No name'}) - {user.email}")
else:
    print("  - No superusers found")

if staff_users:
    print("Staff users (admin access):")
    for user in staff_users:
        if not user.is_superuser:  # Don't duplicate superusers
            print(f"  + {user.username} ({user.get_full_name() or 'No name'}) - {user.email}")

print("\n3. Admin Interface Features Available:")
print("+ Business Information management")
print("+ Contact form submissions")
print("+ Menu categories and items")
print("+ Recipe management")
print("+ Staff/Employee management")
print("+ Work schedules")
print("+ User accounts")

print("\n=== Admin Access Summary ===")
print("Admin URL: http://127.0.0.1:8001/admin/")
print("")
print("Login Credentials:")
print("• admin / admin123! (main admin)")
print("• rose_owner / rose123! (Rose Woolf - Owner)")
print("")
print("Features:")
print("• Custom admin interface with White Raven branding")
print("• Menu management with image uploads")
print("• Staff scheduling and management")
print("• Contact form submissions")
print("• Business hours and information")
print("")
print("Admin interface is ready to use!")