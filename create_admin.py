#!/usr/bin/env python
"""
Simple script to create admin user for production
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from django.contrib.auth.models import User

def main():
    print("🔧 Checking/creating admin user...")
    
    # Check if any superuser exists
    superusers = User.objects.filter(is_superuser=True)
    print(f"Found {superusers.count()} existing superusers")
    
    if superusers.exists():
        for user in superusers:
            print(f"  - {user.username} (email: {user.email})")
        
        # Update password for existing admin user
        admin_user = User.objects.filter(username='admin').first()
        if admin_user:
            admin_user.set_password('WRaven2024!')
            admin_user.save()
            print("✓ Updated password for existing admin user")
        else:
            print("ℹ No 'admin' user found, will create new one")
    
    if not User.objects.filter(username='admin').exists():
        print("Creating new admin user...")
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@whiteravenpourhouse.com',
            password='WRaven2024!',
            first_name='Admin',
            last_name='User'
        )
        print(f"✅ Created superuser: {admin_user.username}")
    else:
        print("✅ Admin user already exists")
    
    # Verify the user can authenticate
    admin_user = User.objects.get(username='admin')
    print(f"\nUser details:")
    print(f"  Username: {admin_user.username}")
    print(f"  Email: {admin_user.email}")
    print(f"  Is superuser: {admin_user.is_superuser}")
    print(f"  Is staff: {admin_user.is_staff}")
    print(f"  Is active: {admin_user.is_active}")
    
    # Test password
    from django.contrib.auth import authenticate
    test_auth = authenticate(username='admin', password='WRaven2024!')
    if test_auth:
        print("✅ Password authentication works")
    else:
        print("❌ Password authentication failed")
        # Reset password  
        admin_user.set_password('WRaven2024!')
        admin_user.save()
        print("✅ Password reset and saved")

if __name__ == '__main__':
    main()